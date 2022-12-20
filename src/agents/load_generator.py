import asyncio
import random
from typing import List

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from src.communication.count_awaiting_cars import ResponseCountCarsTemplate
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
            path = [Direction.NONE, random.choice(Direction.as_list())]
            self.generated_cars += 1
            return Car(
                id=self.generated_cars,
                starting_crossroad_id=random.choice(self.agent.get("available_crossroads_ids")),
                starting_queue_direction=random.choice(Direction.as_list()),
                path=path
            )

        async def on_start(self):
            self.generated_cars = 0

        async def run(self):
            print('sent car')
            await self.send(Message(to="crossroad_handler@localhost", metadata={"context": "incoming_car"},
                                    body=self.generate_car().to_json()))
            await asyncio.sleep(3)

    async def setup(self):
        print(f"{self.__class__.__name__} started")
        self.set("frequency", self.frequency)
        self.set("available_crossroads_ids", self.available_crossroads_ids)

        generate_car = self.GenerateCar()
        self.add_behaviour(generate_car, ResponseCountCarsTemplate())
