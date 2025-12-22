import torch.nn as nn
import torch


class SimpleModel(nn.Module):
    def __init__(self, channels=18, linear_units=512) -> None:
        super().__init__()
        self.linear_units = linear_units
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
        )
        self.value_head = nn.Linear(linear_units, 1)
        self.policy_head = nn.Linear(linear_units, 4096)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        x = self.model(x)
        value = torch.tanh(self.value_head(x))
        policy = self.policy_head(x)
        return value, policy
