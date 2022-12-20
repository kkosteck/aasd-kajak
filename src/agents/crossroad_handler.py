import asyncio
from typing import Dict, List, Optional, Tuple

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from src.communication.move_car_protocol import MoveCarMessage, MoveCarTemplate
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
    lights_state: str = LightState.EW
    line_queues: Dict[str, List[Car]] = {
        Direction.N: [],
        Direction.S: [],
        Direction.E: [],
        Direction.W: [],
    }
    connected_crossroads: Dict[str, str]
    crossroad_id: int

    def __init__(self, jid: str, password: str, crossroad_id: int, n_crossroad_jid: Optional[str] = None,
                 s_crossroad_jid: Optional[str] = None,
                 e_crossroad_jid: Optional[str] = None, w_crossroad_jid: Optional[str] = None):
        super().__init__(jid=jid, password=password)
        self.crossroad_id = crossroad_id

        self.connected_crossroads = {
            Direction.N: n_crossroad_jid,
            Direction.S: s_crossroad_jid,
            Direction.E: e_crossroad_jid,
            Direction.W: w_crossroad_jid,
        }

    class MoveCars(CyclicBehaviour):

        def print_queue_state(self):
            line_queues = self.agent.get('line_queues')
            print('=' * 20 + str(self.agent.jid) + '=' * 20)
            for direction in Direction.as_list():
                print(direction, ':', line_queues[direction])

        async def run(self):
            """
            Move one car from open queue, one at the time
            """
            # self.print_queue_state()
            light_state = self.agent.get('light_state')
            line_queues = self.agent.get('line_queues')
            connected_crossroads = self.agent.get('connected_crossroads')

            # TODO: better logic of choosing car to move, maybe 2 at the time, or random queue?
            car_to_move = None
            if light_state == LightState.NS:
                if len(line_queues[Direction.N]) > 0:
                    car_to_move = line_queues[Direction.N].pop(0)
                if len(line_queues[Direction.S]) and not car_to_move:
                    car_to_move = line_queues[Direction.S].pop(0)

            if light_state == LightState.EW:
                if len(line_queues[Direction.E]) > 0:
                    car_to_move = line_queues[Direction.E].pop(0)
                if len(line_queues[Direction.W]) and not car_to_move:
                    car_to_move = line_queues[Direction.W].pop(0)

            if car_to_move:
                direction = car_to_move.path[0]
                print(
                    f'{self.agent.jid}: sending car {car_to_move} to {connected_crossroads[direction]}')
                await asyncio.sleep(1)
                await self.send(MoveCarMessage(
                    to=connected_crossroads[direction],
                    car=car_to_move
                ))

            self.agent.set('line_queues', line_queues)
            await asyncio.sleep(3)

    # class AllQueueStates(CyclicBehaviour):
    #     async def run(self):
    #         print("RecvBehav running")
    #
    #         msg = await self.receive(10)  # wait for a message for 10 seconds
    #         if msg:
    #             print("Message received with content: {}".format(msg.body))
    #             if self.agent.get("light_state") == LightState.NS:
    #                 self.agent.set("light_state", LightState.EW)
    #             else:
    #                 self.agent.set("light_state", LightState.NS)
    #         else:
    #             print("Did not received any message after 10 seconds")
    #         return

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

            return car, Direction.reverse(next_direction)

        async def run(self):
            msg = await self.receive(10)
            if msg:
                car, direction = self.process_car(Car.from_json(msg.body))
                print(f'{self.agent.jid}: received car {car} from {msg.sender}')

                selected_queue_line = self.agent.get('line_queues')
                selected_queue_line[direction].append(car)
                self.agent.set("line_queues", selected_queue_line)

    async def setup(self):
        self.set("crossroad_id", self.crossroad_id)
        self.set("light_state", self.lights_state)
        self.set("line_queues", self.line_queues)
        self.set("connected_crossroads", self.connected_crossroads)


        move_cars = self.MoveCars()
        self.add_behaviour(move_cars)
        process_arriving_cars = self.ProcessArrivingCars()
        self.add_behaviour(process_arriving_cars, MoveCarTemplate())
