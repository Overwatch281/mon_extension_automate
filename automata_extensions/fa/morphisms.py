"""Morphisms between deterministic automata (#61)."""

from automata.fa.nfa import NFA


class AutomatonMorphism:
    """
    A morphism from a deterministic automaton to another one.

    A morphism is a map from the states of the source to the states of the
    target that preserves the structure:

    - the initial state is sent to the initial state;
    - a state is final exactly when its image is final;
    - for each state p and symbol a, the transition from p on a exists
      exactly when the transition from the image of p on a exists, and
      the image of the state reached from p is the state reached from the
      image of p.

    Such a map sends every run of the source to a run of the target, so
    the two automata recognize the same language.

    Parameters
    ----------
    source, target : Automaton
        Two extended deterministic automata over the same alphabet.
    mapping : dict
        For each state of the source, a state of the target.

    Raises
    ------
    NotImplementedError
        If one of the automata is an NFA.
    ValueError
        If the alphabets differ or if the map is not a morphism.
    """

    def __init__(self, source, target, mapping):
        if isinstance(source, NFA) or isinstance(target, NFA):
            raise NotImplementedError("morphisms are defined for deterministic automata")
        if source.input_symbols != target.input_symbols:
            raise ValueError("the two automata must have the same input alphabet")

        mapping = dict(mapping)
        if set(mapping) != set(source.states):
            raise ValueError("the map must be defined on every state of the source")
        if not set(mapping.values()) <= set(target.states):
            raise ValueError("the map must send the states of the source to states of the target")
        if mapping[source.initial_state] != target.initial_state:
            raise ValueError("the initial state must be sent to the initial state")

        for state in source.states:
            image = mapping[state]
            if (state in source.final_states) != (image in target.final_states):
                raise ValueError(f"the finality of the state {state!r} is not preserved")
            for symbol in source.input_symbols:
                reached = source.transitions.get(state, {}).get(symbol)
                image_reached = target.transitions.get(image, {}).get(symbol)
                if (reached is None) != (image_reached is None):
                    raise ValueError(
                        f"the transition of {state!r} on {symbol!r} exists on one side only"
                    )
                if reached is not None and mapping[reached] != image_reached:
                    raise ValueError(
                        f"the transition of {state!r} on {symbol!r} is not preserved"
                    )

        self.source = source
        self.target = target
        self._mapping = mapping

    @property
    def mapping(self):
        """Return a copy of the map, as a dictionary."""
        return dict(self._mapping)

    def __call__(self, state):
        """
        Return the image of a state of the source.

        Raises
        ------
        ValueError
            If `state` is not a state of the source.
        """
        if state not in self._mapping:
            raise ValueError(f"unknown state: {state!r}")
        return self._mapping[state]

    def image(self):
        """Return the set of states of the target that are images."""
        return frozenset(self._mapping.values())

    def is_surjective(self):
        """Test whether every state of the target is the image of a state."""
        return self.image() == frozenset(self.target.states)

    def is_injective(self):
        """Test whether two different states have different images."""
        return len(self.image()) == len(self._mapping)

    def is_isomorphism(self):
        """Test whether the morphism is a bijection (a renaming of states)."""
        return self.is_surjective() and self.is_injective()

    def kernel(self):
        """
        Return the partition of the states of the source into the sets of
        states having the same image.

        Returns
        -------
        frozenset of frozenset
            The blocks of the partition.
        """
        blocks = {}
        for state, image in self._mapping.items():
            blocks.setdefault(image, set()).add(state)
        return frozenset(frozenset(block) for block in blocks.values())

    def __repr__(self):
        return f"AutomatonMorphism({len(self._mapping)} states -> {len(self.target.states)} states)"