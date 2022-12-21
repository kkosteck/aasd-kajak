import time

from src.agents.car_dispatcher import CarDispatcher
from src.agents.crossroad_handler import CrossroadHandler
from src.agents.load_generator import LoadGenerator


class Jid:
    CROSSROAD_00: str = "crossroad00@localhost"
    CROSSROAD_01: str = "crossroad01@localhost"
    CROSSROAD_10: str = "crossroad10@localhost"
    CROSSROAD_11: str = "crossroad11@localhost"
    DISPATCHER: str = "dispatcher@localhost"
    LOAD_GENERATOR: str = "load_generator@localhost"


if __name__ == "__main__":
    crossroad00 = CrossroadHandler(Jid.CROSSROAD_00, "pwd", 1, n_crossroad_jid=Jid.DISPATCHER,
                                   s_crossroad_jid=Jid.DISPATCHER, e_crossroad_jid=Jid.CROSSROAD_01,
                                   w_crossroad_jid=Jid.DISPATCHER)
    crossroad01 = CrossroadHandler(Jid.CROSSROAD_01, "pwd", 2, n_crossroad_jid=Jid.DISPATCHER,
                                   s_crossroad_jid=Jid.DISPATCHER, e_crossroad_jid=Jid.DISPATCHER,
                                   w_crossroad_jid=Jid.CROSSROAD_00)

    dispatcher = CarDispatcher(Jid.DISPATCHER, "pwd")

    crossroad00.start().result()
    crossroad01.start().result()
    # dispatcher.start().result()
    # load_generator = LoadGenerator(Jid.LOAD_GENERATOR, "pwd", 1, 5, [1, 2])
    # load_generator_future = load_generator.start().result()

    # while load_generator.is_alive():
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            crossroad00.stop()
            crossroad01.stop()
            dispatcher.stop()
            break
    print("Agents finished")
