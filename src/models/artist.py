from dataclasses import dataclass

@dataclass
class Artist:
    name: str
    channel_id: str
    subscribers: int
    category: str
    is_official: bool
