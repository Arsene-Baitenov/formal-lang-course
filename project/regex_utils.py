from pyformlang.finite_automaton import EpsilonNFA, DeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    enfa = Regex(regex).to_epsilon_nfa()
    if not isinstance(enfa, EpsilonNFA):
        raise ValueError(
            f"Regex '{regex}' cannot be converted to epsilon non-deterministic finite automaton"
        )

    dfa = enfa.to_deterministic()

    return dfa.minimize()
