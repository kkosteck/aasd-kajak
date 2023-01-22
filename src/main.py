import time

from src.agents.load_generator import LoadGenerator
from src.graphs.map_generator import MapGenerator


def main():
    map_generator = MapGenerator()
    dispatcher, crossroads = map_generator.generate()
    map_generator.graph.visualize()
    for crossroad in crossroads:
        crossroad.start().result()
    dispatcher.start().result()
    load_generator = LoadGenerator("load_generator@localhost", "pwd", 1, 5, [crossroad.crossroad_id for crossroad in crossroads])
    load_generator.start().result()

    while load_generator.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            for crossroad in crossroads:
                crossroad.stop()
                dispatcher.stop()
            break
    print("Agents finished")


if __name__ == "__main__":
    main()
