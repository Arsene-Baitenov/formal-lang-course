from typing import Tuple, Set
import cfpq_data
import networkx as nx
from networkx import MultiDiGraph
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State

from project.graph import Graph


def get_graph(name: str) -> Graph:
    graph_csv = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(graph_csv)
    return Graph(graph)


def create_labeled_two_cycles_graph(
    num_first_cycle_nodes: int,
    num_second_cycle_nodes: int,
    labels: Tuple[str, str],
    path: str,
) -> None:
    graph = cfpq_data.labeled_two_cycles_graph(
        n=num_first_cycle_nodes, m=num_second_cycle_nodes, labels=labels
    )
    nx.nx_pydot.write_dot(graph, path)


def graph_to_nfa(
    graph: MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    nfa: NondeterministicFiniteAutomaton = (
        NondeterministicFiniteAutomaton.from_networkx(
            graph
        ).remove_epsilon_transitions()
    )

    nodes = [int(node) for node in graph.nodes]

    start_states = start_states if start_states else nodes
    final_states = final_states if final_states else nodes

    for state in start_states:
        nfa.add_start_state(State(state))

    for state in final_states:
        nfa.add_final_state(State(state))

    return nfa
