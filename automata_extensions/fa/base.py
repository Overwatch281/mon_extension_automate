"""Common base class combining all FA-level mixins."""

from automata.fa.fa import FA

from automata_extensions.fa.mixins.analyse import AnalyseMixin
from automata_extensions.fa.mixins.automaton_conversions import AutomatonConversionMixin
from automata_extensions.fa.mixins.conversions import ConversionMixin
from automata_extensions.fa.mixins.cycles import CyclesMixin
from automata_extensions.fa.mixins.determinisation import DeterminisationMixin
from automata_extensions.fa.mixins.export import ExportMixin
from automata_extensions.fa.mixins.language_operations import LanguageOperationsMixin
from automata_extensions.fa.mixins.languages import LanguageMixin
from automata_extensions.fa.mixins.minimisation import MinimisationMixin
from automata_extensions.fa.mixins.operations import OperationsMixin
from automata_extensions.fa.mixins.products import ProductMixin
from automata_extensions.fa.mixins.quotients import QuotientMixin
from automata_extensions.fa.mixins.regex_conversions import RegexConversionMixin
from automata_extensions.fa.mixins.relations import RelationsMixin
from automata_extensions.fa.mixins.simulation import SimulationMixin
from automata_extensions.fa.mixins.transformations import TransformationMixin
from automata_extensions.fa.mixins.traversals import TraversalMixin
from automata_extensions.fa.mixins.visualisation import VisualisationMixin


class ExtendedFA(
    AnalyseMixin,
    AutomatonConversionMixin,
    ConversionMixin,
    CyclesMixin,
    DeterminisationMixin,
    ExportMixin,
    LanguageMixin,
    LanguageOperationsMixin,
    MinimisationMixin,
    OperationsMixin,
    ProductMixin,
    QuotientMixin,
    RegexConversionMixin,
    RelationsMixin,
    SimulationMixin,
    TransformationMixin,
    TraversalMixin,
    VisualisationMixin,
    FA,
):
    """
    Common base class for the finite automata extensions (DFA and NFA).

    Only algorithms that rely solely on states, transitions and
    initial_state belong here, so they become available on both
    ExtendedDFA and ExtendedNFA at once. The generalized NFA has its own
    class (ExtendedGNFA), because its transitions have another format.
    """
    pass