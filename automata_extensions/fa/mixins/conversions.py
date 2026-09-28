"""Transformation algorithms that return a new automaton (FA level)."""


class ConversionMixin:
    """Mixin providing algorithms that build a new automaton from self."""

    def trim(self):
        """
        Return a new automaton restricted to its useful states.

        A state is useful if it is both accessible (reachable from the
        initial state) and coaccessible (able to reach a final state).
        The original automaton is never modified.

        Parameters
        ----------
        None

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

        # Cas limite : langage vide, l'état initial lui-même n'est pas utile.
        # On retourne un automate à un seul état, non final, en boucle sur
        # lui-même : il reconnaît bien le langage vide.
        if self.initial_state not in useful:
            dead_state = self.initial_state
            new_transitions = {
                dead_state: {symbol: dead_state for symbol in self.input_symbols}
            }
            kwargs = dict(
                states={dead_state},
                input_symbols=self.input_symbols,
                transitions=new_transitions,
                initial_state=dead_state,
                final_states=set(),
            )
            return self.__class__(**kwargs)

        new_transitions = {}
        for state in useful:
            paths = self.transitions.get(state, {})
            new_paths = {}
            for symbol, destination in paths.items():
                if isinstance(destination, (set, frozenset)):
                    filtered = destination & useful
                    if filtered:
                        new_paths[symbol] = filtered
                else:
                    if destination in useful:
                        new_paths[symbol] = destination
            new_transitions[state] = new_paths

        new_final_states = self.final_states & useful

        kwargs = dict(
            states=useful,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=new_final_states,
        )

        # Le trim retire des transitions : le résultat est souvent partiel.
        if hasattr(self, "allow_partial"):
            kwargs["allow_partial"] = True

        return self.__class__(**kwargs)