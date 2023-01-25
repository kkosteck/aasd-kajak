import matplotlib
matplotlib.use('Agg')

import networkx as nx
import matplotlib.pyplot as plt
from netgraph import Graph
import numpy as np

class IntersectionsGraph(nx.DiGraph):

    def update_intersection(self, node_id: str, values: dict):
        neighbors = self.get_node_neighbors(node_id)
        for direction, value in values.items():
            nx.set_edge_attributes(self, {(neighbors[direction], node_id): {"value": value}})
        self.visualize()

    def update_intersection_state(self, node_id: str, state: str):
        nx.set_node_attributes(self, {node_id: {"state": state}})
        self.visualize()

    def get_node_neighbors(self, node):
        x = self.nodes[node]['x_cord']
        y = self.nodes[node]['y_cord']

        neighbors = {"N": None, "S": None, "E": None, "W": None}
        for neighbor in self.neighbors(node):
            neighbor_x = self.nodes[neighbor]['x_cord']
            neighbor_y = self.nodes[neighbor]['y_cord']
            if y == neighbor_y and x - neighbor_x > 0:
                neighbors['W'] = neighbor
            elif y == neighbor_y and x - neighbor_x < 0:
                neighbors['E'] = neighbor
            elif x == neighbor_x and y - neighbor_y > 0:
                neighbors['S'] = neighbor
            elif x == neighbor_x and y - neighbor_y < 0:
                neighbors['N'] = neighbor
        return neighbors

    def visualize(self):
        plt.clf()
        scale_x = max(nx.get_node_attributes(self, 'x_cord').values()) + 1
        scale_y = max(nx.get_node_attributes(self, 'y_cord').values()) + 1
        pos = {node: np.array((self.nodes[node]["x_cord"] + 1, self.nodes[node]["y_cord"] + 1))
               for node in self.nodes}
        node_labels = {node: self.nodes[node]["state"] for node in self.nodes}

        Graph(
            self,
            scale=(scale_x + 1, scale_y + 1),
            node_layout=pos,
            node_color="lightblue",
            node_labels=node_labels,
            node_size=10,
            node_label_fontdict=dict(size=8),
            edge_layout='curved',
            edge_width=2,
            edge_label_position=0.6,
            edge_layout_kwargs=dict(k=0.7, bundle_parallel_edges=False),
            edge_labels=nx.get_edge_attributes(self, 'value'),
            edge_label_rotate=False,
            edge_label_fontdict=dict(size=8, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')),
            arrows=True
        )

        plt.gca()
        plt.axis("off")
        plt.savefig('grid_graph.png')
        # plt.show()


# global graph variable for simulation used by agents
simulation_graph = IntersectionsGraph()
