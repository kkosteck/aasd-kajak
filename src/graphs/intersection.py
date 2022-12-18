import random

import networkx as nx
import matplotlib.pyplot as plt


OPPOSITE = {
    "N": "S",
    "S": "N",
    "W": "E",
    "E": "W"
}

RIGHT = {
    "N": "W",
    "S": "E",
    "W": "S",
    "E": "N"
}

LEFT = {
    "N": "E",
    "S": "W",
    "W": "N",
    "E": "S"
}


class Intersection:

    def __init__(self, idx, in_edges, out_edges):
        self.idx = idx
        self.graph = nx.DiGraph()
        self._generate_graph(in_edges, out_edges)

    def _generate_graph(self, in_edges, out_edges):
        out_dirs = set(n[0] for n in out_edges)
        for node in out_edges:
            self.graph.add_node(node, weight=random.randint(1, 10))
        for node in in_edges:
            self.graph.add_node(node, weight=random.randint(1, 10))
            current_dir = node[0]
            current_lane = int(node[1])
            counted = max([int(edge[1]) for edge in in_edges if edge[0] == current_dir])
            if OPPOSITE[current_dir] in out_dirs:  # choose opposite direction
                node_out = self._choose_node(current_lane, OPPOSITE[current_dir], out_edges)
                self.graph.add_edge(node, node_out, delay=random.randint(1, 10))
            else:
                if RIGHT[current_dir] in out_dirs and (current_lane <= counted // 2
                                                       or (current_lane > counted // 2
                                                           and LEFT[current_dir] not in out_dirs)):
                    node_out = self._choose_node(current_lane, RIGHT[current_dir], out_edges)
                    self.graph.add_edge(node, node_out, delay=random.randint(1, 10))
                elif LEFT[current_dir] in out_dirs and ((current_lane <= counted // 2
                                                         and RIGHT[current_dir] not in out_dirs)
                                                        or current_lane > counted // 2):
                    node_out = self._choose_node(current_lane, LEFT[current_dir], out_edges)
                    self.graph.add_edge(node, node_out, delay=random.randint(1, 10))
                else:
                    node_out = self._choose_node(current_lane, current_dir, out_edges)
                    self.graph.add_edge(node, node_out, delay=random.randint(1, 10))
            if current_lane <= counted // 2:
                node_out = f"{RIGHT[current_dir]}{node[1]}_OUT"
                if node_out in out_edges:
                    self.graph.add_edge(node, node_out, delay=random.randint(1, 10))
            else:
                node_out = f"{LEFT[current_dir]}{node[1]}_OUT"
                if node_out in out_edges:
                    self.graph.add_edge(node, node_out, delay=random.randint(1, 10))

    def _choose_node(self, current, opposite_dir, nodes_list):
        closest = min([int(n[1]) for n in nodes_list if n[0] == opposite_dir],
                      key=lambda x: abs(x - current))
        return f"{opposite_dir}{closest}_OUT"

    def step(self):
        for node in self.graph.nodes(data=True):
            current_weight = node[1]["weight"]
            if "OUT" in node[0] or current_weight == 0:
                continue
            transfer_to = random.choice(list(self.graph.out_edges(node[0], data=True)))[1]
            transfer_value = random.randint(1, current_weight)
            nx.set_node_attributes(self.graph, {node[0]: current_weight - transfer_value}, "weight")
            nx.set_node_attributes(self.graph, {transfer_to: current_weight + transfer_value},
                                   "weight")

    def get_out_traffic(self):
        traffic = {}
        for node in self.graph.nodes(data=True):
            if "OUT" not in node[0]:
                continue
            if node[0][0] not in traffic:
                traffic[node[0][0]] = 0
            else:
                traffic[node[0][0]] += node[1]["weight"]
        return traffic

    def insert_traffic(self, value, direction):
        for node in self.graph.nodes:
            if node[0] == direction and "IN" in node and value > 0:
                add_value = random.randint(1, value)
                nx.set_node_attributes(self.graph, {node: add_value}, "weight")
                value -= add_value

    def visualize(self):
        """
        Visualize graph using matplotlib - only for debugging purposes
        Something like PyGame should be used for the final version
        """
        # pos = nx.spring_layout(self.graph)
        pos = {}
        nodes = self.graph.nodes
        for node in nodes:
            x, y = (0, 0)
            direction = node[0]
            lane_id = max([int(edge[1]) for edge in nodes if edge[0] == node[0]]) - int(node[1]) + 1
            offset = lane_id * 0.1 if node.split("_")[1] == "OUT" else -lane_id * 0.1
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

        labels = {node[0]: node[1]["weight"] for node in self.graph.nodes(data=True)}
        nx.draw_networkx_labels(self.graph, pos, labels=labels, font_family="sans-serif")

        plt.title(self.idx)
        ax = plt.gca()
        ax.margins(0.08)
        plt.axis("off")
        plt.tight_layout()
        plt.show()
