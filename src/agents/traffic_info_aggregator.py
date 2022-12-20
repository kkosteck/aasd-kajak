import asyncio

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour



class TrafficInfoAggregator(Agent):
    """
    Agent requesting number of awaiting cars from WaitingHandler.
    Based on number of awaiting cars, chooses state of the traffic lights and sends change request to Crossroad
    """

    class AggregateLines(CyclicBehaviour):
        sent_messages: int

        async def on_start(self):
            print("Starting behaviour . . .")
            self.sent_messages = 0

        async def run(self):
            # await self.send(RequestCountCars("waiting_handler@localhost"))
            cars_count = await self.receive()
            print("counted cars: ", cars_count)
            await asyncio.sleep(3)

            if self.sent_messages > 10:
                # stop agent from behaviour
                await self.agent.stop()

    async def setup(self):
        print("TrafficInfoAggregator started")
        aggregate_lines = self.AggregateLines()
        # self.add_behaviour(aggregate_lines, ResponseCountCarsTemplate())
