from operator import mod
from random import shuffle
from game_dataset import GameDataset
import numpy as np
import chess
import torch
from sklearn.model_selection import train_test_split
from simple_model import SimpleModel
from torch.utils.data import DataLoader

device = 'mps' if torch.backends.mps.is_available() else 'cpu'
BATCH_SIZE = 64

with np.load('lichess_data.npz') as data:
    X, y = data['X'], data['y']
    X = X.astype(np.float32)
    y = y.astype(np.float32)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
train_data = GameDataset(X_train, y_train)
train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)

model = SimpleModel().to(device)

for X_batch, y_batch in train_loader:
    data = X_batch.to(device)
    print(model(data))
    break