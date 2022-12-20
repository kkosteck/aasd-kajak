import asyncio
from typing import Dict, List, Optional, Tuple

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from src.entity.car import Car, Direction


class LightState:
    NS = 'NS'
    EW = 'EW'


class CrossroadHandler(Agent):
    """
    Agent representing crossroad.
    Consists of for queues N, S, W, E storing cars and state of traffic lights.

    Traffic lights has two states:
    NS - pass cars from N,S queues
    EW - pass cars from E,W queues

    Responses to WaitingHandler for CarCount request.
    Reacts to TrafficInfoAggregator for light_change request.
    Moves cars from opened queues to next crossroad based on Car.path field one at the time.
    Processes arriving cars by updating queues.
    """
    lights_state: str = LightState.NS
    line_queue: Dict[str, List[Car]] = {
        Direction.N: [],
        Direction.S: [],
        Direction.E: [],
        Direction.W: [],
    }
    crossroad_id: int

    def __init__(self, jid: str, password: str, crossroad_id: int, n_crossroad_jid: Optional[str] = None,
                 s_crossroad_jid: Optional[str] = None,
                 e_crossroad_jid: Optional[str] = None, w_crossroad_jid: Optional[str] = None):
        super().__init__(jid=jid, password=password)
        self.crossroad_id = crossroad_id

    class MoveCars(CyclicBehaviour):
        sent_messages: int

        def print_queue_state(self):
            line_queues = self.agent.get('line_queue')
            print('=' * 100)
            for direction in Direction.as_list():
                print(direction, ':', line_queues[direction])

        # async def on_start(self):
        #     print("Started crossroad")

        async def run(self):
            # TODO : check if there is another crossroad on the end of the desired direction, if true send message else flush car
            # print(self.agent.get("light_state"))
            self.print_queue_state()
            await asyncio.sleep(1)

    class AllQueueStates(CyclicBehaviour):
        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(10)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
                if self.agent.get("light_state") == LightState.NS:
                    self.agent.set("light_state", LightState.EW)
                else:
                    self.agent.set("light_state", LightState.NS)
            else:
                print("Did not received any message after 10 seconds")
            return

    # class UpdateLight(CyclicBehaviour):
    #     ...

    class ProcessArrivingCars(CyclicBehaviour):
        @staticmethod
        def process_car(car: Car) -> Tuple[Car, str]:
            if len(car.path) == 0:
                return car, Direction.NONE
            next_direction = car.path.pop(0)
            if next_direction == Direction.NONE:
                return car, car.starting_queue_direction

            if next_direction == Direction.S:
                return car, Direction.N
            if next_direction == Direction.N:
                return car, Direction.S
            if next_direction == Direction.E:
                return car, Direction.W
            if next_direction == Direction.E:
                return car, Direction.W

        async def run(self):
            msg = await self.receive(10)
            if msg:
                print('received car')
                car, direction = self.process_car(Car.from_json(msg.body))
                if direction == Direction.NONE:
                    # TODO: save info about flushed cars
                    return

                selected_queue_line = self.agent.get('line_queue')
                selected_queue_line[direction].append(car)
                self.agent.set("line_queue", selected_queue_line)

    async def setup(self):
        self.set("crossroad_id", self.crossroad_id)
        self.set("light_state", LightState.NS)
        self.set("line_queue", self.line_queue)

        print("crossroad started")

        move_cars = self.MoveCars()
        # move_cars1 = self.MoveCars1()
        all_queue_states = self.AllQueueStates()
        process_arriving_cars = self.ProcessArrivingCars()
        self.add_behaviour(move_cars)
        arriving_cars_template = Template()
        arriving_cars_template.metadata = {"context": "incoming_car"}
        self.add_behaviour(process_arriving_cars, arriving_cars_template)
        # self.add_behaviour(move_cars1)
        t = Template()
        # t.metadata = {"fuck": "AASD"}
        # self.add_behaviour(all_queue_states, t)
