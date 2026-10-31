"""Product of automata and relations between languages (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (determinize, complete, is_empty).
"""

from collections import deque


class ProductMixin:
    """Mixin providing the product, inclusion and equality of languages."""

    def _check_comparable(self, other):
        """
        Check that `other` can be combined with this automaton.

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        ValueError
            If the two automata do not share the same input alphabet.
        """
        if not isinstance(other, ProductMixin):
            raise TypeError("the other automaton must be an extended automaton")
        if self.input_symbols != other.input_symbols:
            raise ValueError("the two automata must have the same input alphabet")

    def product(self, other, accept_condition):
        """
        Build the lazy Cartesian product of two automata.

        Non-deterministic automata are determinized first, then both
        automata are completed. The product is built by a breadth-first
        search from the pair of initial states, so only the accessible
        pairs of states are created. A pair (p, q) is final when
        `accept_condition(p is final, q is final)` is True:

        - ``lambda x, y: x and y``      -> intersection
        - ``lambda x, y: x or y``       -> union
        - ``lambda x, y: x and not y``  -> difference

        Parameters
        ----------
        other : Automaton
            The second automaton (an extended DFA or NFA over the same
            alphabet).
        accept_condition : callable
            Function taking two booleans and returning a boolean.

        Returns
        -------
        Automaton
            A new deterministic automaton whose states are tuples
            (state_of_self, state_of_other).

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        ValueError
            If the alphabets differ.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|) for two DFAs; the determinization of an
        NFA can be exponential.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        self._check_comparable(other)

        first = self.determinize().complete()
        second = other.determinize().complete()
        symbols = first.input_symbols

        start = (first.initial_state, second.initial_state)
        visited = {start}
        queue = deque([start])
        transitions = {}

        while queue:
            pair = queue.popleft()
            p, q = pair
            transitions[pair] = {}
            for symbol in symbols:
                target = (first.transitions[p][symbol], second.transitions[q][symbol])
                transitions[pair][symbol] = target
                if target not in visited:
                    visited.add(target)
                    queue.append(target)

        final_states = {
            (p, q)
            for (p, q) in visited
            if accept_condition(p in first.final_states, q in second.final_states)
        }

        return first.__class__(
            states=visited,
            input_symbols=symbols,
            transitions=transitions,
            initial_state=start,
            final_states=final_states,
        )

    def language_subset(self, other):
        """
        Test whether the language of this automaton is included in the
        language of `other` (L1 is a subset of L2).

        L1 is included in L2 if and only if L1 intersected with the
        complement of L2 is empty.

        Parameters
        ----------
        other : Automaton
            The second automaton (same alphabet).

        Returns
        -------
        bool
            True if every word accepted by self is accepted by `other`.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|) for two DFAs.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        difference = self.product(other, lambda x, y: x and not y)
        return difference.is_empty()

    def language_equals(self, other):
        """
        Test whether two automata recognize the same language.

        Uses a double inclusion test: L1 is a subset of L2 and L2 is a
        subset of L1.

        Parameters
        ----------
        other : Automaton
            The second automaton (same alphabet).

        Returns
        -------
        bool
            True if both automata accept exactly the same words.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|) for two DFAs.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.language_subset(other) and other.language_subset(self)