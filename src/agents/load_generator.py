import asyncio
import random
import time
from typing import List

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from src.communication.move_car_protocol import MoveCarMessage
from src.entity.car import Car, Direction


# TODO: random frequency with normal distribution along time axis -> traffic grows then decreases
class LoadGenerator(Agent):
    """
    Agent generating cars with defined frequency on input to crossroads.
    Sends message to CrossroadHandler that car has arrived to one of its line
    """

    available_crossroads_ids: List[int]
    frequency: int

    def __init__(self, jid: str, password: str, frequency: int, available_crossroads_ids: List[int]):
        super().__init__(jid, password)
        self.available_crossroads_ids = available_crossroads_ids
        self.frequency = frequency

    class GenerateCar(CyclicBehaviour):
        generated_cars: int

        def generate_car(self) -> Car:
            # path = [Direction.NONE, random.choice(Direction.as_list())]
            path = [Direction.NONE, Direction.E, Direction.E]
            self.generated_cars += 1
            return Car(
                id=self.generated_cars,
                starting_crossroad_id=1,
                starting_queue_direction=Direction.W,  # random.choice(Direction.as_list()),
                create_timestamp=time.time(),
                path=path
            )

        async def on_start(self):
            self.generated_cars = 0

        async def run(self):
            print('sent car')
            await self.send(MoveCarMessage(to="crossroad00@localhost", car=self.generate_car()))
            await asyncio.sleep(15)

    async def setup(self):
        print(f"{self.__class__.__name__} started")
        self.set("frequency", self.frequency)
        self.set("available_crossroads_ids", self.available_crossroads_ids)

        generate_car = self.GenerateCar()
        self.add_behaviour(generate_car)
