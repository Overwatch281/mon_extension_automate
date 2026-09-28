from automata.fa.dfa import DFA

from automata_extensions.fa.base import ExtendedFA


class ExtendedDFA(ExtendedFA, DFA):
    """DFA augmented with the algorithms defined in ExtendedFA and its mixins."""
    pass