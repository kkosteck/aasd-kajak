import asyncio
import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from src.communication.crossroads_info_protocol import CrossroadsInfoTemplate

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

    class Alive(CyclicBehaviour):
        async def run(self):
            print(f"I'm alive : {self.agent.jid}")
            await asyncio.sleep(3)

    class ProcessCrossroadsInfo(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(20)
            if msg:
                msg_body = json.loads(msg.body)
                line_queues, current_state = msg_body['line_queues'], msg_body['current_state']
                print(f'{self.agent.jid}: received info from {msg.sender}!')


    async def setup(self):
        print("TrafficInfoAggregator started")
        aggregate_lines = self.AggregateLines()
        # self.add_behaviour(aggregate_lines, ResponseCountCarsTemplate())
        process_crossroads_info = self.ProcessCrossroadsInfo()
        self.add_behaviour(process_crossroads_info, CrossroadsInfoTemplate())

        alive = self.Alive()
        self.add_behaviour(alive)
