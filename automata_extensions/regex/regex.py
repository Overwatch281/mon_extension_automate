"""Public names of the regular expression package (facade).

The code is split in `base.py` (the base class), `nodes.py` (the syntax
tree nodes), `constructors.py` (smart constructors, derivatives,
simplification), `parser.py` (reading text) and `construction.py`
(automata built from expressions).
"""

from automata_extensions.regex.base import (
    EMPTY_CHARACTER,
    EPSILON_CHARACTER,
    Regex,
)
from automata_extensions.regex.constructors import (
    concat,
    empty,
    epsilon,
    star,
    symbol,
    union,
)
from automata_extensions.regex.nodes import (
    Concat,
    Empty,
    Epsilon,
    Star,
    Symbol,
    Union,
)

__all__ = [
    "EMPTY_CHARACTER", "EPSILON_CHARACTER", "Regex",
    "Empty", "Epsilon", "Symbol", "Union", "Concat", "Star",
    "empty", "epsilon", "symbol", "union", "concat", "star",
]