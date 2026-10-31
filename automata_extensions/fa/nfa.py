from automata.fa.nfa import NFA

from automata_extensions.fa.base import ExtendedFA


class ExtendedNFA(ExtendedFA, NFA):
    """NFA augmented with the algorithms defined in ExtendedFA and its mixins."""
    pass