"""Building automata from regular expressions.

Two constructions: Thompson's construction (an NFA with epsilon
transitions) and the derivative automaton of Brzozowski (a complete DFA).
"""

from collections import deque

from automata_extensions.regex.nodes import (
    Concat,
    Empty,
    Epsilon,
    Star,
    Symbol,
    Union,
)


def _resolve_alphabet(regex, alphabet):
    """Return the alphabet to use, checking that it covers the expression."""
    symbols = regex.symbols()
    if alphabet is None:
        return symbols
    alphabet = set(alphabet)
    missing = symbols - alphabet
    if missing:
        raise ValueError(f"the alphabet misses the symbols {sorted(missing)}")
    return alphabet


def thompson_nfa(regex, alphabet=None):
    """
    Build the Thompson NFA of an expression.

    Each operator is turned into a small automaton with one entry state and
    one exit state, glued with epsilon transitions:

    - a symbol: entry --a--> exit;
    - a union: a new entry with epsilon transitions to the entries of the
      operands, and the exits of the operands going to a new exit;
    - a concatenation: the exit of each operand goes to the entry of the
      next one;
    - a star: a new entry and a new exit, an epsilon transition to skip
      the operand, and one to repeat it.

    Parameters
    ----------
    regex : Regex
        The expression.
    alphabet : set of str, optional
        The input alphabet (by default, the symbols of the expression).

    Returns
    -------
    ExtendedNFA
        The NFA, whose states are named q0, q1, and so on.

    Raises
    ------
    ValueError
        If `alphabet` misses some symbol of the expression.

    Complexity
    ----------
    O(size of the expression)

    References
    ----------
    Thompson, K. (1968). "Regular expression search algorithm."
    """
    from automata_extensions.fa.nfa import ExtendedNFA

    alphabet = _resolve_alphabet(regex, alphabet)
    transitions = {}

    def new_state():
        name = f"q{len(transitions)}"
        transitions[name] = {}
        return name

    def link(source, symbol, target):
        transitions[source].setdefault(symbol, set()).add(target)

    def build(node):
        """Return the (entry, exit) pair of states for a sub-expression."""
        if isinstance(node, Empty):
            return new_state(), new_state()

        if isinstance(node, Epsilon):
            entry, exit_ = new_state(), new_state()
            link(entry, '', exit_)
            return entry, exit_

        if isinstance(node, Symbol):
            entry, exit_ = new_state(), new_state()
            link(entry, node.char, exit_)
            return entry, exit_

        if isinstance(node, Union):
            entry = new_state()
            fragments = [build(operand) for operand in node.operands]
            exit_ = new_state()
            for fragment_entry, fragment_exit in fragments:
                link(entry, '', fragment_entry)
                link(fragment_exit, '', exit_)
            return entry, exit_

        if isinstance(node, Concat):
            fragments = [build(operand) for operand in node.operands]
            for (_, previous_exit), (next_entry, _) in zip(fragments, fragments[1:]):
                link(previous_exit, '', next_entry)
            return fragments[0][0], fragments[-1][1]

        if isinstance(node, Star):
            inner_entry, inner_exit = build(node.inner)
            entry, exit_ = new_state(), new_state()
            link(entry, '', inner_entry)
            link(entry, '', exit_)
            link(inner_exit, '', inner_entry)
            link(inner_exit, '', exit_)
            return entry, exit_

        raise TypeError(f"not a regular expression: {node!r}")

    initial_state, final_state = build(regex)

    return ExtendedNFA(
        states=set(transitions),
        input_symbols=alphabet,
        transitions=transitions,
        initial_state=initial_state,
        final_states={final_state},
    )


def derivative_dfa(regex, alphabet=None):
    """
    Build the derivative automaton of an expression.

    The initial state is the expression itself. From a state r, the
    transition by a symbol a leads to the derivative of r by a. A state is
    final if it accepts the empty word. Since the smart constructors
    identify the expressions that differ only by the associativity,
    commutativity and idempotence of the union, there are finitely many
    states and the construction ends.

    Parameters
    ----------
    regex : Regex
        The expression.
    alphabet : set of str, optional
        The input alphabet (by default, the symbols of the expression).

    Returns
    -------
    ExtendedDFA
        A complete DFA whose states are expressions.

    Raises
    ------
    ValueError
        If `alphabet` misses some symbol of the expression.

    Complexity
    ----------
    Exponential in the worst case (number of distinct derivatives).

    References
    ----------
    Brzozowski, J. (1964). "Derivatives of regular expressions."
    """
    from automata_extensions.fa.dfa import ExtendedDFA

    alphabet = _resolve_alphabet(regex, alphabet)

    start = regex.simplify()
    visited = {start}
    queue = deque([start])
    transitions = {}

    while queue:
        current = queue.popleft()
        transitions[current] = {}
        for symbol in sorted(alphabet):
            target = current.derivative(symbol)
            transitions[current][symbol] = target
            if target not in visited:
                visited.add(target)
                queue.append(target)

    return ExtendedDFA(
        states=visited,
        input_symbols=alphabet,
        transitions=transitions,
        initial_state=start,
        final_states={state for state in visited if state.nullable()},
    )