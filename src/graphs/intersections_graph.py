import networkx as nx
import matplotlib.pyplot as plt
from netgraph import Graph
import numpy as np

class IntersectionsGraph(nx.DiGraph):
    
    def add_intersection(self, x_cord, y_cord):
        self.add_node(f"{x_cord}{y_cord}", x_cord=x_cord, y_cord=y_cord)
    
    def update_edge(self, from_intersection, to_intersection, value):
        from_node = f"{from_intersection['x']}{from_intersection['y']}"
        to_node = f"{to_intersection['x']}{to_intersection['y']}"
        self.add_edge(from_node, to_node, value=value)

    def visualize(self):
        scale_x = max(nx.get_node_attributes(self, 'x_cord').values()) + 1
        scale_y = max(nx.get_node_attributes(self, 'y_cord').values()) + 1
        pos = {node: np.array((self.nodes[node]["x_cord"] + 1, self.nodes[node]["y_cord"] + 1))
               for node in self.nodes}

        Graph(
            self,
            scale=(scale_x + 1, scale_y + 1),
            node_layout=pos,
            node_color="lightblue",
            node_labels=True,
            node_size=10,
            node_label_fontdict=dict(size=8),
            edge_layout='curved',
            edge_width=3,
            edge_label_position=0.3,
            edge_layout_kwargs=dict(k=0.5, bundle_parallel_edges=False),
            edge_labels=nx.get_edge_attributes(self, 'value'),
            edge_label_rotate=False,
            edge_label_fontdict=dict(size=8, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')),
            arrows=True
        )

        plt.gca()
        plt.axis("off")
        # plt.savefig('test.png', dpi=1200)
        plt.show()


if __name__ == '__main__':
    grid = IntersectionsGraph()
    for x in range(0, 5):
        for y in range(0, 5):
            grid.add_intersection(x, y)
    grid.update_edge({'x': 0, 'y': 0}, {'x': 0, 'y': 1}, 321)
    grid.update_edge({'x': 0, 'y': 1}, {'x': 0, 'y': 0}, 123)
    grid.visualize()
