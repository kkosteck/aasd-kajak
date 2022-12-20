import json
from dataclasses import dataclass
from typing import List, Optional


class Direction:
    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'
    NONE = 'NONE'

    @staticmethod
    def as_list() -> List[str]:
        return [Direction.N, Direction.S, Direction.E, Direction.W]

    @staticmethod
    def reverse(direction: str) -> str:
        if direction == Direction.N:
            return Direction.S
        if direction == Direction.S:
            return Direction.N
        if direction == Direction.E:
            return Direction.W
        if direction == Direction.W:
            return Direction.E
        return Direction.NONE


@dataclass
class Car:
    id: int
    starting_crossroad_id: int
    starting_queue_direction: str
    create_timestamp: float
    path: List[str]
    dispatch_timestamp: Optional[float] = None

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "starting_crossroad_id": self.starting_crossroad_id,
            "starting_queue_direction": self.starting_queue_direction,
            "create_timestamp": self.create_timestamp,
            "dispatch_timestamp": self.dispatch_timestamp,
            "path": self.path,
        })

    @classmethod
    def from_json(cls, json_str) -> 'Car':
        return cls(**json.loads(json_str))

    def __repr__(self):
        return f"({self.id}, {self.path})"
