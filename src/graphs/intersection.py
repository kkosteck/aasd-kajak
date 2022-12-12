import networkx as nx
import matplotlib.pyplot as plt

INTERSECTIONS = {
    "SIMPLE_2X2": {
        "N1_IN": ["S1_OUT", "W1_OUT", "W2_OUT"],
        "N2_IN": ["S2_OUT", "E1_OUT", "E2_OUT"],
        "S1_IN": ["N1_OUT", "E1_OUT", "E2_OUT"],
        "S2_IN": ["N2_OUT", "W1_OUT", "W2_OUT"],
        "W1_IN": ["E1_OUT", "S1_OUT", "S2_OUT"],
        "W2_IN": ["E2_OUT", "N1_OUT", "N2_OUT"],
        "E1_IN": ["W1_OUT", "N1_OUT", "N2_OUT"],
        "E2_IN": ["W2_OUT", "S1_OUT", "S2_OUT"],
    }
}


class Intersection:

    def __init__(self, idx, edges=INTERSECTIONS["SIMPLE_2X2"]):
        self.idx = idx
        self.graph = nx.DiGraph()
        for intersection in INTERSECTIONS.values():
            if set(intersection.keys()) == set(edges):
                self._generate_graph(intersection)
                break

    def _generate_graph(self, config: dict):
        for node in config.keys():
            self.graph.add_node(node)
        for node, node_outs in config.items():
            for node_out in node_outs:
                self.graph.add_edge(node, node_out)

    def visualize(self):
        """
        Visualize graph using matplotlib - only for debugging purposes
        Something like PyGame should be used for the final version
        """
        # pos = nx.spring_layout(self.graph)
        pos = {}
        for node in self.graph.nodes:
            x, y = (0, 0)
            direction = node[0]
            offset = int(node[1]) * 0.1
            offset = int(node[1]) * 0.1 if node.split("_")[1] == "OUT" else -int(node[1]) * 0.1
            if direction == "N":
                x, y = (offset, 1)
            elif direction == "S":
                x, y = (-offset, -1)
            elif direction == "W":
                x, y = (-1, offset)
            elif direction == "E":
                x, y = (1, -offset)
            pos[node] = (x, y)
            color = "r" if "OUT" in node else "g"
            nx.draw_networkx_nodes(self.graph, pos, nodelist=[node], node_color=color)

        for edge in self.graph.edges(data=True):
            if (edge[0][0] + edge[1][0] == "NS") or (edge[0][0] + edge[1][0] == "SN") \
               or (edge[0][0] + edge[1][0] == "EW") or (edge[0][0] + edge[1][0] == "WE"):
                connectionstyle = "arc3"
            else:
                connectionstyle = "arc3,rad=0.2"
            nx.draw_networkx_edges(self.graph, pos, edgelist=[(edge[0], edge[1])], style="dashed",
                                   connectionstyle=connectionstyle)

        # nx.draw_networkx_labels(self.graph, pos, font_family="sans-serif")

        ax = plt.gca()
        ax.margins(0.08)
        plt.axis("off")
        plt.tight_layout()
        plt.show()
