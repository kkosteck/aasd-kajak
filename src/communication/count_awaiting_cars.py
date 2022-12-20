from spade.message import Message
from spade.template import Template

from src.commons.ontology import Ontology
from src.commons.performative import Performative


class RequestCountCars(Message):
    METADATA = {'performative': Performative.INFORM, 'ontology': Ontology.ARRIVING_CARS}

    def __init__(self, to: str):
        super().__init__(to=to, metadata=dict(self.METADATA))


class RequestCountCarsTemplate(Template):
    def __init__(self):
        super().__init__()
        self.metadata = RequestCountCars.METADATA


class ResponseCountCars(Message):
    metadata = {'performative': Performative.INFORM, 'ontology': Ontology.ARRIVING_CARS}

    def __init__(self, to: str, cars_count: int):
        super().__init__(to=to, metadata=dict(self.metadata), body=str(cars_count))


class ResponseCountCarsTemplate(Template):
    def __init__(self):
        super().__init__()
        self.metadata = {"performative": Performative.INFORM, "ontology": Ontology.ARRIVING_CARS}
