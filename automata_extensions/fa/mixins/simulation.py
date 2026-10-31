"""Simulation algorithms: running a word through an automaton (FA level)."""


class SimulationMixin:
    """Mixin providing word recognition and execution traces."""

    def _step(self, current_states, symbol):
        """
        Return the set of states reached from `current_states` by reading
        one symbol (no epsilon closure applied).

        Complexity
        ----------
        O(|current_states|)
        """
        reached = set()
        for state in current_states:
            destination = self.transitions.get(state, {}).get(symbol)
            if destination is None:
                continue
            reached |= self._destination_states(destination)
        return reached

    def _epsilon_closure(self, states):
        """
        Return the set of states reachable from `states` using only
        epsilon transitions (the empty string '' as symbol).

        For a DFA, which has no epsilon transitions, this returns the
        given states unchanged. The public version of this algorithm
        (#34) will be built on top of this method.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in self._step({state}, ''):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def trace(self, word):
        """
        Compute the execution trace of a word.

        The trace is the list of sets of active states: the first element
        is the initial configuration (before reading anything), then one
        element after each symbol read. For a DFA each set has at most one
        state; an empty set means the automaton is blocked.

        Parameters
        ----------
        word : str
            The word to read, symbol by symbol.

        Returns
        -------
        list of frozenset
            The sets of active states, of length len(word) + 1.

        Raises
        ------
        ValueError
            If the word contains a symbol outside the input alphabet.

        Complexity
        ----------
        O(|word| * (|Q| + |E|))

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        current = self._epsilon_closure({self.initial_state})
        history = [frozenset(current)]

        for symbol in word:
            if symbol not in self.input_symbols:
                raise ValueError(
                    f"symbol {symbol!r} is not in the input alphabet"
                )
            current = self._epsilon_closure(self._step(current, symbol))
            history.append(frozenset(current))

        return history

    def accepts(self, word):
        """
        Decide whether the automaton accepts a word.

        The word is accepted if, after reading it entirely, at least one
        active state is a final state.

        Parameters
        ----------
        word : str
            The word to test.

        Returns
        -------
        bool
            True if the word belongs to the language of the automaton.

        Raises
        ------
        ValueError
            If the word contains a symbol outside the input alphabet.

        Complexity
        ----------
        O(|word| * (|Q| + |E|))

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return bool(self.trace(word)[-1] & set(self.final_states))