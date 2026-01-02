from tqdm import tqdm
from datetime import datetime
from typing import Union
import chess
from training.encoder import encode_board, encode_move
from reinforcement import ReinforcementAgent
import numpy as np
from torch.nn import CrossEntropyLoss, MSELoss
from torch.optim import Adam
from training.simple_model import SimpleModel
import torch
import random

GAMES_PER_CYCLE = 100
EVAL_GAMES = 3
NUM_EPOCHS = 100

device = "mps" if torch.backends.mps.is_available() else "cpu"

def simulate_game(
    agent1: ReinforcementAgent, 
    agent2: ReinforcementAgent, 
    smart_agent_1: ReinforcementAgent,
    smart_agent_2: ReinforcementAgent,
    save: bool = True
) -> Union[int, tuple[np.ndarray, np.ndarray]]:
    board = chess.Board()
    board_encs = []
    move_encs = []
    player = agent1
    smart_player = smart_agent_1

    while not board.is_game_over():
        if random.random() > 0.95:
            move = smart_player.select_move(board)
            smart = True
        else:
            move = player.select_move(board)
            smart = False

        if save and smart:
            board_enc = encode_board(board)
            board_encs.append(board_enc)
            move = board.push_san(move)
            move_enc = encode_move(move)
            move_encs.append((move_enc, board.turn))
        else:
            board.push_san(move)

        if player == agent1:
            player = agent2
            smart_player = smart_agent_2
        else:
            player = agent1
            smart_player = smart_agent_1

    winner = board.outcome().winner
    if winner is None:
        tqdm.write("Game Drawn")
        move_encs = [(move_enc, 0) for (move_enc, player) in move_encs]
        return 0 if not save else board_encs, move_encs
    
    tqdm.write(f"Game Winner: {"White" if winner else "Black"}")
    if not save:
        return 1 if winner else 0 -1
    move_encs = [(move_enc, 1 if player == winner else -1) for (move_enc, player) in move_encs]
    return board_encs, move_encs

def train_model():
    model = SimpleModel().to(device)
    state_dict = torch.load("reinforcement_model.pt")
    model.load_state_dict(state_dict)
    optimizer = Adam(model.parameters())
    ce_loss = CrossEntropyLoss()
    mse_loss = MSELoss(reduction='mean')

    with np.load("self_play_episodes.npz") as data:
        X, y = data["X"], data["y"]
        X = X.astype(np.float32)
        y = y.astype(np.float32)

    X_tensor = torch.from_numpy(X).to(device)
    y_tensor = torch.from_numpy(y).to(device)
    moves, values = y_tensor[0], y_tensor[1]
    model.train()
    for _ in range(NUM_EPOCHS):
        pred_values, pred_moves = model(X_tensor)
        policy_loss = ce_loss(pred_moves, moves)
        value_loss = mse_loss(pred_values, values)
        total_loss = policy_loss + value_loss

        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

    torch.save(model.state_dict(), "reinforcement_model.pt")

    

def self_play():
    agent = ReinforcementAgent(50)
    smart_agent = ReinforcementAgent()
    X, y = [], []
    non_drawn = 0
    tqdm.write("Start Self Play")
    for i in tqdm(range(GAMES_PER_CYCLE)):
        board_encs, move_encs = simulate_game(agent, agent, smart_agent, smart_agent)
        result = move_encs[0][0]
        if result != 0:
            non_drawn += 1
        X.extend(board_encs)
        y.extend(move_encs)

    X_data = np.array(X, dtype=np.float32)
    y_data = np.array(y, dtype=np.float32)

    tqdm.write(f"Games with a winner: {non_drawn}")
    np.savez_compressed(
        "self_play_episodes.npz",
        X=X_data,
        y=y_data,
    )

    tqdm.write("Start Training")
    train_model()

    agent1 = ReinforcementAgent()
    agent2 = ReinforcementAgent(old=True)
    white = True
    wins = 0
    tqdm.write("Start Eval")
    for _ in range(EVAL_GAMES):
        if white:
            winner = simulate_game(agent1, agent2, agent1, agent2, save=False)
        else:
            winner = simulate_game(agent2, agent1, agent2, agent1, save=False)
        wins += int(winner == white)

    tqdm.write(f'New model wins: {wins} / {EVAL_GAMES}, {wins / EVAL_GAMES}%')

self_play()