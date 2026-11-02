"""Smart constructors, derivatives and simplification of expressions.

The functions `union`, `concat` and `star` build expressions while
applying simplification rules (union is associative, commutative and
idempotent, the empty word is neutral for concatenation, and so on).
Thanks to these rules the set of derivatives of an expression is finite,
which makes the derivative automaton possible.
"""

from automata_extensions.regex.nodes import (
    Concat,
    Empty,
    Epsilon,
    Star,
    Symbol,
    Union,
)


def empty():
    """Return the expression of the empty language."""
    return Empty()


def epsilon():
    """Return the expression of the empty word."""
    return Epsilon()


def symbol(char):
    """Return the expression made of a single symbol."""
    return Symbol(char)


def union(*operands):
    """
    Build the union of expressions, in simplified form.

    Nested unions are flattened, the empty language is dropped, duplicates
    are removed, the operands are sorted (so that r|s and s|r give the same
    tree), and the empty word is dropped when another operand already
    accepts it.
    """
    flat = []
    for operand in operands:
        if isinstance(operand, Union):
            flat.extend(operand.operands)
        else:
            flat.append(operand)

    unique = sorted(
        {operand for operand in flat if not isinstance(operand, Empty)},
        key=str,
    )

    has_epsilon = any(isinstance(operand, Epsilon) for operand in unique)
    if has_epsilon and any(
        operand.nullable() and not isinstance(operand, Epsilon)
        for operand in unique
    ):
        unique = [op for op in unique if not isinstance(op, Epsilon)]

    if not unique:
        return Empty()
    if len(unique) == 1:
        return unique[0]
    return Union(tuple(unique))


def concat(*operands):
    """
    Build the concatenation of expressions, in simplified form.

    Nested concatenations are flattened, the empty word is dropped, and
    the result is the empty language if one operand is the empty language.
    """
    flat = []
    for operand in operands:
        if isinstance(operand, Concat):
            flat.extend(operand.operands)
        else:
            flat.append(operand)

    if any(isinstance(operand, Empty) for operand in flat):
        return Empty()

    flat = [operand for operand in flat if not isinstance(operand, Epsilon)]
    if not flat:
        return Epsilon()
    if len(flat) == 1:
        return flat[0]
    return Concat(tuple(flat))


def star(operand):
    """
    Build the Kleene star of an expression, in simplified form.

    The star of the empty language or of the empty word is the empty word,
    the star of a star is the star, and the empty word inside a starred
    union is useless.
    """
    if isinstance(operand, (Empty, Epsilon)):
        return Epsilon()
    if isinstance(operand, Star):
        return operand
    if isinstance(operand, Union) and operand._has_epsilon():
        return star(union(*(op for op in operand.operands if not isinstance(op, Epsilon))))
    return Star(operand)


def derivative_of(regex, symbol):
    """
    Compute the derivative of an expression by a symbol.

    See `Regex.derivative` for the rules.
    """
    if isinstance(regex, (Empty, Epsilon)):
        return Empty()

    if isinstance(regex, Symbol):
        return Epsilon() if regex.char == symbol else Empty()

    if isinstance(regex, Union):
        return union(*(derivative_of(op, symbol) for op in regex.operands))

    if isinstance(regex, Concat):
        first = regex.operands[0]
        rest = concat(*regex.operands[1:])
        result = concat(derivative_of(first, symbol), rest)
        if first.nullable():
            result = union(result, derivative_of(rest, symbol))
        return result

    if isinstance(regex, Star):
        return concat(derivative_of(regex.inner, symbol), regex)

    raise TypeError(f"not a regular expression: {regex!r}")


def simplify_of(regex):
    """
    Rebuild an expression with the smart constructors.

    See `Regex.simplify`.
    """
    if isinstance(regex, Union):
        return union(*(simplify_of(op) for op in regex.operands))
    if isinstance(regex, Concat):
        return concat(*(simplify_of(op) for op in regex.operands))
    if isinstance(regex, Star):
        return star(simplify_of(regex.inner))
    return regex