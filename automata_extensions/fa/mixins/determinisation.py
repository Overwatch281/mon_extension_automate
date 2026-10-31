"""Determinism, epsilon closures and determinization (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (_epsilon_closure and _step from SimulationMixin,
_check_state and _destination_states from AnalyseMixin).
"""

from collections import deque

from automata.fa.nfa import NFA


class DeterminisationMixin:
    """Mixin providing determinism tests and the subset construction."""

    def is_deterministic(self):
        """
        Test whether the automaton is deterministic.

        An automaton is deterministic if it has no epsilon transition and
        at most one transition for each state and each symbol. A
        deterministic automaton is not necessarily complete. An
        ExtendedDFA is always deterministic.

        Returns
        -------
        bool
            True if the automaton is deterministic.

        Complexity
        ----------
        O(|E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        for state in self.states:
            for symbol, destination in self.transitions.get(state, {}).items():
                destinations = self._destination_states(destination)
                if len(destinations) > 1:
                    return False
                if symbol == '' and destinations:
                    return False
        return True

    def epsilon_closure(self, state):
        """
        Compute the epsilon closure of a state.

        This is the set of states reachable from `state` by following
        only epsilon transitions (the empty string ''). The state itself
        always belongs to its closure.

        Parameters
        ----------
        state : str
            The starting state.

        Returns
        -------
        set
            The epsilon closure of `state`.

        Raises
        ------
        ValueError
            If `state` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        self._check_state(state)
        return self._epsilon_closure({state})

    def epsilon_closure_of_set(self, states):
        """
        Compute the epsilon closure of a set of states.

        This is the union of the epsilon closures of its states.

        Parameters
        ----------
        states : set
            A set (or frozenset) of states. Do not pass a bare string.

        Returns
        -------
        set
            The epsilon closure of the set.

        Raises
        ------
        ValueError
            If one of the states is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        states = set(states)
        for state in states:
            self._check_state(state)
        return self._epsilon_closure(states)

    def determinize(self):
        """
        Return a deterministic automaton recognizing the same language.

        This is the subset construction. Starting from the epsilon
        closure of the initial state, each subset of states and each
        symbol give a new subset (the epsilon closure of the states
        reached). Only the accessible subsets are built. A subset is
        final if it contains a final state of the original automaton.

        The result is a complete ExtendedDFA whose states are frozensets
        of states of the original automaton. The empty frozenset acts as
        a sink state when it is reached. A deterministic automaton is
        returned unchanged. The original automaton is never modified.

        Returns
        -------
        ExtendedDFA
            A complete deterministic automaton.

        Complexity
        ----------
        O(2^|Q| * |Sigma|) in the worst case, since up to 2^|Q| subsets
        can be accessible.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        if not isinstance(self, NFA):
            return self

        # Imported here to avoid a circular import (dfa.py imports base.py,
        # which imports this module).
        from automata_extensions.fa.dfa import ExtendedDFA

        start = frozenset(self._epsilon_closure({self.initial_state}))
        visited = {start}
        queue = deque([start])
        transitions = {}

        while queue:
            subset = queue.popleft()
            transitions[subset] = {}
            for symbol in self.input_symbols:
                target = frozenset(
                    self._epsilon_closure(self._step(subset, symbol))
                )
                transitions[subset][symbol] = target
                if target not in visited:
                    visited.add(target)
                    queue.append(target)

        final_states = {
            subset for subset in visited if subset & self.final_states
        }

        return ExtendedDFA(
            states=visited,
            input_symbols=self.input_symbols,
            transitions=transitions,
            initial_state=start,
            final_states=final_states,
        )