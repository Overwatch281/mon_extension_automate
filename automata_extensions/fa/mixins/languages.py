"""Properties and operations on the recognized language (FA level)."""

from automata.fa.nfa import NFA


class LanguageMixin:
    """Mixin providing algorithms about the language of an automaton."""

    def _require_deterministic(self):
        """Raise NotImplementedError if the automaton is non-deterministic."""
        if isinstance(self, NFA):
            raise NotImplementedError(
                "this operation requires a deterministic automaton: "
                "call determinize() first"
            )

    def is_prefix_closed(self):
        """
        Test whether the recognized language is prefix-closed.

        A language is prefix-closed if every prefix of a word of the
        language also belongs to the language. For a deterministic
        automaton, this holds if and only if all the useful states are
        final (a non-final state that can never lead to acceptance does
        not matter). A non-deterministic automaton is determinized first.
        The empty language is prefix-closed.

        Returns
        -------
        bool
            True if the language is prefix-closed.

        Complexity
        ----------
        O(|Q| + |E|) for a DFA; the determinization of an NFA can be
        exponential.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        automaton = self.determinize()
        return automaton.useful_states() <= set(automaton.final_states)

    def prefix_closed_sublanguage(self):
        """
        Return an automaton for the largest prefix-closed sublanguage.

        This is the set of words of the language all of whose prefixes
        also belong to the language. A non-deterministic automaton is
        determinized first. Then only the final states reachable from the
        initial state through final states are kept; transitions leading
        to the other states are removed. If the initial state is not
        final, the result recognizes the empty language. The original
        automaton is never modified.

        Returns
        -------
        Automaton
            A new deterministic automaton (usually partial).

        Complexity
        ----------
        O(|Q| + |E|) for a DFA; the determinization of an NFA can be
        exponential.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        automaton = self.determinize()

        if automaton.initial_state not in automaton.final_states:
            # Le mot vide n'est pas dans le langage : le sous-langage est
            # vide. L'état initial seul, non final, le reconnaît.
            return automaton.induced_subautomaton({automaton.initial_state})

        return automaton.induced_subautomaton(automaton.final_states).trim()

    def is_universal(self):
        """
        Decide whether the language is universal.

        The language is universal if it contains every word over the
        input alphabet (the empty word included). This holds if and only
        if the complement language is empty. A non-deterministic automaton
        is determinized first. A partial automaton is completed first (by
        the complement), so a blocked word counts as rejected.

        Returns
        -------
        bool
            True if the automaton accepts every word of the alphabet.

        Complexity
        ----------
        O(|Q| * |Sigma|) for a DFA; O(2^|Q| * |Sigma|) for an NFA, because
        of the determinization.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        return self.determinize().complement().is_empty()