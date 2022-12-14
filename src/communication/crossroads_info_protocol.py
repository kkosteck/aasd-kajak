from typing import Dict, List
import json

from spade.message import Message
from spade.template import Template

from src.communication.fipa.ontology import Ontology
from src.communication.fipa.performative import Performative
from src.commons.util import serialize_list


METADATA = {'performative': Performative.INFORM, 'ontology': Ontology.CROSSROADS_INFO}


class CrossroadsInfoMessage(Message):
    def __init__(self, to: str, line_queues: Dict[str, List], current_state: str):
        super().__init__(to=to,
                         metadata=METADATA,
                         body=json.dumps({
                            'line_queues': {line: serialize_list(list_of_cars)
                                            for line, list_of_cars in line_queues.items()},
                            'current_state': current_state
                         }))


class CrossroadsInfoTemplate(Template):
    def __init__(self):
        super().__init__()
        self.metadata = METADATA
