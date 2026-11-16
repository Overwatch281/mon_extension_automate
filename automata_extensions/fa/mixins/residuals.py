"""Myhill-Nerode classes and the canonical residual automaton (FA level).

These algorithms rely on helpers provided by the other mixins of
ExtendedFA (determinize and minimize, left_quotient, language_subset,
union, is_empty, _fresh_state).
"""

from collections import deque, namedtuple
from functools import reduce

NerodeClass = namedtuple("NerodeClass", ["representative", "accepting", "quotient"])


class ResidualMixin:
    """Mixin providing the Myhill-Nerode classes and the residual automaton."""

    def _nerode_data(self):
        """
        Return the minimal complete DFA and a representative word per state.

        The representative of a state is the shortest word reaching it
        from the initial state (the smallest one in alphabetical order
        among the shortest), found by a breadth-first search.

        Complexity
        ----------
        O(|Q| * |Sigma|) after the minimization.
        """
        minimal = self.determinize().minimize()
        representative = {minimal.initial_state: ''}
        queue = deque([minimal.initial_state])
        while queue:
            state = queue.popleft()
            for symbol in sorted(minimal.input_symbols):
                target = minimal.transitions[state][symbol]
                if target not in representative:
                    representative[target] = representative[state] + symbol
                    queue.append(target)
        return minimal, representative

    def myhill_nerode_classes(self):
        """
        Compute the Myhill-Nerode classes of the language (#59).

        Two words u and v are equivalent if, for every word w, uw belongs
        to the language exactly when vw does, that is, if they have the
        same left quotient. The classes are in bijection with the states
        of the minimal complete DFA, and their number is its number of
        states. Each class is described by its shortest word, by whether
        its words belong to the language, and by an automaton for the
        quotient u^-1 L shared by its words.

        Returns
        -------
        list of NerodeClass
            One entry per class, ordered by representative (shortest
            first). Each entry has three fields: `representative` (a
            string), `accepting` (bool, whether the representative is in
            the language) and `quotient` (a DFA recognizing the words w
            such that representative + w is in the language).

        Complexity
        ----------
        O(|Q|^3 * |Sigma|) for the minimization, then one quotient per
        class.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        minimal, representative = self._nerode_data()
        ordered = sorted(representative.items(), key=lambda item: (len(item[1]), item[1]))
        return [
            NerodeClass(
                word,
                state in minimal.final_states,
                minimal.left_quotient(word),
            )
            for state, word in ordered
        ]

    def nerode_equivalent(self, first, second):
        """
        Test whether two words are in the same Myhill-Nerode class.

        Parameters
        ----------
        first, second : str
            The two words.

        Returns
        -------
        bool
            True if, for every word w, `first + w` and `second + w` are
            either both in the language or both outside of it.

        Raises
        ------
        ValueError
            If a word contains a symbol outside the input alphabet.

        Complexity
        ----------
        O(|Q|^3 * |Sigma|) for the minimization, then linear in the
        length of the words.
        """
        minimal = self.determinize().minimize()
        return minimal.trace(first)[-1] == minimal.trace(second)[-1]

    def residual_automaton(self):
        """
        Build the canonical residual automaton of the language (#60).

        A residual (left quotient) is prime if it is not the union of the
        residuals that it strictly contains. The canonical residual
        automaton has one state per prime residual, named by the shortest
        word of the class (``ε`` for the empty word):

        - there is a transition on a from a prime residual R to every
          prime residual included in a^-1 R;
        - the initial states are the prime residuals included in the
          language;
        - the final states are the prime residuals containing the empty
          word.

        Each state recognizes exactly its own residual. This NFA can be
        much smaller than the minimal DFA. Since an NFA has a single
        initial state, several initial residuals are reached from a new
        initial state ``init`` by epsilon transitions. The empty language
        gives a single non-final state.

        Returns
        -------
        ExtendedNFA
            The residual automaton.

        Complexity
        ----------
        Several language inclusions between the residuals; exponential
        time in the worst case because of the unions.

        References
        ----------
        Denis, F., Lemay, A., Terlutte, A. (2002). "Residual finite state
        automata."
        """
        from automata_extensions.fa.nfa import ExtendedNFA

        minimal, representative = self._nerode_data()
        states = list(representative)
        quotient = {
            state: minimal.left_quotient(representative[state]) for state in states
        }

        inclusion_cache = {}

        def included(first, second):
            """Whether the residual of `first` is included in that of `second`."""
            key = (first, second)
            if key not in inclusion_cache:
                inclusion_cache[key] = quotient[first].language_subset(quotient[second])
            return inclusion_cache[key]

        def is_prime(state):
            below = [other for other in states if other != state and included(other, state)]
            if not below:
                return not quotient[state].is_empty()
            union = reduce(
                lambda left, right: left.union(right),
                (quotient[other] for other in below),
            )
            return not quotient[state].language_subset(union)

        primes = [state for state in states if is_prime(state)]

        def name(state):
            return representative[state] or "ε"

        if not primes:
            empty_state = self._fresh_state("init")
            return ExtendedNFA(
                states={empty_state},
                input_symbols=self.input_symbols,
                transitions={empty_state: {}},
                initial_state=empty_state,
                final_states=set(),
            )

        transitions = {name(state): {} for state in primes}
        for state in primes:
            for symbol in sorted(minimal.input_symbols):
                target = minimal.transitions[state][symbol]
                successors = {name(other) for other in primes if included(other, target)}
                if successors:
                    transitions[name(state)][symbol] = successors

        initial_primes = [state for state in primes if included(state, minimal.initial_state)]
        if len(initial_primes) == 1:
            initial_state = name(initial_primes[0])
        else:
            used = set(transitions)
            initial_state, counter = "init", 0
            while initial_state in used:
                counter += 1
                initial_state = f"init_{counter}"
            transitions[initial_state] = {'': {name(state) for state in initial_primes}}

        return ExtendedNFA(
            states=set(transitions),
            input_symbols=minimal.input_symbols,
            transitions=transitions,
            initial_state=initial_state,
            final_states={name(state) for state in primes if state in minimal.final_states},
        )