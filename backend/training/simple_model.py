import torch.nn as nn


class SimpleModel(nn.Module):
    def __init__(self, channels=18, linear_units=512) -> None:
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(3),
            nn.Flatten(),
            nn.Linear(72, linear_units),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(linear_units, 64 * 64),
        )

    def forward(self, x):
        return self.model(x)
