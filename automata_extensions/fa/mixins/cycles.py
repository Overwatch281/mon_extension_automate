"""Cycles, strongly connected components and finiteness (FA level).

These algorithms rely on helpers provided by AnalyseMixin
(_successors, _check_state, useful_states).
"""


class CyclesMixin:
    """Mixin providing graph-structure algorithms on the transitions."""

    def strongly_connected_components(self):
        """
        Compute the strongly connected components (SCCs) of the automaton.

        Uses Tarjan's algorithm: two states are in the same SCC if each
        is reachable from the other. A state with no cycle through it
        forms its own trivial SCC of size 1.

        Returns
        -------
        list of frozenset
            One frozenset of state names per strongly connected component.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Tarjan, R. (1972). "Depth-first search and linear graph algorithms."
        """
        index_counter = [0]
        index = {}
        lowlink = {}
        on_stack = {}
        stack = []
        result = []

        def strongconnect(node):
            index[node] = index_counter[0]
            lowlink[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack[node] = True

            for successor in self._successors(node):
                if successor not in index:
                    strongconnect(successor)
                    lowlink[node] = min(lowlink[node], lowlink[successor])
                elif on_stack.get(successor):
                    lowlink[node] = min(lowlink[node], index[successor])

            if lowlink[node] == index[node]:
                component = set()
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.add(w)
                    if w == node:
                        break
                result.append(frozenset(component))

        for state in self.states:
            if state not in index:
                strongconnect(state)

        return result

    def _has_cycle_from_roots(self, roots, allowed=None):
        """
        Depth-first search looking for a back edge, starting from `roots`.

        A state is "in progress" while it is on the DFS stack. Meeting an
        in-progress state again means we found a cycle (a self-loop counts).

        Parameters
        ----------
        roots : iterable
            States from which the search starts.
        allowed : set, optional
            If given, the search is restricted to the subgraph induced by
            these states (transitions leaving this set are ignored).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        in_progress = 1
        finished = 2
        color = {}

        def successors_of(node):
            successors = self._successors(node)
            if allowed is not None:
                successors = successors & allowed
            return iter(successors)

        for root in roots:
            if root in color:
                continue
            color[root] = in_progress
            stack = [(root, successors_of(root))]

            while stack:
                node, successors = stack[-1]
                went_deeper = False
                for successor in successors:
                    state_color = color.get(successor)
                    if state_color == in_progress:
                        return True  # arête de retour : cycle trouvé
                    if state_color is None:
                        color[successor] = in_progress
                        stack.append((successor, successors_of(successor)))
                        went_deeper = True
                        break
                if not went_deeper:
                    color[node] = finished
                    stack.pop()

        return False

    def has_cycle(self):
        """
        Test whether the automaton contains at least one cycle.

        Returns
        -------
        bool
            True if some cycle exists anywhere in the transition graph
            (a self-loop is a cycle).

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*
        (cycle detection with DFS).
        """
        return self._has_cycle_from_roots(self.states)

    def has_cycle_from(self, state):
        """
        Test whether a cycle exists in the part of the automaton reachable
        from the given state.

        Parameters
        ----------
        state : str
            The starting state.

        Returns
        -------
        bool
            True if a cycle can be reached from `state` (including a cycle
            through `state` itself).

        Raises
        ------
        ValueError
            If `state` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*.
        """
        self._check_state(state)
        return self._has_cycle_from_roots([state])

    def is_finite(self):
        """
        Decide whether the language of the automaton is finite.

        The language is infinite if and only if there is a cycle made of
        useful states (accessible and coaccessible). Cycles on states that
        can never lead to acceptance do not matter. The empty language is
        finite.

        Returns
        -------
        bool
            True if the recognized language is finite.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        useful = self.useful_states()
        return not self._has_cycle_from_roots(useful, allowed=useful)

    def is_infinite(self):
        """
        Decide whether the language of the automaton is infinite.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return not self.is_finite()