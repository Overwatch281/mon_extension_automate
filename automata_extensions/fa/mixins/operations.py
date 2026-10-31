"""Completion and complement of automata (FA level)."""

from automata.fa.nfa import NFA


class OperationsMixin:
    """Mixin providing completion and complement."""

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _has_transition(self, state, symbol):
        """
        Test whether `state` has at least one transition on `symbol`.

        Complexity
        ----------
        O(1)
        """
        destination = self.transitions.get(state, {}).get(symbol)
        if destination is None:
            return False
        return len(self._destination_states(destination)) > 0

    def _single_destination(self, state):
        """
        Build the destination value pointing to a single state, in the
        format used by the automaton: a frozenset for an NFA, the bare
        state for a DFA.
        """
        if isinstance(self, NFA):
            return frozenset({state})
        return state

    def _fresh_state(self, base="sink"):
        """
        Return a state name not already used: `base`, then `base1`,
        `base2`, and so on.
        """
        candidate = base
        counter = 0
        while candidate in self.states:
            counter += 1
            candidate = f"{base}{counter}"
        return candidate

    # ------------------------------------------------------------------
    # Completion and complement
    # ------------------------------------------------------------------

    def is_complete(self):
        """
        Test whether the automaton is complete.

        An automaton is complete if every state has at least one
        transition for every symbol of the input alphabet (epsilon
        transitions are not considered).

        Returns
        -------
        bool
            True if the automaton is complete.

        Complexity
        ----------
        O(|Q| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return all(
            self._has_transition(state, symbol)
            for state in self.states
            for symbol in self.input_symbols
        )

    def complete(self):
        """
        Return a complete automaton recognizing the same language.

        Every missing transition is redirected to a new sink state, which
        loops on itself for every symbol. The sink state is only added if
        it is needed. The original automaton is never modified.

        Returns
        -------
        Automaton
            A new, complete automaton of the same class.

        Complexity
        ----------
        O(|Q| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        sink = self._fresh_state()
        sink_destination = self._single_destination(sink)

        new_states = set(self.states)
        new_transitions = {
            state: dict(self.transitions.get(state, {}))
            for state in self.states
        }

        sink_is_used = False
        for state in self.states:
            for symbol in self.input_symbols:
                if not self._has_transition(state, symbol):
                    new_transitions[state][symbol] = sink_destination
                    sink_is_used = True

        if sink_is_used:
            new_states.add(sink)
            new_transitions[sink] = {
                symbol: sink_destination for symbol in self.input_symbols
            }

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=self.final_states,
        )

    def complement(self):
        """
        Return an automaton recognizing the complement language.

        A non-deterministic automaton is determinized first. The
        automaton is then completed, and accepting and non-accepting
        states are swapped. The original automaton is never modified.

        Returns
        -------
        Automaton
            A new deterministic automaton recognizing the words over the
            alphabet that the original automaton rejects.

        Complexity
        ----------
        O(|Q| * |Sigma|) for a DFA; O(2^|Q| * |Sigma|) for an NFA, because
        of the determinization.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        completed = self.determinize().complete()
        new_final_states = frozenset(completed.states) - completed.final_states

        return completed.__class__(
            states=completed.states,
            input_symbols=completed.input_symbols,
            transitions=completed.transitions,
            initial_state=completed.initial_state,
            final_states=new_final_states,
        )