from dataclasses import dataclass
from typing import List
import json


class Direction:
    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'
    NONE = 'NONE'

    @staticmethod
    def as_list() -> List[str]:
        return [Direction.N, Direction.S, Direction.E, Direction.W]


@dataclass
class Car:
    id: int
    starting_crossroad_id: int
    starting_queue_direction: str
    path: List[str]

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "starting_crossroad_id": self.starting_crossroad_id,
            "starting_queue_direction": self.starting_queue_direction,
            "path": self.path,
        })

    @classmethod
    def from_json(cls, json_str) -> 'Car':
        return cls(**json.loads(json_str))

    # def __repr__(self) -> str:
    #     return str(self.id)
