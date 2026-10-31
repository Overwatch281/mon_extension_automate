"""Transformation algorithms that return a new automaton (FA level)."""

from automata.fa.nfa import NFA


class ConversionMixin:
    """Mixin providing algorithms that build a new automaton from self."""

    def induced_subautomaton(self, states):
        """
        Return the subautomaton induced by a set of states.

        Only the given states are kept, together with the transitions
        between them. Final states are restricted accordingly. The initial
        state must be part of the kept states. The original automaton is
        never modified.

        Parameters
        ----------
        states : iterable
            The states to keep.

        Returns
        -------
        Automaton
            A new automaton of the same class.

        Raises
        ------
        ValueError
            If some state is unknown, or if the initial state is not kept.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        kept = frozenset(states)

        unknown = kept - set(self.states)
        if unknown:
            raise ValueError(f"unknown states: {set(unknown)}")
        if self.initial_state not in kept:
            raise ValueError(
                "the initial state must belong to the induced subautomaton"
            )

        new_transitions = {}
        for state in kept:
            new_paths = {}
            for symbol, destination in self.transitions.get(state, {}).items():
                kept_destinations = self._destination_states(destination) & kept
                if not kept_destinations:
                    continue
                if isinstance(self, NFA):
                    new_paths[symbol] = frozenset(kept_destinations)
                else:
                    new_paths[symbol] = destination
            new_transitions[state] = new_paths

        kwargs = dict(
            states=kept,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=self.final_states & kept,
        )

        # Removing states removes transitions: the result is often partial.
        if hasattr(self, "allow_partial"):
            kwargs["allow_partial"] = True

        return self.__class__(**kwargs)

    def trim(self):
        """
        Return a new automaton restricted to its useful states.

        A state is useful if it is both accessible (reachable from the
        initial state) and coaccessible (able to reach a final state).
        The original automaton is never modified.

        If the language is empty, the initial state is not useful: the
        result is then a single non-final state looping on itself, which
        recognizes the empty language.

        Returns
        -------
        Automaton
            A new automaton of the same class, containing only useful
            states and the transitions between them.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        useful = self.useful_states()

        if self.initial_state not in useful:
            dead_state = self.initial_state
            loop = self._single_destination(dead_state)
            kwargs = dict(
                states={dead_state},
                input_symbols=self.input_symbols,
                transitions={
                    dead_state: {symbol: loop for symbol in self.input_symbols}
                },
                initial_state=dead_state,
                final_states=set(),
            )
            return self.__class__(**kwargs)

        return self.induced_subautomaton(useful)