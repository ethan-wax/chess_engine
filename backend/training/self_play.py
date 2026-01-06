from tqdm import tqdm
from typing import Union
from pathlib import Path
import sys

# Add parent directory to path to allow imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

import chess
from training.encoder import encode_board, encode_move
from reinforcement import ReinforcementAgent
import numpy as np
from torch.nn import CrossEntropyLoss, MSELoss
from torch.optim import Adam
from torch.utils.data import DataLoader, TensorDataset
from training.simple_model import SimpleModel
import torch

GAMES_PER_CYCLE = 100
EVAL_GAMES = 10
NUM_EPOCHS = 20  # Reduced from 100 - can train multiple cycles
BATCH_SIZE = 64  # Batch size for training
LEARNING_RATE = 0.001
MCTS_ROUNDS_SELF_PLAY = 100  # Higher rounds for quality self-play moves

device = "mps" if torch.backends.mps.is_available() else "cpu"

def simulate_game(
    agent1: ReinforcementAgent, 
    agent2: ReinforcementAgent, 
    save: bool = True
) -> Union[int, tuple[np.ndarray, np.ndarray]]:
    board = chess.Board()
    board_encs = []
    move_encs = []
    player = agent1

    while not board.is_game_over():
        # Capture the player's color BEFORE the move
        player_color = board.turn
        move = player.select_move(board)
        
        if save:
            board_enc = encode_board(board)
            board_encs.append(board_enc)
            move = board.push_san(move)
            move_enc = encode_move(move)
            # Save the color of the player who made the move
            move_encs.append((move_enc, player_color))
        else:
            board.push_san(move)

        if player == agent1:
            player = agent2
        else:
            player = agent1

    winner = board.outcome().winner
    if winner is None:
        tqdm.write("Game Drawn")
        if not save:
            return 0
        move_encs = [(move_enc, 0) for (move_enc, _) in move_encs]
        return board_encs, move_encs
    
    tqdm.write(f"Game Winner: {"White" if winner else "Black"}")
    if not save:
        return 1 if winner else -1
    # Assign value from perspective of player who made the move
    # +1 if that player won, -1 if they lost
    move_encs = [(move_enc, 1.0 if bool(turn) == winner else -1.0) for (move_enc, turn) in move_encs]
    return board_encs, move_encs

def train_model():
    model = SimpleModel().to(device)
    model_path = Path("training/reinforcement_model.pt")
    state_dict = torch.load(model_path)
    model.load_state_dict(state_dict)
    optimizer = Adam(model.parameters(), lr=LEARNING_RATE)
    ce_loss = CrossEntropyLoss()
    mse_loss = MSELoss(reduction='mean')

    episodes_path = Path("training/self_play_episodes.npz")
    with np.load(episodes_path) as data:
        X, y = data["X"], data["y"]
        X = X.astype(np.float32)
        y = y.astype(np.float32)

    # Create DataLoader for batch processing
    X_tensor = torch.from_numpy(X)
    y_tensor = torch.from_numpy(y)
    moves = y_tensor[:, 0].long()  # Extract move column and convert to long
    values = y_tensor[:, 1].float().unsqueeze(1)  # Extract value column
    
    dataset = TensorDataset(X_tensor, values, moves)
    train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model.train()
    for epoch in range(NUM_EPOCHS):
        epoch_loss = 0
        for X_batch, values_batch, moves_batch in train_loader:
            X_batch = X_batch.to(device)
            values_batch = values_batch.to(device)
            moves_batch = moves_batch.to(device)
            
            pred_values, pred_moves = model(X_batch)
            policy_loss = ce_loss(pred_moves, moves_batch)
            value_loss = mse_loss(pred_values, values_batch)
            total_loss = policy_loss + value_loss

            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
            
            epoch_loss += total_loss.item()
        
        if (epoch + 1) % 5 == 0:
            tqdm.write(f"Epoch {epoch + 1}/{NUM_EPOCHS}, Loss: {epoch_loss / len(train_loader):.4f}")

    model_path = Path("training/reinforcement_model.pt")
    torch.save(model.state_dict(), model_path)

def self_play():
    # Use higher MCTS rounds for quality moves in self-play
    agent = ReinforcementAgent(MCTS_ROUNDS_SELF_PLAY)
    X, y = [], []
    non_drawn = 0
    tqdm.write("Start Self Play")
    for i in tqdm(range(GAMES_PER_CYCLE)):
        board_encs, move_encs = simulate_game(agent, agent)
        # Check if any move has non-zero value (not a draw)
        if len(move_encs) > 0 and any(val != 0 for _, val in move_encs):
            non_drawn += 1
        X.extend(board_encs)
        y.extend(move_encs)

    X_data = np.array(X, dtype=np.float32)
    y_data = np.array(y, dtype=np.float32)

    tqdm.write(f"Games with a winner: {non_drawn}")
    episodes_path = Path("training/self_play_episodes.npz")
    np.savez_compressed(
        episodes_path,
        X=X_data,
        y=y_data,
    )

    tqdm.write("Start Training")
    train_model()

    agent1 = ReinforcementAgent()
    agent2 = ReinforcementAgent(old=True)
    white = True
    score = 0
    tqdm.write("Start Eval")
    for _ in range(EVAL_GAMES):
        if white:
            winner = simulate_game(agent1, agent2, save=False)
            score += (winner + 1.0) / 2.0
        else:
            winner = simulate_game(agent2, agent1, save=False)
            score += (winner - 1.0) / 2.0
        white = not white

    tqdm.write(f'New model score: {score} / {EVAL_GAMES}, {score / EVAL_GAMES * 100:.2f}%')

self_play()