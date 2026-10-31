"""Analysis algorithms for finite automata (FA level).

These methods rely only on states, transitions, initial_state and
final_states, so they work identically on DFA, NFA and GNFA.
"""

from automata.fa.nfa import NFA


class AnalyseMixin:
    """Mixin providing structural analysis algorithms for automata."""

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _destination_states(self, destination):
        """
        Return the set of states designated by a transition value.

        The format of a transition value depends on the kind of automaton,
        not on the kind of value: an NFA stores a set of states, a DFA
        stores a single state. Testing the class (and not whether the value
        is a set) matters, because the states of a DFA may themselves be
        frozensets (this happens after a minimization).

        Complexity
        ----------
        O(size of the destination)
        """
        if isinstance(self, NFA):
            return set(destination)
        return {destination}

    def _successors(self, state):
        """
        Return the set of states reachable from `state` in one transition.

        Complexity
        ----------
        O(number of transitions leaving `state`)
        """
        successors = set()
        for destination in self.transitions.get(state, {}).values():
            successors |= self._destination_states(destination)
        return successors

    def _predecessors_map(self):
        """
        Build the reversed transition graph.

        Returns
        -------
        dict
            For each state, the set of states having a transition to it.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        reverse = {state: set() for state in self.states}
        for state in self.states:
            for target in self._successors(state):
                reverse[target].add(state)
        return reverse

    def _forward_reachable(self, sources):
        """
        Depth-first search following transitions forward.

        Returns the set of states reachable from any state of `sources`
        (the sources themselves included).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        visited = set()
        stack = list(sources)

        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)
            for next_state in self._successors(state):
                if next_state not in visited:
                    stack.append(next_state)

        return visited

    def _backward_reachable(self, targets):
        """
        Depth-first search following transitions backward.

        Returns the set of states from which some state of `targets` can
        be reached (the targets themselves included).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        reverse = self._predecessors_map()
        visited = set()
        stack = list(targets)

        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)
            for predecessor in reverse.get(state, set()):
                if predecessor not in visited:
                    stack.append(predecessor)

        return visited

    def _check_state(self, state):
        """Raise ValueError if `state` does not belong to the automaton."""
        if state not in self.states:
            raise ValueError(f"unknown state: {state!r}")

    # ------------------------------------------------------------------
    # Accessibility
    # ------------------------------------------------------------------

    def accessible_states(self):
        """
        Compute the set of states reachable from the initial state.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self._forward_reachable({self.initial_state})

    def is_accessible_state(self, state):
        """
        Test whether a given state is accessible.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return state in self.accessible_states()

    def coaccessible_states(self):
        """
        Compute the set of states from which a final state is reachable.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self._backward_reachable(self.final_states)

    def is_coaccessible_state(self, state):
        """
        Test whether a given state is coaccessible.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return state in self.coaccessible_states()

    def useful_states(self):
        """
        Compute the set of useful states (both accessible and coaccessible).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self.accessible_states() & self.coaccessible_states()

    def is_trim(self):
        """
        Test whether the automaton is trim (every state is useful).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self.useful_states() == set(self.states)

    # ------------------------------------------------------------------
    # Reachability from / to a given state
    # ------------------------------------------------------------------

    def reachable_states_from(self, state):
        """
        Compute the states reachable from a given state.

        The state itself is included (path of length 0).

        Parameters
        ----------
        state : str
            The starting state.

        Returns
        -------
        set
            States reachable from `state`.

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
        return self._forward_reachable({state})

    def predecessors(self, state):
        """
        Compute the direct predecessors of a state.

        These are the states having at least one transition leading
        directly to `state` (a self-loop makes a state its own
        predecessor).

        Parameters
        ----------
        state : str
            The target state.

        Returns
        -------
        set
            States with a transition to `state`.

        Raises
        ------
        ValueError
            If `state` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        self._check_state(state)
        return self._predecessors_map()[state]

    def states_reaching(self, state):
        """
        Compute all the states from which a given state can be reached.

        This is a backward traversal of the transitions. The state itself
        is included (path of length 0).

        Parameters
        ----------
        state : str
            The target state.

        Returns
        -------
        set
            States from which `state` is reachable.

        Raises
        ------
        ValueError
            If `state` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        self._check_state(state)
        return self._backward_reachable({state})

    # ------------------------------------------------------------------
    # Emptiness
    # ------------------------------------------------------------------

    def is_empty(self):
        """
        Decide whether the language of the automaton is empty.

        The language is empty if and only if no accepting state is
        accessible from the initial state.

        Returns
        -------
        bool
            True if the recognized language is empty.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return not (self.accessible_states() & set(self.final_states))