"""Conversions towards regular expressions (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (_destination_states from AnalyseMixin) and on the classes
ExtendedGNFA and EquationSystem.
"""

from automata.fa.nfa import NFA

from automata_extensions.fa.mixins.visualisation import _state_label


class RegexConversionMixin:
    """Mixin providing conversions to a GNFA and to a regular expression."""

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

    def to_regex(self, method="elimination", order=None):
        """
        Convert the automaton to a regular expression.

        Two methods are available:

        - ``"elimination"`` (#53): the automaton is converted to a GNFA
          and its states are eliminated one by one; the label that
          remains between the initial and the final state is the result;
        - ``"arden"`` (#54): the system of equations of the automaton is
          solved with Arden's lemma, and the solution of the initial
          state is the result.

        Both give an expression for the same language, but not always
        the same expression, and the size depends on the order in which
        the states are treated.

        The symbols of the automaton must be single characters that are
        not reserved in the syntax of expressions (``| * + ? ( ) ε ∅``).

        Parameters
        ----------
        method : str
            ``"elimination"`` or ``"arden"``.
        order : iterable, optional
            The order in which the states are eliminated (every state
            once). By default, sorted by name.

        Returns
        -------
        Regex
            An expression recognizing the same language.

        Raises
        ------
        ValueError
            If `method` is unknown, if `order` does not list every state
            exactly once, or if a symbol cannot be used in an expression.

        Complexity
        ----------
        O(|Q|^3) operations on expressions.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        if method not in ("elimination", "arden"):
            raise ValueError(
                f"unknown method {method!r}: use 'elimination' or 'arden'"
            )

        if order is None:
            states_order = sorted(self.states, key=_state_label)
        else:
            states_order = list(order)
            if len(states_order) != len(self.states) or set(states_order) != set(self.states):
                raise ValueError("the order must list every state exactly once")

        from automata_extensions.regex import EquationSystem, empty, parse_regex

        if method == "arden":
            system = EquationSystem.from_automaton(self)
            return system.solve(states_order)[self.initial_state]

        gnfa = self.to_gnfa()
        for state in states_order:
            gnfa = gnfa.eliminate_state(state)
        label = gnfa.transitions[gnfa.initial_state][gnfa.final_state]
        if label is None:
            return empty()
        return parse_regex(label)