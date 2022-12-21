import json

from spade.message import Message
from spade.template import Template

from src.communication.fipa.ontology import Ontology
from src.communication.fipa.performative import Performative


METADATA = {'performative': Performative.INFORM, 'ontology': Ontology.STATE_RECOMMENDATION}


class StateRecommendationMessage(Message):
    def __init__(self, to: str, state: str):
        super().__init__(to=to,
                         metadata=METADATA,
                         body=json.dumps({'state': state}))


class StateRecommendationTemplate(Template):
    def __init__(self):
        super().__init__()
        self.metadata = METADATA