import torch
from torch.utils.data import Dataset
import numpy as np

class GameDataset(Dataset):
    def __init__(self, data: np.array, labels: np.array) -> None:
        self.data = data
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx) -> tuple[np.array, np.float32]:
        data = torch.from_numpy(self.data[idx])
        label = self.labels[idx]
        return data, label