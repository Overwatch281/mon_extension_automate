"""Analysis algorithms for finite automata (FA level).

These methods rely only on states, transitions, initial_state and
final_states, so they work identically on DFA, NFA and GNFA.
"""


class AnalyseMixin:
    """Mixin providing structural analysis algorithms for automata."""

    def accessible_states(self):
        """
        Compute the set of states reachable from the initial state.

        Parameters
        ----------
        None

        Returns
        -------
        set
            Set of state names reachable from the initial state.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        visited = set()
        stack = [self.initial_state]

        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)

            transitions_from_state = self.transitions.get(state, {})
            for symbol, destination in transitions_from_state.items():
                if isinstance(destination, (set, frozenset)):
                    for next_state in destination:
                        if next_state not in visited:
                            stack.append(next_state)
                else:
                    if destination not in visited:
                        stack.append(destination)

        return visited

    def coaccessible_states(self):
        """
        Compute the set of states from which a final state is reachable.

        Equivalent to computing accessible_states() on the reversed
        automaton, starting from the final states instead of the
        initial state.

        Parameters
        ----------
        None

        Returns
        -------
        set
            Set of state names from which at least one final state
            can be reached.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        # Build the reverse transition map: for each state, its predecessors.
        reverse_transitions = {state: set() for state in self.states}
        for state, paths in self.transitions.items():
            for symbol, destination in paths.items():
                targets = destination if isinstance(destination, (set, frozenset)) else {destination}
                for target in targets:
                    reverse_transitions[target].add(state)

        visited = set()
        stack = list(self.final_states)

        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)
            for predecessor in reverse_transitions.get(state, set()):
                if predecessor not in visited:
                    stack.append(predecessor)

        return visited


    def useful_states(self):
        """
        Compute the set of useful states (both accessible and coaccessible).

        A state is useful if it lies on at least one accepted path:
        reachable from the initial state AND able to reach a final state.

        Parameters
        ----------
        None

        Returns
        -------
        set
            Set of useful state names.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.accessible_states() & self.coaccessible_states()
    def is_trim(self):
        """
        Test whether the automaton is trim (every state is useful).

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True if every state is both accessible and coaccessible.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.useful_states() == set(self.states)
    def is_accessible_state(self, state):
        """
        Test whether a given state is accessible.

        Parameters
        ----------
        state : str
            The state to test.

        Returns
        -------
        bool
            True if the state is reachable from the initial state.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return state in self.accessible_states()

    def is_coaccessible_state(self, state):
        """
        Test whether a given state is coaccessible.

        Parameters
        ----------
        state : str
            The state to test.

        Returns
        -------
        bool
            True if a final state can be reached from this state.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return state in self.coaccessible_states()