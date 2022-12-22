import asyncio
import json
from typing import Dict, List, Optional, Tuple, Deque
from collections import deque

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour, FSMBehaviour, State

from src.communication.move_car_protocol import MoveCarMessage, MoveCarTemplate
from src.communication.crossroads_info_protocol import CrossroadsInfoTemplate, CrossroadsInfoMessage
from src.communication.state_recommendation_protocol import StateRecommendationTemplate
from src.entity.LightState import LightState
from src.entity.car import Car, Direction
from src.agents.traffic_info_aggregator import TrafficInfoAggregator


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

    def __init__(self, jid: str, password: str,
                 crossroad_id: int,
                 update_status_time: Optional[float] = 2.0,
                 n_crossroad_jid: Optional[str] = None,
                 s_crossroad_jid: Optional[str] = None,
                 e_crossroad_jid: Optional[str] = None,
                 w_crossroad_jid: Optional[str] = None):
        super().__init__(jid=jid, password=password)
        self.crossroad_id = crossroad_id
        self.lights_state: str = LightState.EW
        self.connected_crossroads: Dict[str, str] = {
            Direction.N: n_crossroad_jid,
            Direction.S: s_crossroad_jid,
            Direction.E: e_crossroad_jid,
            Direction.W: w_crossroad_jid,
        }
        self.line_queues: Dict[str, Deque[Car]] = {
            Direction.N: deque(),
            Direction.S: deque(),
            Direction.E: deque(),
            Direction.W: deque(),
        }
        self.update_status_time = update_status_time
        assert '@' in jid
        self._aggregator_jid = f'{jid.split("@")[0]}_aggr@{jid.split("@")[1]}'

    class MoveCars(PeriodicBehaviour):

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
            lights_state = self.agent.get('lights_state')
            line_queues = self.agent.get('line_queues')
            connected_crossroads = self.agent.get('connected_crossroads')

            # TODO: better logic of choosing car to move, maybe 2 at the time, or random queue?
            car_to_move = None
            if lights_state == LightState.NS:
                if line_queues[Direction.N]:
                    car_to_move = line_queues[Direction.N].popleft()
                if line_queues[Direction.S] and not car_to_move:
                    car_to_move = line_queues[Direction.S].popleft()

            if lights_state == LightState.EW:
                if line_queues[Direction.E]:
                    car_to_move = line_queues[Direction.E].popleft()
                if line_queues[Direction.W] and not car_to_move:
                    car_to_move = line_queues[Direction.W].popleft()

            if car_to_move:
                direction = car_to_move.path[0]
                print(
                    f'MOVECAR: {self.agent.jid}: sending car {car_to_move} to {connected_crossroads[direction]}')
                await asyncio.sleep(1)
                await self.send(MoveCarMessage(
                    to=connected_crossroads[direction],
                    car=car_to_move
                ))

            self.agent.set('line_queues', line_queues)

    class SimpleLightsState(State):
        def __init__(self, current_state, default_next_state, timeout=30):
            self.current_state = current_state
            self.default_next_state = default_next_state
            self.timeout = timeout
            super().__init__()

        async def run(self):
            print(f'{self.agent.jid} changed state to {self.current_state}')
            self.agent.set('lights_state', self.current_state)
            while msg := await self.receive(timeout=self.timeout):
                recommended_state = json.loads(msg.body)['state']
                if recommended_state != self.current_state:
                    self.set_next_state(recommended_state)
                    print(
                        f'RECOMMENDATION: {self.agent.jid}: received info from {msg.sender}! Recommended state: {recommended_state}')
                    break
            else:
                self.set_next_state(self.default_next_state)

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
                print(f'MOVECAR: {self.agent.jid}: received car {car} from {msg.sender}')

                selected_queue_line = self.agent.get('line_queues')
                selected_queue_line[direction].append(car)
                self.agent.set("line_queues", selected_queue_line)

    class SendWaitingInfo(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(1)
            await self.send(CrossroadsInfoMessage(to=self.agent.get('_aggregator_jid'),
                                                  line_queues=self.agent.get('line_queues'),
                                                  current_state=self.agent.get('lights_state')))
            print(
                f'CROSSROADS INFO: {self.agent.jid}: sending  to {self.agent.get("_aggregator_jid")}')
            await asyncio.sleep(self.agent.get('update_status_time'))

    class CreateAggregator(OneShotBehaviour):
        async def run(self):
            aggr_agent = TrafficInfoAggregator(self.agent.get("_aggregator_jid"), "pwd")
            await aggr_agent.start(auto_register=True)

    async def setup(self):
        self.set("crossroad_id", self.crossroad_id)
        self.set("lights_state", self.lights_state)
        self.set("line_queues", self.line_queues)
        self.set("connected_crossroads", self.connected_crossroads)
        self.set("update_status_time", self.update_status_time)
        self.set("_aggregator_jid", self._aggregator_jid)

        create_aggr = self.CreateAggregator()
        self.add_behaviour(create_aggr)
        # create_aggr.join()

        print('Created Aggregator agent: ', self._aggregator_jid)

        move_cars = self.MoveCars(period=0.5)
        self.add_behaviour(move_cars)

        process_arriving_cars = self.ProcessArrivingCars()
        self.add_behaviour(process_arriving_cars, MoveCarTemplate())

        send_waiting_info = self.SendWaitingInfo()
        self.add_behaviour(send_waiting_info)

        process_state_info = FSMBehaviour()
        ns_state = self.SimpleLightsState(current_state=LightState.NS, default_next_state=LightState.EW)
        process_state_info.add_state(name=LightState.NS, state=ns_state, initial=True)
        ew_state = self.SimpleLightsState(current_state=LightState.EW, default_next_state=LightState.NS)
        process_state_info.add_state(name=LightState.EW, state=ew_state)
        process_state_info.add_transition(source=LightState.NS, dest=LightState.EW)
        process_state_info.add_transition(source=LightState.EW, dest=LightState.NS)
        self.add_behaviour(process_state_info, StateRecommendationTemplate())
