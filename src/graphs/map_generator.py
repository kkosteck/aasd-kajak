import random

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from src.graphs.intersection import Intersection


class MapGenerator:

    def __init__(self, inters_count=10, width=10, height=10):
        self.inters_count = inters_count
        self.intersections: dict[int, Intersection] = {}
        self.width = width
        self.height = height
        self.grid = np.zeros([width, height], dtype=int)
        self.graph = nx.MultiDiGraph()

    def _create_edges(self, axis):
        node_1 = None
        grid = self.grid if axis == 0 else self.grid.T.copy(order='C')
        for node_2 in (grid_iter := np.nditer(grid, flags=['multi_index'])):
            if grid_iter.multi_index[1] == 0:
                node_1 = None
            node_2 = int(node_2)
            if not node_2:
                continue
            elif not node_1:
                node_1 = node_2
                continue
            else:
                # lanes = random.randint(1, 2)
                lanes = 2
                for lane in range(1, lanes + 1):
                    self.graph.add_edge(node_1, node_2, delay=random.randint(1, 10),
                                        lane=lane, direction="EW" if axis else "NS")
                # lanes = random.randint(1, 2)
                for lane in range(1, lanes + 1):
                    self.graph.add_edge(node_2, node_1, delay=random.randint(1, 10),
                                        lane=lane, direction="WE" if axis else "SN")
                node_1 = node_2

    def _generate_intersections_graphs(self):
        for node in self.graph.nodes(data=True):
            in_edges = []
            out_edges = []
            for _, _, data in self.graph.in_edges(node[0], data=True):
                in_edges.append(f"{data['direction'][1]}{data['lane']}_IN")
            for _, _, data in self.graph.out_edges(node[0], data=True):
                out_edges.append(f"{data['direction'][0]}{data['lane']}_OUT")
            self.intersections[node[0]] = Intersection(node[0], in_edges, out_edges)

    def generate(self):
        # position nodes on the grid
        positions = sorted(random.sample(list(np.ndindex(self.grid.shape)), self.inters_count))
        for idx, (x, y) in enumerate(positions, start=1):
            self.grid[x, y] = idx
            self.graph.add_node(idx, x_cord=x, y_cord=y)

        # add horizontal edges
        self._create_edges(1)
        # add vertical edges
        self._create_edges(0)
        # generate intersection nested graphs
        self._generate_intersections_graphs()

    def step(self):  # simulate next traffix step
        for idx, inter in self.intersections.items():
            inter.step()
            out_traffic = inter.get_out_traffic()
            for neighbor, direction in self._get_intersection_neighbors(idx).items():
                self.intersections[neighbor].insert_traffic(out_traffic[direction], direction)

    def _get_intersection_neighbors(self, idx):
        neighbors = {}
        for edge in self.graph.out_edges(idx, data=True):
            neighbors[edge[1]] = edge[2]['direction'][0]
        return neighbors

    def visualize(self):
        """
        Visualize graph using matplotlib - only for debugging purposes
        Something like PyGame should be used for the final version
        """
        pos = {node: (self.graph.nodes[node]["x_cord"] + 1, self.graph.nodes[node]["y_cord"] + 1)
               for node in self.graph.nodes}

        nx.draw_networkx_nodes(self.graph, pos)

        for edge in self.graph.edges(data=True):
            nx.draw_networkx_edges(self.graph, pos, edgelist=[(edge[0], edge[1])], style="dashed",
                                   connectionstyle=f'arc3, rad = {edge[2]["lane"]*0.05}')

        nx.draw_networkx_labels(self.graph, pos, font_family="sans-serif")

        ax = plt.gca()
        ax.margins(0.08)
        plt.axis("off")
        # plt.tight_layout()
        plt.show()
