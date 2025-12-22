import numpy as np
import torch
from torch.utils.data import Dataset


class GameDataset(Dataset):
    def __init__(self, data: np.array, labels: np.array) -> None:
        self.data = data
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx) -> tuple[np.array, np.float32, np.float32]:
        data = torch.from_numpy(self.data[idx])
        value = self.labels[idx][0].item()
        move = self.labels[idx][1].item()
        return data, value, move
