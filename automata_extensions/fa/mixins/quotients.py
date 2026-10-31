"""Left and right quotients of a language by a word (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (trace from SimulationMixin, reverse from TransformationMixin,
_fresh_state from OperationsMixin).
"""

from automata.fa.nfa import NFA


class QuotientMixin:
    """Mixin providing the quotients of a language by a word."""

    def left_quotient(self, word):
        """
        Return an automaton for the left quotient of the language by a word.

        The left quotient of L by the word u is the set of words w such
        that uw belongs to L. To build it, the word u is read from the
        initial state: the states reached (epsilon closure included)
        become the starting points of the new automaton.

        - For a DFA, the state reached becomes the new initial state. If
          the word is blocked, the quotient is empty and the result is a
          single non-final state.
        - For an NFA, several states may be reached: a new initial state
          (named ``init``, or ``init1``... if that name is taken) is added,
          with epsilon transitions to each of them.

        The original automaton is never modified.

        Parameters
        ----------
        word : str
            The word u to read, symbol by symbol.

        Returns
        -------
        Automaton
            A new automaton of the same class.

        Raises
        ------
        ValueError
            If the word contains a symbol outside the input alphabet.

        Complexity
        ----------
        O(|word| * (|Q| + |E|)) to read the word, then O(|Q| + |E|).

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        reached = self.trace(word)[-1]

        if isinstance(self, NFA):
            new_initial = self._fresh_state("init")
            transitions = {
                state: dict(self.transitions.get(state, {}))
                for state in self.states
            }
            transitions[new_initial] = {'': set(reached)} if reached else {}
            return self.__class__(
                states=set(self.states) | {new_initial},
                input_symbols=self.input_symbols,
                transitions=transitions,
                initial_state=new_initial,
                final_states=self.final_states,
            )

        if reached:
            (state,) = reached
            return self.__class__(
                states=self.states,
                input_symbols=self.input_symbols,
                transitions=self.transitions,
                initial_state=state,
                final_states=self.final_states,
                allow_partial=self.allow_partial,
            )

        # The word is blocked: no word w satisfies "uw in L".
        dead_state = self._fresh_state("dead")
        return self.__class__(
            states={dead_state},
            input_symbols=self.input_symbols,
            transitions={dead_state: {}},
            initial_state=dead_state,
            final_states=set(),
            allow_partial=True,
        )

    def right_quotient(self, word):
        """
        Return an automaton for the right quotient of the language by a word.

        The right quotient of L by the word u is the set of words w such
        that wu belongs to L. It is built by duality: reading u at the end
        of a word of L is reading the reversed word u at the beginning of
        a word of the reversed language. So the right quotient is the
        reverse of the left quotient, by the reversed word, of the reverse
        automaton. The original automaton is never modified.

        Parameters
        ----------
        word : str
            The word u removed at the end of the words.

        Returns
        -------
        ExtendedNFA
            A new automaton with epsilon transitions.

        Raises
        ------
        ValueError
            If the word contains a symbol outside the input alphabet.

        Complexity
        ----------
        O(|word| * (|Q| + |E|)) plus two reversals in O(|Q| + |E|).

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.reverse().left_quotient(word[::-1]).reverse()