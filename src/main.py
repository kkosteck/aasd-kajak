import time

from src.agents.crossroad_handler import CrossroadHandler
from src.agents.load_generator import LoadGenerator
from src.agents.traffic_info_aggregator import TrafficInfoAggregator
from src.agents.waiting_handler import WaitingHandler

if __name__ == "__main__":
    crossroad = CrossroadHandler("crossroad_handler@localhost", "pwd", 1)
    future = crossroad.start()
    future.result()  # wait for receiver agent to be prepared.
    load_generator = LoadGenerator("load_generator@localhost", "pwd", 1, 4, [1])
    load_generator_future = load_generator.start()
    # waiting_handler = WaitingHandler("waiting_handler@localhost", "pwd")
    # sender_future = waiting_handler.start()
    # sender_future.result()

    while crossroad.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            # waiting_handler.stop()
            crossroad.stop()
            break
    print("Agents finished")
