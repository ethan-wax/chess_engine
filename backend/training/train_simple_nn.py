from tqdm import tqdm
from game_dataset import GameDataset
import numpy as np
import chess
import torch
from sklearn.model_selection import train_test_split
from simple_model import SimpleModel
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss
import gc

device = 'mps' if torch.backends.mps.is_available() else 'cpu'
BATCH_SIZE = 64
MODEL_PATH = 'simple_nn_model.pt'
NUM_EPOCHS = 100

with np.load('lichess_data.npz') as data:
    X, y = data['X'], data['y']
    X = X.astype(np.float32)
    y = y.astype(np.float32)

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_valid, y_train, y_valid = train_test_split(X_temp, y_temp, test_size=.25, random_state=42)
train_data = GameDataset(X_train, y_train)
train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
valid_data = GameDataset(X_valid, y_valid)
valid_loader = DataLoader(valid_data, batch_size=BATCH_SIZE)
test_data = GameDataset(X_test, y_test)
test_loader = DataLoader(test_data, batch_size=BATCH_SIZE)

model = SimpleModel().to(device)
optimizer = Adam(model.parameters())
loss_fn = CrossEntropyLoss()
best_valid_loss = float('inf')

for epoch in tqdm(range(NUM_EPOCHS)):
    epoch_loss = 0
    model.train()

    for i, (X_batch, y_batch) in enumerate(train_loader):
        data = X_batch.to(device)
        labels = y_batch.to(device)
        outputs = model(data)
        loss = loss_fn(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_loss += loss

    gc.collect()
    
    if epoch % 10 == 0:
        print(f"Epoch {epoch} complete: {epoch_loss}")

    with torch.no_grad():
        model.eval()
        valid_loss = 0
        for X_vbatch, y_vbatch in valid_loader:
            data = X_vbatch.to(device)
            labels = y_vbatch.to(device)
            outputs = model(data)
            loss = loss_fn(outputs, labels)
            valid_loss += loss
        
        gc.collect()
        
        if valid_loss > best_valid_loss:
            break
        else:
            best_valid_loss = valid_loss

print("Model Training Complete")
model.eval()
moves = 0
correct = 0
for X_tbatch, y_tbatch in test_loader:
    data = X_tbatch.to(device)
    labels = y_tbatch.to(device)
    outputs = model(data)
    predicted = torch.argmax(outputs, dim=1)
    moves += len(predicted)
    correct += (predicted == labels).sum().item()

gc.collect()

print(f"Model Accuracy: {correct / moves * 100:2f}")
torch.save(model.state_dict(), MODEL_PATH)