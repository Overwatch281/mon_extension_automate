"""The base class of the regular expressions.

An expression is an immutable syntax tree built from the empty language,
the empty word, symbols, union, concatenation and Kleene star (see
`nodes.py`). The base class holds the operations shared by all the
nodes: derivatives, matching, and conversions to automata.

Textual syntax (see `parse_regex`): symbols, ``|`` for the union, ``*``,
``+`` and ``?`` as postfix operators, parentheses, ``ε`` for the empty word
and ``∅`` for the empty language.
"""

EPSILON_CHARACTER = "ε"
EMPTY_CHARACTER = "∅"


class Regex:
    """Base class of the regular expressions."""

    def nullable(self):
        """
        Test whether the empty word belongs to the language.

        Returns
        -------
        bool
            True if the expression accepts the empty word.

        Complexity
        ----------
        O(size of the expression)
        """
        raise NotImplementedError

    def symbols(self):
        """
        Return the set of symbols that appear in the expression.

        Complexity
        ----------
        O(size of the expression)
        """
        raise NotImplementedError

    def _precedence(self):
        """Binding strength used to place parentheses when printing."""
        raise NotImplementedError

    def derivative(self, symbol):
        """
        Compute the Brzozowski derivative with respect to a symbol.

        The derivative of a language L by a symbol a is the set of words
        w such that aw belongs to L. For an expression r it is computed
        recursively:

        - d_a(empty) = d_a(epsilon) = empty
        - d_a(b) = epsilon if a = b, empty otherwise
        - d_a(r | s) = d_a(r) | d_a(s)
        - d_a(r s) = d_a(r) s | d_a(s) if r is nullable, d_a(r) s otherwise
        - d_a(r*) = d_a(r) r*

        The result is simplified by the smart constructors.

        Parameters
        ----------
        symbol : str
            A single symbol.

        Returns
        -------
        Regex
            An expression for the derivative.

        Complexity
        ----------
        O(size of the expression)

        References
        ----------
        Brzozowski, J. (1964). "Derivatives of regular expressions."
        """
        from automata_extensions.regex.constructors import derivative_of

        return derivative_of(self, symbol)

    def simplify(self):
        """
        Return the expression rebuilt with the smart constructors.

        Useful for a tree assembled by hand with the raw node classes. A
        tree built with `union`, `concat`, `star` or `parse_regex` is
        already simplified.

        Complexity
        ----------
        O(size of the expression)
        """
        from automata_extensions.regex.constructors import simplify_of

        return simplify_of(self)

    def derivative_word(self, word):
        """
        Compute the derivative with respect to a word.

        This is the derivative by the first symbol, then by the second,
        and so on.

        Parameters
        ----------
        word : str
            The word to derive by.

        Returns
        -------
        Regex
            An expression for the set of words w such that (word)w
            belongs to the language.

        Complexity
        ----------
        O(|word| * size of the expression)
        """
        result = self
        for symbol in word:
            result = result.derivative(symbol)
        return result

    def accepts(self, word):
        """
        Test whether a word belongs to the language of the expression.

        A word belongs to the language if and only if the derivative by
        this word accepts the empty word.

        Parameters
        ----------
        word : str
            The word to test.

        Returns
        -------
        bool
            True if the word matches the expression.

        Complexity
        ----------
        O(|word| * size of the expression)
        """
        return self.derivative_word(word).nullable()

    def to_nfa(self, alphabet=None):
        """
        Convert the expression to an NFA by Thompson's construction (#51).

        Parameters
        ----------
        alphabet : set of str, optional
            The input alphabet. By default, the symbols of the expression.

        Returns
        -------
        ExtendedNFA
            An NFA with epsilon transitions, with one initial state, one
            final state, and at most twice as many states as the size of
            the expression.

        Raises
        ------
        ValueError
            If `alphabet` misses some symbol of the expression.

        Complexity
        ----------
        O(size of the expression)
        """
        from automata_extensions.regex.construction import thompson_nfa

        return thompson_nfa(self, alphabet)

    def to_dfa(self, alphabet=None):
        """
        Convert the expression directly to a complete DFA.

        This is the derivative automaton: the states are the distinct
        derivatives of the expression, a state is final if it accepts the
        empty word, and the transition by a symbol leads to the derivative
        by this symbol.

        Parameters
        ----------
        alphabet : set of str, optional
            The input alphabet. By default, the symbols of the expression.

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
        from automata_extensions.regex.construction import derivative_dfa

        return derivative_dfa(self, alphabet)

    @staticmethod
    def parse(text):
        """Read an expression written as text (see `parse_regex`)."""
        from automata_extensions.regex.parser import parse_regex

        return parse_regex(text)