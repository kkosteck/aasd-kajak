import asyncio

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from src.communication.count_awaiting_cars import RequestCountCarsTemplate


class WaitingHandler(Agent):
    """
    Agent counting waiting cars in single Crossroad and sending batch info to TrafficInfoAggregator
    """

    class CountCars(CyclicBehaviour):
        sent_messages: int

        async def on_start(self):
            self.sent_messages = 0
            print("Starting WaitingHandler behaviour . . .")

        async def run(self):
            await self.send(Message(to="crossroad_handler@localhost", metadata={"fuck": "AASD"}, body='fml'))
            # cars_count = await self.receive()
            # print("counted cars: ", cars_count)
            await asyncio.sleep(5)

            if self.sent_messages > 10:
                # stop agent from behaviour
                await self.agent.stop()

    async def setup(self):
        print("WaitingHandler started")
        self.add_behaviour(self.CountCars(), RequestCountCarsTemplate())
