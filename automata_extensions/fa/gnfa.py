from automata.fa.gnfa import GNFA

from automata_extensions.fa.mixins.elimination import EliminationMixin
from automata_extensions.fa.mixins.export import ExportMixin
from automata_extensions.fa.mixins.visualisation import VisualisationMixin


class ExtendedGNFA(EliminationMixin, ExportMixin, VisualisationMixin, GNFA):
    """
    GNFA augmented with state elimination and DOT export.

    Unlike ExtendedDFA and ExtendedNFA, it does not derive from ExtendedFA:
    its transitions are labelled by regular expressions between states
    (not by input symbols), so the algorithms written for symbol-labelled
    transitions do not apply to it.
    """

    def _dot_edges(self):
        """Return the edges to draw: every transition with a regex label."""
        return [
            (source, target, label)
            for source, target, label in self.iter_transitions()
            if label is not None
        ]