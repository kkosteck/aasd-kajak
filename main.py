from src.graphs.map_generator import MapGenerator


def main():
    map_graph = MapGenerator(intersections=20)
    map_graph.generate()
    map_graph.visualize()


if __name__ == '__main__':
    main()
