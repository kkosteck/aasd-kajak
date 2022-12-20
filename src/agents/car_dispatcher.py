import asyncio
import time
from typing import List

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from src.communication.move_car_protocol import MoveCarTemplate
from src.entity.car import Car


class CarDispatcher(Agent):
    """
    Agent collecting cars leaving map
    Sets dispatch timestamp for received cars, and calculates statistics based on it
    """

    class DispatchCar(CyclicBehaviour):
        dispatched_cars: List[Car]

        async def on_start(self):
            self.dispatched_cars = []

        async def run(self):
            msg = await self.receive(1)  # wait for a message for 10 seconds
            if msg:
                car = Car.from_json(msg.body)
                car.dispatch_timestamp = time.time()
                self.dispatched_cars.append(car)
                print("Dispatched:", str(car), f"from {msg.sender}, in total", len(self.dispatched_cars))

            await asyncio.sleep(1)

    async def setup(self):
        print(f"{self.__class__.__name__} started")
        dispatch_car = self.DispatchCar()
        self.add_behaviour(dispatch_car, MoveCarTemplate())
