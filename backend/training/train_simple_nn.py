import gc

import numpy as np
import torch
from game_dataset import GameDataset
from simple_model import SimpleModel
from sklearn.model_selection import train_test_split
from torch.nn import CrossEntropyLoss, MSELoss
from torch.optim import Adam
from torch.utils.data import DataLoader
from tqdm import tqdm

device = "mps" if torch.backends.mps.is_available() else "cpu"
BATCH_SIZE = 64
MODEL_PATH = "simple_nn_model.pt"
NUM_EPOCHS = 100

with np.load("lichess_data.npz") as data:
    X, y = data["X"], data["y"]
    X = X.astype(np.float32)
    y = y.astype(np.float32)

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_valid, y_train, y_valid = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42
)
train_data = GameDataset(X_train, y_train)
train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
valid_data = GameDataset(X_valid, y_valid)
valid_loader = DataLoader(valid_data, batch_size=BATCH_SIZE)
test_data = GameDataset(X_test, y_test)
test_loader = DataLoader(test_data, batch_size=BATCH_SIZE)

model = SimpleModel().to(device)
optimizer = Adam(model.parameters())
ce_loss = CrossEntropyLoss()
mse_loss = MSELoss()
best_valid_loss = float("inf")



for epoch in tqdm(range(NUM_EPOCHS)):
    epoch_loss = 0
    model.train()

    for i, (data_batch, value_batch, move_batch) in enumerate(train_loader):
        data = data_batch.float().to(device)
        values = value_batch.float().to(device).unsqueeze(1)
        moves = move_batch.float().to(device)
        pred_values, pred_moves = model(data)

        policy_loss = ce_loss(pred_moves, moves)
        value_loss = mse_loss(pred_values, values)
        total_loss = policy_loss + value_loss

        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        epoch_loss += total_loss

    gc.collect()

    if epoch % 10 == 0:
        print(f"Epoch {epoch} complete: {epoch_loss}")

    with torch.no_grad():
        model.eval()
        valid_loss = 0

        for data_batch, value_batch, move_batch in valid_loader:
            data = data_batch.to(device)
            values = value_batch.float().to(device).unsqueeze(1)
            moves = move_batch.float().to(device)
            pred_values, pred_moves = model(data)

            policy_loss = ce_loss(pred_moves, moves)
            value_loss = mse_loss(pred_values, values)
            valid_loss += policy_loss + value_loss


        gc.collect()

        if valid_loss > best_valid_loss:
            break
        else:
            best_valid_loss = valid_loss

print("Model Training Complete")
model.eval()
moves = 0
correct = 0

for data_batch, _, move_batch in test_loader:
    data = data_batch.float().to(device)
    moves = move_batch.float().to(device)
    _, output_moves = model(data)
    pred_move = torch.argmax(output_moves, dim=1)
    moves += len(pred_move)
    correct += (pred_move == moves).sum().item()

gc.collect()

print(f"Model Accuracy: {correct / moves * 100:2f}")
torch.save(model.state_dict(), MODEL_PATH)
