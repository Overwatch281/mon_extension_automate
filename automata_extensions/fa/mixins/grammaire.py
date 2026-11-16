"""Conversion of an automaton to a grammar (FA level)."""


class GrammaireMixin:
    """Mixin providing the conversion to a right-linear grammar."""

    def to_grammar(self):
        """
        Convert the automaton to a right-linear (regular) grammar (#55).

        Each state becomes a nonterminal, a transition from p to q on a
        gives the production ``p -> a q``, and a final state p gives
        ``p -> epsilon``. The start symbol is the initial state.

        Returns
        -------
        RegularGrammar
            A grammar generating the language of the automaton.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        # Imported here to avoid a circular import between the packages.
        from automata_extensions.grammar.regular import RegularGrammar

        return RegularGrammar.from_automaton(self)