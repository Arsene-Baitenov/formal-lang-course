from typing import List, Any
import cfpq_data
import networkx as nx


class Graph:
    _graph: nx.MultiDiGraph

    def __init__(self, graph: nx.MultiDiGraph):
        self._graph = graph

    @property
    def num_nodes(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def num_edges(self) -> int:
        return self._graph.number_of_edges()

    @property
    def edge_labels(self) -> List[Any]:
        return cfpq_data.get_sorted_labels(self._graph)
