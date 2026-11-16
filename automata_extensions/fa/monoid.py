"""The syntactic monoid of a regular language (#62)."""

from collections import deque

from automata_extensions.fa.mixins.visualisation import _state_label


class SyntacticMonoid:
    """
    The syntactic monoid of the language of an automaton.

    Every word w induces a transformation of the states of the minimal
    complete DFA: it sends each state q to the state reached from q by
    reading w. Two words induce the same transformation exactly when they
    have the same behaviour in every context (xuy and xvy are both in the
    language, or both outside of it, for all words x and y). The set of
    these transformations, with the composition, is the syntactic monoid;
    the product of two elements is the element of the concatenation of
    their words.

    Each element is named by its shortest word (the smallest one in
    alphabetical order among the shortest); the identity is the empty
    word ``''``.

    Parameters
    ----------
    minimal : Automaton
        The minimal complete DFA of the language (see `from_automaton`).
    """

    def __init__(self, minimal):
        self._automaton = minimal
        self._order = sorted(minimal.states, key=_state_label)
        self._index = {state: i for i, state in enumerate(self._order)}
        self._letters = sorted(minimal.input_symbols)
        self._letter_maps = {
            letter: tuple(
                self._index[minimal.transitions[state][letter]] for state in self._order
            )
            for letter in self._letters
        }

        identity = tuple(range(len(self._order)))
        self._elements = {identity: ''}
        queue = deque([identity])
        while queue:
            current = queue.popleft()
            word = self._elements[current]
            for letter in self._letters:
                following = tuple(self._letter_maps[letter][i] for i in current)
                if following not in self._elements:
                    self._elements[following] = word + letter
                    queue.append(following)

    @classmethod
    def from_automaton(cls, automaton):
        """
        Build the syntactic monoid of the language of a DFA or an NFA.

        The automaton is determinized and minimized first.

        Complexity
        ----------
        O(|Q|^3 * |Sigma|) for the minimization, then at most |Q|^|Q|
        elements (usually far fewer), each computed in O(|Q|).

        References
        ----------
        Pin, J.-E. (2020). "Mathematical foundations of automata theory."
        """
        return cls(automaton.determinize().minimize())

    def _transformation(self, word):
        """Return the transformation induced by a word."""
        current = tuple(range(len(self._order)))
        for symbol in word:
            if symbol not in self._letter_maps:
                raise ValueError(f"symbol {symbol!r} is not in the input alphabet")
            current = tuple(self._letter_maps[symbol][i] for i in current)
        return current

    def __len__(self):
        return len(self._elements)

    @property
    def identity(self):
        """The identity element: the empty word."""
        return ''

    def elements(self):
        """
        Return the elements, each named by its shortest word.

        Returns
        -------
        list of str
            The shortest words of the elements, shortest first.
        """
        return list(self._elements.values())

    def element(self, word):
        """
        Return the element of a word, named by its shortest word.

        Raises
        ------
        ValueError
            If the word contains a symbol outside the input alphabet.
        """
        return self._elements[self._transformation(word)]

    def multiply(self, first, second):
        """
        Return the product of two elements (or of the elements of two
        words): the element of the concatenation.

        Returns
        -------
        str
            The shortest word of the product.
        """
        return self.element(first + second)

    def multiplication_table(self):
        """
        Return the multiplication table of the monoid.

        Returns
        -------
        dict
            Maps each pair (x, y) of elements to their product.
        """
        elements = self.elements()
        return {(x, y): self.multiply(x, y) for x in elements for y in elements}

    def accepting_elements(self):
        """
        Return the elements that belong to the language.

        An element is accepting if its words are in the language (all the
        words of an element are, or none is).

        Returns
        -------
        set of str
            The shortest words of the accepting elements.
        """
        start = self._index[self._automaton.initial_state]
        finals = {self._index[state] for state in self._automaton.final_states}
        return {
            word for transformation, word in self._elements.items()
            if transformation[start] in finals
        }

    def is_commutative(self):
        """
        Test whether xy = yx for all elements.

        The monoid is generated by the letters, so it is enough to check
        that every two letters commute.
        """
        for first in self._letters:
            for second in self._letters:
                a, b = self._letter_maps[first], self._letter_maps[second]
                if tuple(b[i] for i in a) != tuple(a[i] for i in b):
                    return False
        return True

    def is_aperiodic(self):
        """
        Test whether the monoid is aperiodic.

        It is aperiodic if every element x satisfies x^n = x^(n+1) for
        some n (no non-trivial group inside). By Schützenberger's theorem,
        this holds exactly when the language is star-free.
        """
        for transformation in self._elements:
            seen = {}
            power, exponent = transformation, 1
            while power not in seen:
                seen[power] = exponent
                power = tuple(transformation[i] for i in power)
                exponent += 1
            if exponent - seen[power] != 1:
                return False
        return True