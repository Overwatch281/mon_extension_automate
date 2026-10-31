"""Conversions between kinds of finite automata, and the Brzozowski
automaton (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (determinize from DeterminisationMixin and
_destination_states from AnalyseMixin).
"""

from collections import deque

from automata.fa.nfa import NFA


class AutomatonConversionMixin:
    """Mixin providing to_nfa, to_dfa and the Brzozowski automaton."""

    def to_nfa(self):
        """
        Convert the automaton to an NFA.

        A DFA is a particular NFA: each transition is turned into a
        transition to a set made of a single state. An NFA is returned
        unchanged. The original automaton is never modified.

        Returns
        -------
        ExtendedNFA
            An NFA recognizing the same language.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        if isinstance(self, NFA):
            return self

        # Imported here to avoid a circular import (nfa.py imports base.py,
        # which imports this module).
        from automata_extensions.fa.nfa import ExtendedNFA

        return ExtendedNFA(
            states=self.states,
            input_symbols=self.input_symbols,
            transitions={
                state: {
                    symbol: self._destination_states(destination)
                    for symbol, destination in self.transitions.get(state, {}).items()
                }
                for state in self.states
            },
            initial_state=self.initial_state,
            final_states=self.final_states,
        )

    def to_dfa(self):
        """
        Convert the automaton to a DFA (subset construction, #52).

        This is `determinize()`: the states of the result are the
        accessible sets of states of the NFA. A DFA is returned unchanged.

        Returns
        -------
        ExtendedDFA
            A deterministic automaton recognizing the same language.

        Complexity
        ----------
        O(2^|Q| * |Sigma|) in the worst case.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.determinize()

    def _determinized_reverse(self):
        """
        Build the DFA of the reversed language of a DFA, directly.

        This is the subset construction applied to the reversed
        transitions: the first subset is the set of final states of the
        automaton, a subset S and a symbol a lead to the set of states
        that have an a-transition into S, and a subset is final if it
        contains the initial state of the automaton. Only the accessible
        subsets are built. Unlike `reverse().determinize()`, no artificial
        initial state is added, which matters for Brzozowski's algorithm.

        Complexity
        ----------
        O(2^|Q| * |Sigma|) in the worst case.
        """
        predecessors = {}
        for state in self.states:
            for symbol, destination in self.transitions.get(state, {}).items():
                for target in self._destination_states(destination):
                    predecessors.setdefault((target, symbol), set()).add(state)

        start = frozenset(self.final_states)
        visited = {start}
        queue = deque([start])
        transitions = {}

        while queue:
            subset = queue.popleft()
            transitions[subset] = {}
            for symbol in self.input_symbols:
                target = frozenset(
                    state
                    for member in subset
                    for state in predecessors.get((member, symbol), ())
                )
                transitions[subset][symbol] = target
                if target not in visited:
                    visited.add(target)
                    queue.append(target)

        return self.__class__(
            states=visited,
            input_symbols=self.input_symbols,
            transitions=transitions,
            initial_state=start,
            final_states={subset for subset in visited if self.initial_state in subset},
        )

    def brzozowski_automaton(self):
        """
        Return the minimal DFA computed by Brzozowski's algorithm.

        The automaton is first determinized (if it is an NFA). Then the
        reversal followed by a subset construction is applied twice. The
        surprising result of Brzozowski is that the final automaton is the
        minimal complete DFA of the language, because the first step
        gives an accessible DFA. It works on any DFA or NFA, with or
        without epsilon transitions. The states of the result are sets of
        sets of original states.

        Returns
        -------
        ExtendedDFA
            The minimal complete DFA of the language, unique up to
            isomorphism.

        Complexity
        ----------
        Exponential in the worst case, because of the determinizations.

        References
        ----------
        Brzozowski, J. (1962). "Canonical regular expressions and minimal
        state graphs for definite events."
        """
        deterministic = self.determinize()
        return deterministic._determinized_reverse()._determinized_reverse()