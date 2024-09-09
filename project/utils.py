from typing import Tuple
import cfpq_data
import networkx as nx

from project.graph import Graph


def get_graph(name: str) -> Graph:
    graph_csv = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(graph_csv)
    return Graph(graph)


def create_labeled_two_cycles_graph(
        num_first_cycle_nodes: int,
        num_second_cycle_nodes: int,
        labels: Tuple[str, str],
        path: str
) -> None:
    graph = cfpq_data.labeled_two_cycles_graph(
        n=num_first_cycle_nodes,
        m=num_second_cycle_nodes,
        labels=labels
    )
    nx.nx_pydot.write_dot(graph, path)
