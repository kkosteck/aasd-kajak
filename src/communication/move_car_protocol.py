from spade.message import Message
from spade.template import Template

from src.communication.fipa.ontology import Ontology
from src.communication.fipa.performative import Performative
from src.entity.car import Car

METADATA = {'performative': Performative.INFORM, 'ontology': Ontology.MOVE_CAR}


class MoveCarMessage(Message):
    def __init__(self, to: str, car: Car):
        super().__init__(to=to, metadata=METADATA, body=car.to_json())


class MoveCarTemplate(Template):
    def __init__(self):
        super().__init__()
        self.metadata = METADATA
