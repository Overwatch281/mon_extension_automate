"""Distinguishability, equivalence classes and minimization (FA level).

These algorithms work on deterministic automata. They rely on helpers
provided by the other mixins of ExtendedFA (is_complete, complete,
accessible_states, induced_subautomaton, _require_deterministic).
"""


class MinimisationMixin:
    """Mixin providing Myhill-Nerode style algorithms on states."""

    def distinguishable_pairs(self):
        """
        Compute the pairs of distinguishable states.

        Two states p and q are distinguishable if some word leads one of
        them to a final state and the other to a non-final state. This is
        the "table-filling" algorithm:

        1. mark every pair containing exactly one final state;
        2. repeat: mark a pair {p, q} if, for some symbol, the pair of
           successors is already marked;
        3. stop when a full pass marks nothing new.

        Returns
        -------
        set of frozenset
            The distinguishable pairs, each one a frozenset of two states.

        Raises
        ------
        NotImplementedError
            For a non-deterministic automaton.
        ValueError
            If the automaton is not complete (call complete() first).

        Complexity
        ----------
        O(|Q|^3 * |Sigma|): at most |Q| passes over the O(|Q|^2) pairs.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*, section on testing equivalence of
        states.
        """
        self._require_deterministic()
        if not self.is_complete():
            raise ValueError(
                "the automaton must be complete: call complete() first"
            )

        states = list(self.states)
        marked = set()

        # Step 1: one final state, one non-final state.
        for i, p in enumerate(states):
            for q in states[i + 1:]:
                if (p in self.final_states) != (q in self.final_states):
                    marked.add(frozenset({p, q}))

        # Step 2: propagate until nothing changes.
        changed = True
        while changed:
            changed = False
            for i, p in enumerate(states):
                for q in states[i + 1:]:
                    pair = frozenset({p, q})
                    if pair in marked:
                        continue
                    for symbol in self.input_symbols:
                        successors = frozenset({
                            self.transitions[p][symbol],
                            self.transitions[q][symbol],
                        })
                        # A successor pair of size 1 means "same state":
                        # it is never in `marked`.
                        if successors in marked:
                            marked.add(pair)
                            changed = True
                            break

        return marked

    def equivalence_classes(self):
        """
        Compute the equivalence classes of states (Myhill-Nerode).

        Two states are equivalent if they are not distinguishable. The
        classes form a partition of the set of states.

        Returns
        -------
        list of frozenset
            One frozenset of states per equivalence class.

        Raises
        ------
        NotImplementedError
            For a non-deterministic automaton.
        ValueError
            If the automaton is not complete (call complete() first).

        Complexity
        ----------
        O(|Q|^3 * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        distinguishable = self.distinguishable_pairs()

        classes = []
        remaining = set(self.states)
        while remaining:
            state = next(iter(remaining))
            members = {
                other
                for other in remaining
                if other == state
                or frozenset({state, other}) not in distinguishable
            }
            classes.append(frozenset(members))
            remaining -= members

        return classes

    def is_minimal(self):
        """
        Test whether the automaton is the minimal complete DFA of its
        language.

        An automaton is minimal if it is complete, if all its states are
        accessible, and if each equivalence class contains exactly one
        state.

        Returns
        -------
        bool
            True if the automaton is minimal.

        Raises
        ------
        NotImplementedError
            For a non-deterministic automaton.

        Complexity
        ----------
        O(|Q|^3 * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        self._require_deterministic()

        if not self.is_complete():
            return False
        if self.accessible_states() != set(self.states):
            return False
        return all(len(cls) == 1 for cls in self.equivalence_classes())

    def minimize(self):
        """
        Return the minimal complete DFA recognizing the same language.

        Steps: keep only the accessible states, complete the automaton,
        compute the equivalence classes, then merge each class into a
        single state. Each state of the result is named by the frozenset
        of original states it stands for. The original automaton is never
        modified.

        Returns
        -------
        Automaton
            A new minimal complete automaton of the same class. It is
            unique up to isomorphism.

        Raises
        ------
        NotImplementedError
            For a non-deterministic automaton.

        Complexity
        ----------
        O(|Q|^3 * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        self._require_deterministic()

        reduced = self.induced_subautomaton(self.accessible_states()).complete()
        classes = reduced.equivalence_classes()
        class_of = {state: cls for cls in classes for state in cls}

        transitions = {}
        for cls in classes:
            representative = next(iter(cls))
            transitions[cls] = {
                symbol: class_of[reduced.transitions[representative][symbol]]
                for symbol in reduced.input_symbols
            }

        final_classes = {
            cls for cls in classes
            if next(iter(cls)) in reduced.final_states
        }

        return self.__class__(
            states=set(classes),
            input_symbols=reduced.input_symbols,
            transitions=transitions,
            initial_state=class_of[reduced.initial_state],
            final_states=final_classes,
        )