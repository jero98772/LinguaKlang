from dataclasses import dataclass


@dataclass
class AudioCommand:
    topic: str
    native: str
    target: str
    repeat: int
