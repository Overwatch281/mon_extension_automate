"""Helpers shared by the tests of the regex package."""

import itertools

from automata_extensions.regex import Concat, Empty, Epsilon, Star, Symbol, Union


def all_words(alphabet, max_length):
    """Every word over `alphabet` of length 0 to `max_length`."""
    for length in range(max_length + 1):
        for letters in itertools.product(sorted(alphabet), repeat=length):
            yield ''.join(letters)


def reference_accepts(regex, word):
    """
    Decide whether `word` matches `regex`, straight from the definition.

    It does not use derivatives nor automata, so it can serve as an
    independent reference for them.
    """
    if isinstance(regex, Empty):
        return False
    if isinstance(regex, Epsilon):
        return word == ''
    if isinstance(regex, Symbol):
        return word == regex.char
    if isinstance(regex, Union):
        return any(reference_accepts(operand, word) for operand in regex.operands)
    if isinstance(regex, Concat):
        return _concat_accepts(regex.operands, word)
    if isinstance(regex, Star):
        if word == '':
            return True
        return any(
            reference_accepts(regex.inner, word[:i])
            and reference_accepts(regex, word[i:])
            for i in range(1, len(word) + 1)
        )
    raise TypeError(f"not a regular expression: {regex!r}")


def _concat_accepts(operands, word):
    """Decide whether `word` is a concatenation of words of the operands."""
    if not operands:
        return word == ''
    first, rest = operands[0], operands[1:]
    return any(
        reference_accepts(first, word[:i]) and _concat_accepts(rest, word[i:])
        for i in range(len(word) + 1)
    )