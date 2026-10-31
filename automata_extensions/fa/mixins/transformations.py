"""Structural transformations of automata (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (_epsilon_closure and _step from SimulationMixin,
_destination_states from AnalyseMixin, _fresh_state from
OperationsMixin).
"""

from automata.fa.nfa import NFA


class TransformationMixin:
    """Mixin providing reversal and epsilon-transition removal."""

    def reverse(self):
        """
        Return an automaton recognizing the mirror language.

        Every transition (p, a, q) becomes (q, a, p), the initial state
        becomes the only final state, and the final states become the
        starting points. Since an NFA has a single initial state, a new
        initial state is added, with epsilon transitions to the former
        final states. The result is therefore always an ExtendedNFA, even
        for a DFA. The original automaton is never modified.

        Returns
        -------
        ExtendedNFA
            A new automaton accepting the words of the original language
            read backwards.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        # Imported here to avoid a circular import (nfa.py imports base.py,
        # which imports this module).
        from automata_extensions.fa.nfa import ExtendedNFA

        new_initial = self._fresh_state("init")

        reversed_paths = {state: {} for state in self.states}
        for state in self.states:
            for symbol, destination in self.transitions.get(state, {}).items():
                for target in self._destination_states(destination):
                    reversed_paths[target].setdefault(symbol, set()).add(state)

        if self.final_states:
            reversed_paths[new_initial] = {'': set(self.final_states)}
        else:
            reversed_paths[new_initial] = {}

        return ExtendedNFA(
            states=set(self.states) | {new_initial},
            input_symbols=self.input_symbols,
            transitions=reversed_paths,
            initial_state=new_initial,
            final_states={self.initial_state},
        )

    def remove_epsilon_transitions(self):
        """
        Return an equivalent automaton without epsilon transitions.

        For each state p and each symbol a, the new transition leads to
        the epsilon closure of the states reached by reading a from the
        epsilon closure of p. A state becomes final if its epsilon closure
        contains a final state. The initial state is unchanged. A
        deterministic automaton has no epsilon transition and is returned
        unchanged. The original automaton is never modified.

        Returns
        -------
        Automaton
            A new automaton of the same class, without epsilon
            transitions.

        Complexity
        ----------
        O(|Q| * (|Q| + |E|) * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        if not isinstance(self, NFA):
            return self

        closures = {
            state: self._epsilon_closure({state}) for state in self.states
        }

        new_transitions = {}
        for state in self.states:
            paths = {}
            for symbol in self.input_symbols:
                targets = self._epsilon_closure(
                    self._step(closures[state], symbol)
                )
                if targets:
                    paths[symbol] = frozenset(targets)
            new_transitions[state] = paths

        new_final_states = {
            state
            for state in self.states
            if closures[state] & self.final_states
        }

        return self.__class__(
            states=self.states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=new_final_states,
        )