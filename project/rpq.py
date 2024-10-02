from networkx import MultiDiGraph

from project.graph_utils import graph_to_nfa
from project.regex_utils import regex_to_dfa
from project.adjacency_matrix_fa import AdjacencyMatrixFA, intersect_automata


def tensor_based_rpq(
    regex: str, graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int]
) -> set[tuple[int, int]]:
    graph_amfa = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))
    regex_dfa = regex_to_dfa(regex)
    regex_amfa = AdjacencyMatrixFA(regex_dfa)

    inter_amfa = intersect_automata(graph_amfa, regex_amfa)

    result = set()

    for g_start in start_nodes:
        for g_final in final_nodes:
            for r_start in regex_dfa.start_states:
                for r_final in regex_dfa.final_states:
                    inter_start = inter_amfa.states[(g_start, r_start)]
                    inter_final = inter_amfa.states[(g_final, r_final)]
                    if inter_amfa.transitive_closure[inter_start, inter_final]:
                        result.add((g_start, g_final))

    return result
