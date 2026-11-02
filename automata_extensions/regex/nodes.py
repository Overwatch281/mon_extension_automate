"""The nodes of the syntax tree of a regular expression.

The classes are immutable and hashable, and two expressions are equal when
their trees are equal. They are plain data: the derivatives and the
simplification are computed by `constructors.py`. To build expressions,
prefer the smart constructors `union`, `concat` and `star`, which keep the
trees in simplified form.
"""

from dataclasses import dataclass

from automata_extensions.regex.base import (
    EMPTY_CHARACTER,
    EPSILON_CHARACTER,
    Regex,
)

_RESERVED_CHARACTERS = frozenset("|*+?()") | {EPSILON_CHARACTER, EMPTY_CHARACTER}


@dataclass(frozen=True)
class Empty(Regex):
    """The empty language (no word at all)."""

    def nullable(self):
        return False

    def symbols(self):
        return set()

    def _precedence(self):
        return 4

    def __str__(self):
        return EMPTY_CHARACTER


@dataclass(frozen=True)
class Epsilon(Regex):
    """The language made of the empty word only."""

    def nullable(self):
        return True

    def symbols(self):
        return set()

    def _precedence(self):
        return 4

    def __str__(self):
        return EPSILON_CHARACTER


@dataclass(frozen=True)
class Symbol(Regex):
    """The language made of a single one-symbol word."""

    char: str

    def __post_init__(self):
        if (
            not isinstance(self.char, str)
            or len(self.char) != 1
            or self.char in _RESERVED_CHARACTERS
            or self.char.isspace()
        ):
            raise ValueError(f"invalid symbol: {self.char!r}")

    def nullable(self):
        return False

    def symbols(self):
        return {self.char}

    def _precedence(self):
        return 4

    def __str__(self):
        return self.char


@dataclass(frozen=True)
class Union(Regex):
    """The union of at least two expressions."""

    operands: tuple

    def nullable(self):
        return any(operand.nullable() for operand in self.operands)

    def symbols(self):
        return set().union(*(operand.symbols() for operand in self.operands))

    def _has_epsilon(self):
        return any(isinstance(operand, Epsilon) for operand in self.operands)

    def _precedence(self):
        # "r|ε" is written "r?", which binds like a postfix operator.
        return 3 if self._has_epsilon() else 1

    def __str__(self):
        rest = [op for op in self.operands if not isinstance(op, Epsilon)]
        if not self._has_epsilon():
            return "|".join(str(operand) for operand in rest)
        inner = rest[0] if len(rest) == 1 else Union(tuple(rest))
        text = str(inner)
        if inner._precedence() < 4:
            text = f"({text})"
        return text + "?"


@dataclass(frozen=True)
class Concat(Regex):
    """The concatenation of at least two expressions."""

    operands: tuple

    def nullable(self):
        return all(operand.nullable() for operand in self.operands)

    def symbols(self):
        return set().union(*(operand.symbols() for operand in self.operands))

    def _precedence(self):
        return 2

    def __str__(self):
        parts = []
        for operand in self.operands:
            text = str(operand)
            if operand._precedence() < 2:
                text = f"({text})"
            parts.append(text)
        return "".join(parts)


@dataclass(frozen=True)
class Star(Regex):
    """The Kleene star of an expression."""

    inner: Regex

    def nullable(self):
        return True

    def symbols(self):
        return self.inner.symbols()

    def _precedence(self):
        return 3

    def __str__(self):
        text = str(self.inner)
        if self.inner._precedence() < 4:
            text = f"({text})"
        return text + "*"