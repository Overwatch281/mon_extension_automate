"""Algebraic objects of a deterministic automaton: morphisms and monoid.

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (_require_deterministic, induced_subautomaton, complete,
equivalence_classes, accessible_states).
"""

from collections import deque

from automata_extensions.fa.monoid import SyntacticMonoid
from automata_extensions.fa.morphisms import AutomatonMorphism


class AlgebraMixin:
    """Mixin providing morphisms of automata and the syntactic monoid."""

    def merge_states(self, partition):
        """
        Merge the states of each block of a partition (#61).

        The result is the projection morphism onto the quotient automaton,
        whose states are the blocks. The partition must be a congruence:
        the states of a block are all final or all non-final, and for each
        symbol they either all lack the transition or all go to the same
        block. The original automaton is never modified.

        Parameters
        ----------
        partition : iterable of iterable
            Disjoint blocks of states covering every state.

        Returns
        -------
        AutomatonMorphism
            The projection; its `target` is the quotient automaton, whose
            states are frozensets of states.

        Raises
        ------
        NotImplementedError
            For a non-deterministic automaton.
        ValueError
            If the blocks are not a partition of the states, or if the
            partition is not a congruence.

        Complexity
        ----------
        O(|Q| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        self._require_deterministic()

        blocks = [frozenset(block) for block in partition]
        covered = set()
        for block in blocks:
            if not block:
                raise ValueError("a block of the partition is empty")
            if covered & block:
                raise ValueError("the blocks of the partition overlap")
            covered |= block
        if covered != set(self.states):
            raise ValueError("the blocks must cover exactly the states of the automaton")

        block_of = {state: block for block in blocks for state in block}

        transitions = {}
        for block in blocks:
            row = {}
            for symbol in self.input_symbols:
                reached = {self.transitions.get(state, {}).get(symbol) for state in block}
                if None in reached:
                    if len(reached) > 1:
                        raise ValueError(
                            f"the states of a block differ on the existence of the transition on {symbol!r}"
                        )
                    continue
                next_blocks = {block_of[state] for state in reached}
                if len(next_blocks) > 1:
                    raise ValueError(
                        f"the partition is not a congruence: a block splits on {symbol!r}"
                    )
                row[symbol] = next_blocks.pop()
            transitions[block] = row

        final_blocks = set()
        for block in blocks:
            finals = {state in self.final_states for state in block}
            if len(finals) > 1:
                raise ValueError("a block mixes final and non-final states")
            if finals == {True}:
                final_blocks.add(block)

        quotient = self.__class__(
            states=set(blocks),
            input_symbols=self.input_symbols,
            transitions=transitions,
            initial_state=block_of[self.initial_state],
            final_states=final_blocks,
            allow_partial=True,
        )
        return AutomatonMorphism(self, quotient, {state: block_of[state] for state in self.states})

    def minimization_morphism(self):
        """
        Return the morphism of the minimization (#61).

        The accessible part of the automaton is completed, then its
        equivalent states are merged. The morphism goes from this complete
        accessible automaton (its `source`) to the minimal DFA (its
        `target`), which is isomorphic to the result of `minimize()`. Its
        kernel is the set of the equivalence classes.

        Returns
        -------
        AutomatonMorphism
            A surjective morphism onto the minimal complete DFA.

        Raises
        ------
        NotImplementedError
            For a non-deterministic automaton.

        Complexity
        ----------
        O(|Q|^3 * |Sigma|)
        """
        self._require_deterministic()
        reduced = self.induced_subautomaton(self.accessible_states()).complete()
        return reduced.merge_states(reduced.equivalence_classes())

    def morphism_to(self, target):
        """
        Find a morphism from the accessible part of this automaton to
        another one, or None if there is none (#61).

        The image of the initial state is forced, and then the image of
        every state reached by a word is forced by the transitions: the
        two automata are explored in parallel, as in the isomorphism test.

        Parameters
        ----------
        target : Automaton
            An extended deterministic automaton.

        Returns
        -------
        AutomatonMorphism or None
            The morphism from the accessible part of this automaton (its
            `source`) to `target`, or None if the alphabets differ or if
            the structure cannot be preserved.

        Raises
        ------
        NotImplementedError
            If one of the automata is non-deterministic.

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        self._require_deterministic()
        target._require_deterministic()

        if self.input_symbols != target.input_symbols:
            return None

        source = self.induced_subautomaton(self.accessible_states())
        mapping = {source.initial_state: target.initial_state}
        queue = deque([source.initial_state])

        while queue:
            state = queue.popleft()
            image = mapping[state]
            if (state in source.final_states) != (image in target.final_states):
                return None
            for symbol in source.input_symbols:
                reached = source.transitions.get(state, {}).get(symbol)
                image_reached = target.transitions.get(image, {}).get(symbol)
                if (reached is None) != (image_reached is None):
                    return None
                if reached is None:
                    continue
                if reached in mapping:
                    if mapping[reached] != image_reached:
                        return None
                else:
                    mapping[reached] = image_reached
                    queue.append(reached)

        return AutomatonMorphism(source, target, mapping)

    def syntactic_monoid(self):
        """
        Build the syntactic monoid of the language (#62).

        Returns
        -------
        SyntacticMonoid
            The monoid of the transformations of the states of the minimal
            complete DFA induced by the words.

        Complexity
        ----------
        See `SyntacticMonoid.from_automaton`.
        """
        return SyntacticMonoid.from_automaton(self)