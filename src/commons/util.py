from typing import List


def serialize_list(l: List):
    return [e.__dict__ for e in l]
