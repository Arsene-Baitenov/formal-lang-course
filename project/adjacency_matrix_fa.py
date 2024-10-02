from typing import Any, cast, Dict, Iterable, Optional, Set
from scipy.sparse import csr_matrix, kron
from scipy.sparse.linalg import matrix_power

from pyformlang.finite_automaton import Symbol, NondeterministicFiniteAutomaton


class AdjacencyMatrixFA:
    _states_num: int
    _states: Dict[Any, int]
    _start_states: Set[int]
    _final_states: Set[int]
    _adjacency_matrices: Dict[Any, csr_matrix]
    _transitive_closure: csr_matrix

    def _from_nfa(self, nfa: NondeterministicFiniteAutomaton):
        self._states = {state: i for (i, state) in enumerate(nfa.states)}
        self._states_num = len(nfa.states)
        self._start_states = set(self._states[state] for state in nfa.start_states)
        self._final_states = set(self._states[state] for state in nfa.final_states)

        self._adjacency_matrices = {
            symbol: csr_matrix((self._states_num, self._states_num), dtype=bool)
            for symbol in nfa.symbols
        }

        graph = nfa.to_networkx()
        for from_state, to_state, symbol in graph.edges(data="label"):
            if symbol is not None:
                self._adjacency_matrices[symbol][
                    self._states[from_state], self._states[to_state]
                ] = True

    def _from_params(
        self,
        states_num: int,
        states: Dict[Any, int],
        start_states: Set[int],
        final_states: Set[int],
        adjacency_matrices: Dict[Any, csr_matrix],
    ):
        self._states_num = states_num
        self._states = states
        self._start_states = start_states
        self._final_states = final_states
        self._adjacency_matrices = adjacency_matrices

    def _eval_transitive_closure(self) -> csr_matrix:
        matrix = csr_matrix((self.states_num, self.states_num), dtype=bool)

        for i in range(self.states_num):
            matrix[i, i] = True

        for adjacency_matrix in self.adjacency_matrices.values():
            matrix += adjacency_matrix

        return matrix_power(matrix, self.states_num)

    def __init__(
        self,
        nfa: Optional[NondeterministicFiniteAutomaton] = None,
        states_num: Optional[int] = None,
        states: Optional[Dict[Any, int]] = None,
        start_states: Optional[Set[int]] = None,
        final_states: Optional[Set[int]] = None,
        adjacency_matrices: Optional[Dict[Any, csr_matrix]] = None,
    ):
        if nfa is not None:
            self._from_nfa(nfa)
        else:
            states_num: int = states_num if states_num else 0
            states: Dict[Any, int] = states if states else {}
            start_states: Set[int] = start_states if start_states else set()
            final_states: Set[int] = final_states if final_states else set()
            adjacency_matrices: Dict[Any, csr_matrix] = (
                adjacency_matrices if adjacency_matrices else {}
            )
            self._from_params(
                states_num, states, start_states, final_states, adjacency_matrices
            )

        self._transitive_closure = self._eval_transitive_closure()

    @property
    def states_num(self) -> int:
        return self._states_num

    @property
    def states(self) -> Dict[Any, int]:
        return self._states

    @property
    def start_states(self) -> Set[int]:
        return self._start_states

    @property
    def final_states(self) -> Set[int]:
        return self._final_states

    @property
    def adjacency_matrices(self) -> Dict[Any, csr_matrix]:
        return self._adjacency_matrices

    @property
    def transitive_closure(self) -> csr_matrix:
        return self._transitive_closure

    def accepts(self, word: Iterable[Symbol]) -> bool:
        configurations = [(0, state) for state in self.start_states]
        word = list(word)

        while len(configurations) > 0:
            pos, state = configurations.pop()

            if pos >= len(word):
                if state in self.final_states:
                    return True
                continue

            matrix = self.adjacency_matrices[word[pos]]

            if matrix is not None:
                for to_state in matrix.getrow(state).indices:
                    if matrix[state, to_state]:
                        configurations.append((pos + 1, to_state))

        return False

    def is_empty(self) -> bool:
        transitive_closure = self.transitive_closure

        for start_state in self.start_states:
            for final_state in self.final_states:
                if transitive_closure[start_state, final_state]:
                    return False

        return True

    @classmethod
    def _create_with_params(
        cls,
        states_num: int,
        states: Dict[Any, int],
        start_states: Set[int],
        final_states: Set[int],
        adjacency_matrices: Dict[Any, csr_matrix],
    ) -> "AdjacencyMatrixFA":
        return cls(
            states_num=states_num,
            states=states,
            start_states=start_states,
            final_states=final_states,
            adjacency_matrices=adjacency_matrices,
        )

    def intersect(self, other: "AdjacencyMatrixFA") -> "AdjacencyMatrixFA":
        inter_states_num = self.states_num * other.states_num
        inter_states = {}
        inter_start_states = set()
        inter_final_states = set()
        inter_adjacency_matrices = {}

        for state, idx in self.states.items():
            for other_state, other_idx in other.states.items():
                inter_states[(state, other_state)] = idx * other.states_num + other_idx

        for state in self.start_states:
            for other_state in other.start_states:
                inter_start_states.add(state * other.states_num + other_state)

        for state in self.final_states:
            for other_state in other.final_states:
                inter_final_states.add(state * other.states_num + other_state)

        for symbol in self.adjacency_matrices.keys():
            if symbol in other.adjacency_matrices.keys():
                matrix = self.adjacency_matrices[symbol]
                other_matrix = other.adjacency_matrices[symbol]
                inter_adjacency_matrices[symbol] = cast(
                    csr_matrix, kron(matrix, other_matrix, format="csr")
                )

        return self._create_with_params(
            inter_states_num,
            inter_states,
            inter_start_states,
            inter_final_states,
            inter_adjacency_matrices,
        )


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    return automaton1.intersect(automaton2)
