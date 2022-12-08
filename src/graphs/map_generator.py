import random

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import numpy as np


class MapGenerator:

    def __init__(self, intersections=10, width=10, height=10):
        self.intersections = intersections
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
                # print(node_1, grid_iter.multi_index)
                continue
            else:
                # print(node_2, grid_iter.multi_index)
                for lane in range(1, random.randint(1, 4) + 1):
                    self.graph.add_edge(node_1, node_2, weight=random.randint(1, 10), lane=lane)
                for lane in range(1, random.randint(1, 4) + 1):
                    self.graph.add_edge(node_2, node_1, weight=random.randint(1, 10), lane=lane)
                node_1 = node_2

    def generate(self):
        # position nodes on the grid
        positions = sorted(random.sample(list(np.ndindex(self.grid.shape)), self.intersections))
        for idx, (x, y) in enumerate(positions, start=1):
            self.grid[x, y] = idx
            self.graph.add_node(idx, x_cord=x, y_cord=y)

        # add horizontal edges
        self._create_edges(1)
        # add vertical edges
        self._create_edges(0)

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
