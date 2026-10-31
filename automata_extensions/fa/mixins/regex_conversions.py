"""Conversions towards regular expressions (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA.
"""

from automata.fa.nfa import NFA


class RegexConversionMixin:
    """Mixin providing conversions to a generalized NFA."""

    def to_gnfa(self):
        """
        Convert the automaton to a normalized generalized NFA (GNFA).

        The GNFA has a new initial state with no incoming transition and a
        new final state with no outgoing transition (both named by fresh
        integers). Its transitions are labelled by regular expressions.
        It recognizes the same language, and its states can be eliminated
        one by one with `eliminate_state`.

        Returns
        -------
        ExtendedGNFA
            The equivalent GNFA.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        # Imported here to avoid a circular import (gnfa.py imports mixins).
        from automata_extensions.fa.gnfa import ExtendedGNFA

        if isinstance(self, NFA):
            return ExtendedGNFA.from_nfa(self)
        return ExtendedGNFA.from_dfa(self)