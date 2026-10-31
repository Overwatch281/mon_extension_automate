"""Depth-first and breadth-first traversals of the transition graph.

These algorithms rely on helpers provided by AnalyseMixin (_successors and
_check_state). Successors are always visited in a fixed order (sorted by
their readable name), so the result does not change from one run to the
next.
"""

from collections import deque

from automata_extensions.fa.mixins.visualisation import _state_label


class TraversalMixin:
    """Mixin providing DFS and BFS traversals of an automaton."""

    def _sorted_successors(self, state):
        """Return the successors of `state` in a deterministic order."""
        return sorted(self._successors(state), key=_state_label)

    def _traversal_start(self, start):
        """Return the starting state (the initial state by default)."""
        if start is None:
            return self.initial_state
        self._check_state(start)
        return start

    def dfs(self, start=None):
        """
        Depth-first traversal, iterative version (with an explicit stack).

        The states are listed in the order of their first visit. A state
        is marked as visited when it is taken off the stack, and its
        successors are pushed in reverse order, so that the smallest
        successor is explored first. The result is the same as with
        `dfs_recursive`.

        Parameters
        ----------
        start : object, optional
            The state to start from (the initial state by default).

        Returns
        -------
        list
            The states reachable from `start`, in visiting order.

        Raises
        ------
        ValueError
            If `start` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*,
        depth-first search.
        """
        stack = [self._traversal_start(start)]
        visited = set()
        order = []

        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)
            order.append(state)
            for successor in reversed(self._sorted_successors(state)):
                if successor not in visited:
                    stack.append(successor)

        return order

    def dfs_recursive(self, start=None):
        """
        Depth-first traversal, recursive version.

        The states are listed in the order of their first visit, exploring
        the smallest successor first. The result is the same as with
        `dfs`. Python limits the depth of recursion (about 1000 calls), so
        use `dfs` for very large automata.

        Parameters
        ----------
        start : object, optional
            The state to start from (the initial state by default).

        Returns
        -------
        list
            The states reachable from `start`, in visiting order.

        Raises
        ------
        ValueError
            If `start` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*,
        depth-first search.
        """
        visited = set()
        order = []

        def visit(state):
            visited.add(state)
            order.append(state)
            for successor in self._sorted_successors(state):
                if successor not in visited:
                    visit(successor)

        visit(self._traversal_start(start))
        return order

    def _bfs_distances(self, start):
        """
        Breadth-first search with a queue.

        Returns a dictionary giving the distance (number of transitions
        of a shortest path) from `start` to each reachable state. Its keys
        are in the order of discovery.
        """
        distances = {start: 0}
        queue = deque([start])

        while queue:
            state = queue.popleft()
            for successor in self._sorted_successors(state):
                if successor not in distances:
                    distances[successor] = distances[state] + 1
                    queue.append(successor)

        return distances

    def bfs(self, start=None):
        """
        Breadth-first traversal (with a queue).

        The states are listed in the order of their discovery: first the
        starting state, then the states one transition away, then those
        two transitions away, and so on.

        Parameters
        ----------
        start : object, optional
            The state to start from (the initial state by default).

        Returns
        -------
        list
            The states reachable from `start`, in discovery order.

        Raises
        ------
        ValueError
            If `start` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*,
        breadth-first search.
        """
        return list(self._bfs_distances(self._traversal_start(start)))

    def bfs_levels(self, start=None):
        """
        Breadth-first traversal, grouped by level.

        Level k contains the states whose shortest path from `start` has
        exactly k transitions.

        Parameters
        ----------
        start : object, optional
            The state to start from (the initial state by default).

        Returns
        -------
        list of list
            The levels, from the starting state (level 0) onwards.

        Raises
        ------
        ValueError
            If `start` is not a state of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        distances = self._bfs_distances(self._traversal_start(start))

        levels = []
        for state, distance in distances.items():
            if distance == len(levels):
                levels.append([])
            levels[distance].append(state)
        return levels