"""Reading regular expressions written as text.

Grammar (from the weakest to the strongest binding)::

    union   := concat ('|' concat)*
    concat  := postfix*
    postfix := atom ('*' | '+' | '?')*
    atom    := symbol | 'ε' | '∅' | '(' union ')'

An empty text, or an empty pair of parentheses, is the empty word.
Spaces are ignored.
"""

from automata_extensions.regex.base import EMPTY_CHARACTER, EPSILON_CHARACTER
from automata_extensions.regex.constructors import (
    concat,
    empty,
    epsilon,
    star,
    symbol,
    union,
)


class _Parser:
    """Recursive descent parser over a text."""

    def __init__(self, text):
        self.text = text
        self.position = 0

    def peek(self):
        """Return the next character that is not a space, or None."""
        while self.position < len(self.text) and self.text[self.position].isspace():
            self.position += 1
        if self.position < len(self.text):
            return self.text[self.position]
        return None

    def advance(self):
        """Consume and return the next character."""
        char = self.peek()
        self.position += 1
        return char

    def parse_union(self):
        terms = [self.parse_concat()]
        while self.peek() == '|':
            self.advance()
            terms.append(self.parse_concat())
        return union(*terms)

    def parse_concat(self):
        factors = []
        while self.peek() not in (None, '|', ')'):
            factors.append(self.parse_postfix())
        return concat(*factors)

    def parse_postfix(self):
        node = self.parse_atom()
        while self.peek() in ('*', '+', '?'):
            operator = self.advance()
            if operator == '*':
                node = star(node)
            elif operator == '+':
                node = concat(node, star(node))
            else:
                node = union(epsilon(), node)
        return node

    def parse_atom(self):
        char = self.peek()
        if char == '(':
            self.advance()
            node = self.parse_union()
            if self.peek() != ')':
                raise ValueError("missing closing parenthesis")
            self.advance()
            return node
        if char in ('*', '+', '?'):
            raise ValueError(
                f"nothing to repeat before {char!r} at position {self.position}"
            )
        self.advance()
        if char == EPSILON_CHARACTER:
            return epsilon()
        if char == EMPTY_CHARACTER:
            return empty()
        return symbol(char)


def parse_regex(text):
    """
    Read a regular expression written as text.

    Parameters
    ----------
    text : str
        The expression, for example ``"(a|b)*abb"``.

    Returns
    -------
    Regex
        The expression, in simplified form.

    Raises
    ------
    ValueError
        If the text is malformed (unbalanced parentheses, an operator
        with nothing to repeat, a reserved character used as a symbol).

    Complexity
    ----------
    O(length of the text)
    """
    parser = _Parser(text)
    result = parser.parse_union()
    if parser.peek() is not None:
        raise ValueError(
            f"unexpected {parser.peek()!r} at position {parser.position}"
        )
    return result