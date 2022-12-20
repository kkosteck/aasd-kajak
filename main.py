from src.graphs.map_generator import MapGenerator
import random

random.seed(10)


def main():
    map_graph = MapGenerator(inters_count=16, width=4, height=4)
    map_graph.generate()
    for idx in range(3):
        map_graph.step()
        map_graph.intersections[5].visualize()
    # map_graph.visualize()


if __name__ == '__main__':
    main()
