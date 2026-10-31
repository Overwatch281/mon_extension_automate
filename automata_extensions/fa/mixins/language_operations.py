"""Operations on languages: union, intersection, difference,
concatenation and Kleene star (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (product from ProductMixin, _destination_states from
AnalyseMixin, _fresh_state from OperationsMixin).
"""


class LanguageOperationsMixin:
    """Mixin providing the classical operations on languages."""

    def _check_same_alphabet(self, other):
        """
        Check that `other` can be combined with this automaton.

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        ValueError
            If the two automata do not share the same input alphabet.
        """
        if not isinstance(other, LanguageOperationsMixin):
            raise TypeError("the other automaton must be an extended automaton")
        if self.input_symbols != other.input_symbols:
            raise ValueError("the two automata must have the same input alphabet")

    def _renamed_paths(self, rename):
        """
        Return the transitions in NFA format, with renamed states.

        The result maps each renamed state to a dictionary
        ``{symbol: set of renamed states}``, whatever the kind of the
        automaton (a DFA destination becomes a one-element set).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return {
            rename(state): {
                symbol: {rename(target) for target in self._destination_states(destination)}
                for symbol, destination in self.transitions.get(state, {}).items()
            }
            for state in self.states
        }

    # ------------------------------------------------------------------
    # Boolean operations (through the product)
    # ------------------------------------------------------------------

    def union(self, other):
        """
        Return an automaton recognizing the union of two languages.

        This is the product of the two automata (completed, after the
        determinization of the non-deterministic ones) where a pair is
        final if at least one of its two states is final.

        Parameters
        ----------
        other : Automaton
            The second automaton (same alphabet).

        Returns
        -------
        ExtendedDFA
            A new complete deterministic automaton.

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        ValueError
            If the alphabets differ.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|) for two DFAs.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.product(other, lambda x, y: x or y)

    def intersection(self, other):
        """
        Return an automaton recognizing the intersection of two languages.

        This is the product of the two automata where a pair is final if
        both of its states are final.

        Parameters
        ----------
        other : Automaton
            The second automaton (same alphabet).

        Returns
        -------
        ExtendedDFA
            A new complete deterministic automaton.

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        ValueError
            If the alphabets differ.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|) for two DFAs.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.product(other, lambda x, y: x and y)

    def difference(self, other):
        """
        Return an automaton recognizing the words of this language that
        are not in the language of `other`.

        This is the intersection with the complement: the product of the
        two automata where a pair is final if its first state is final
        and its second state is not.

        Parameters
        ----------
        other : Automaton
            The second automaton (same alphabet).

        Returns
        -------
        ExtendedDFA
            A new complete deterministic automaton.

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        ValueError
            If the alphabets differ.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|) for two DFAs.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.product(other, lambda x, y: x and not y)

    # ------------------------------------------------------------------
    # Concatenation and Kleene star (with epsilon transitions)
    # ------------------------------------------------------------------

    def concatenate(self, other):
        """
        Return an automaton recognizing the concatenation of two languages.

        The states of the first automaton are renamed ``(0, state)`` and
        those of the second ``(1, state)``, so that they never collide.
        Each final state of the first automaton gets an epsilon transition
        to the initial state of the second one. The final states of the
        result are those of the second automaton. The operands are never
        modified.

        Parameters
        ----------
        other : Automaton
            The second automaton (same alphabet).

        Returns
        -------
        ExtendedNFA
            A new automaton, generally with epsilon transitions (use
            `determinize()` to get a DFA).

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        ValueError
            If the alphabets differ.

        Complexity
        ----------
        O(|Q1| + |Q2| + |E1| + |E2|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        self._check_same_alphabet(other)

        # Imported here to avoid a circular import (nfa.py imports base.py,
        # which imports this module).
        from automata_extensions.fa.nfa import ExtendedNFA

        def first(state):
            return (0, state)

        def second(state):
            return (1, state)

        transitions = self._renamed_paths(first)
        transitions.update(other._renamed_paths(second))

        start_of_second = second(other.initial_state)
        for final_state in self.final_states:
            paths = transitions[first(final_state)]
            paths[''] = set(paths.get('', set())) | {start_of_second}

        return ExtendedNFA(
            states=set(transitions),
            input_symbols=self.input_symbols,
            transitions=transitions,
            initial_state=first(self.initial_state),
            final_states={second(state) for state in other.final_states},
        )

    def star(self):
        """
        Return an automaton recognizing the Kleene star of the language.

        A new state, both initial and final, is added (named ``init``, or
        ``init1``... if that name is taken). It has an epsilon transition
        to the old initial state, and each old final state gets an epsilon
        transition back to it. The new state being final, the empty word
        is accepted. The original automaton is never modified.

        Returns
        -------
        ExtendedNFA
            A new automaton with epsilon transitions.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        from automata_extensions.fa.nfa import ExtendedNFA

        loop_state = self._fresh_state("init")

        transitions = self._renamed_paths(lambda state: state)
        for final_state in self.final_states:
            paths = transitions[final_state]
            paths[''] = set(paths.get('', set())) | {loop_state}
        transitions[loop_state] = {'': {self.initial_state}}

        return ExtendedNFA(
            states=set(transitions),
            input_symbols=self.input_symbols,
            transitions=transitions,
            initial_state=loop_state,
            final_states={loop_state},
        )