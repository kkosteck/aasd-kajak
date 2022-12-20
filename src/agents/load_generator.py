import asyncio
import random
import time
from typing import List

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import numpy as np

from src.communication.move_car_protocol import MoveCarMessage
from src.entity.car import Car, Direction


class LoadGenerator(Agent):
    """
    Agent generating cars with defined intervals on input to crossroads.
    Cars are send with sine wave frequency and given max/min intervals.
    Sends message to CrossroadHandler that car has arrived to one of its line
    """

    available_crossroads_ids: List[int]
    min_interval: int
    max_interval: int

    def __init__(self, jid: str, password: str, min_interval: int, max_interval: int, available_crossroads_ids: List[int]):
        super().__init__(jid, password)
        self.available_crossroads_ids = available_crossroads_ids
        self.min_interval = min_interval
        self.max_interval = max_interval

    class GenerateCar(CyclicBehaviour):
        generated_cars: int
        sample: int
        frequency: np.ndarray

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
            self.sample = 0
            min_inter = self.get("min_interval")
            max_inter = self.get("max_interval")
            self.frequency = ((max_inter + min_inter)/2) + (((max_inter - min_inter)/2) * np.sin(2*np.linspace(0, 2*np.pi, 20)))

        async def run(self):
            print('sent car')
            await self.send(MoveCarMessage(to="crossroad00@localhost", car=self.generate_car()))
            await asyncio.sleep(self.frequency[self.sample])
            self.sample = (self.sample + 1) % len(self.frequency)
            print(self.sample)
 
    async def setup(self):
        print(f"{self.__class__.__name__} started")
        self.set("min_interval", self.min_interval)
        self.set("max_interval", self.max_interval)
        self.set("available_crossroads_ids", self.available_crossroads_ids)

        generate_car = self.GenerateCar()
        self.add_behaviour(generate_car)
