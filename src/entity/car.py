import json
from dataclasses import dataclass
from typing import List, Optional


class Direction:
    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'

    @staticmethod
    def as_list() -> List[str]:
        return [Direction.N, Direction.S, Direction.E, Direction.W]


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

    @property
    def direction(self):
        assert self.path, f'Car lost {self}'
        return self.path[0]


    @classmethod
    def from_json(cls, json_str) -> 'Car':
        return cls(**json.loads(json_str))

    def __repr__(self):
        return f"({self.id}, {self.path})"
