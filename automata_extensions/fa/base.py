"""Common base class combining all FA-level mixins."""

from automata.fa.fa import FA

from automata_extensions.fa.mixins.analyse import AnalyseMixin
from automata_extensions.fa.mixins.conversions import ConversionMixin


class ExtendedFA(AnalyseMixin, ConversionMixin, FA):
    """
    Common base class for all finite automata extensions (DFA, NFA, GNFA).

    Only algorithms that rely solely on states, transitions and
    initial_state belong here, so they become available on every
    subclass (ExtendedDFA, ExtendedNFA, ExtendedGNFA) at once.
    """
    pass