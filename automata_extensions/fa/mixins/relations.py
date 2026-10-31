"""Relations between automata (FA level)."""

from collections import deque

from automata.fa.nfa import NFA


class RelationsMixin:
    """Mixin providing comparisons between two automata."""

    def is_isomorphic(self, other):
        """
        Test whether two deterministic automata are isomorphic.

        Two automata are isomorphic if their states can be renamed so that
        they become identical: same initial state, same final states and
        same transitions. The two automata are read in parallel from their
        initial states, building the renaming on the fly; the search fails
        as soon as an inconsistency is found.

        Only the accessible states are compared: unreachable states are
        ignored. Automata with different alphabets are never isomorphic.

        Parameters
        ----------
        other : Automaton
            The second automaton (deterministic).

        Returns
        -------
        bool
            True if a renaming of the states makes both automata equal.

        Raises
        ------
        TypeError
            If `other` is not an extended automaton.
        NotImplementedError
            If one of the automata is non-deterministic.

        Complexity
        ----------
        O(|Q| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        if not isinstance(other, RelationsMixin):
            raise TypeError("the other automaton must be an extended automaton")
        if isinstance(self, NFA) or isinstance(other, NFA):
            raise NotImplementedError(
                "isomorphism is only implemented for deterministic automata"
            )
        if self.input_symbols != other.input_symbols:
            return False

        if len(self.accessible_states()) != len(other.accessible_states()):
            return False

        # renaming[p] = state of `other` playing the role of p
        renaming = {self.initial_state: other.initial_state}
        images = {other.initial_state}
        queue = deque([self.initial_state])

        while queue:
            p = queue.popleft()
            q = renaming[p]

            if (p in self.final_states) != (q in other.final_states):
                return False

            for symbol in self.input_symbols:
                next_p = self.transitions.get(p, {}).get(symbol)
                next_q = other.transitions.get(q, {}).get(symbol)

                if (next_p is None) != (next_q is None):
                    return False
                if next_p is None:
                    continue

                if next_p in renaming:
                    if renaming[next_p] != next_q:
                        return False
                else:
                    if next_q in images:
                        return False  # deux états distincts vers le même
                    renaming[next_p] = next_q
                    images.add(next_q)
                    queue.append(next_p)

        return True