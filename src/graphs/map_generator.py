import random
from typing import Tuple
import numpy as np
from src.agents.car_dispatcher import CarDispatcher
from src.graphs.intersections_graph import simulation_graph
from src.agents.crossroad_handler import CrossroadHandler


class MapGenerator:

    def __init__(self, crossroads_count, width, height):
        assert crossroads_count <= width * height
        self.crossroads_count = crossroads_count
        self.width = width
        self.height = height
        self.grid = np.zeros([width, height], dtype=int)
        self.graph = simulation_graph

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
                self.graph.add_edge(node_1, node_2, value=0)
                self.graph.add_edge(node_2, node_1, value=0)
                node_1 = node_2

    def generate(self, jid_dispatcher="dispatcher@localhost") -> Tuple[CarDispatcher, list[CrossroadHandler]]:
        # position nodes on the grid
        crossroad_handlers = []
        for idx, (x, y) in enumerate(list(np.ndindex(self.grid.shape))[:self.crossroads_count], start=1):
            self.grid[x, y] = idx
            self.graph.add_node(idx, x_cord=x, y_cord=y, state="")

        # add horizontal edges
        self._create_edges(1)
        # add vertical edges
        self._create_edges(0)
        
        for node in self.graph.nodes:
            neighbors_jid = {}
            for direction, node_id in self.graph.get_node_neighbors(node).items():
                if node_id is None:
                    neighbors_jid[f"{direction.lower()}_crossroad_jid"] = jid_dispatcher
                else:
                    neighbors_jid[f"{direction.lower()}_crossroad_jid"] = f"crossroad{node_id}@localhost"
            crossroad_handlers.append(CrossroadHandler(f"crossroad{node}@localhost",
                                                       "pwd", node, **neighbors_jid))

        dispatcher = CarDispatcher(jid_dispatcher, "pwd")
        return dispatcher, crossroad_handlers

