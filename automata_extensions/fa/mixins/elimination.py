"""State elimination on generalized NFAs (GNFA).

A GNFA is an automaton whose transitions are labelled by regular
expressions. It is normalized: it has a single initial state with no
incoming transition, and a single final state with no outgoing
transition. Eliminating the intermediate states one by one leaves a single
regular expression on the edge from the initial state to the final state.

Regular expression labels follow the syntax of automata-lib: symbols,
``*``, ``|``, ``?`` and parentheses. The label ``None`` means "no
transition" (the empty language) and the label ``""`` means the empty word.
"""


def _has_top_level_union(regex):
    """Return True if `regex` contains a '|' outside any parentheses."""
    depth = 0
    for char in regex:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == '|' and depth == 0:
            return True
    return False


def _group(regex):
    """Wrap `regex` in parentheses if it is a union (for concatenation)."""
    if _has_top_level_union(regex):
        return f"({regex})"
    return regex


def _star(regex):
    """Return the Kleene star of `regex` (None and the empty word give ε)."""
    if regex is None or regex == "":
        return ""
    if len(regex) == 1:
        return f"{regex}*"
    return f"({regex})*"


def _optional(regex):
    """Return `regex` made optional (the empty word added to its language)."""
    if len(regex) == 1:
        return f"{regex}?"
    return f"({regex})?"


def _eliminated_label(r_in, r_loop, r_out, r_direct):
    """
    Compute the new label of an edge when a state is eliminated.

    The eliminated state is entered with `r_in`, left with `r_out`, and
    loops on itself with `r_loop`. The edge already carried `r_direct`.
    The new label is ``r_in r_loop* r_out | r_direct``.
    """
    if r_in is None or r_out is None:
        return r_direct

    through = _group(r_in) + _star(r_loop) + _group(r_out)

    if r_direct is None:
        return through
    if through == "":
        return "" if r_direct == "" else _optional(r_direct)
    if r_direct == "":
        return _optional(through)
    return f"{through}|{r_direct}"


class EliminationMixin:
    """Mixin providing state elimination for an ExtendedGNFA."""

    def intermediate_states(self):
        """
        Return the states that can be eliminated.

        These are all the states except the initial state and the final
        state.

        Returns
        -------
        set
            The intermediate states.

        Complexity
        ----------
        O(|Q|)
        """
        return set(self.states) - {self.initial_state, self.final_state}

    def eliminate_state(self, state):
        """
        Eliminate an intermediate state of the GNFA.

        For every pair of states (p, q) such that p is not the final state
        and q is not the initial state, the new label of the edge p -> q is
        ``r(p, s) r(s, s)* r(s, q) | r(p, q)``, where s is the eliminated
        state. The language of the GNFA is unchanged. The original GNFA is
        never modified.

        Parameters
        ----------
        state : object
            The intermediate state to eliminate.

        Returns
        -------
        ExtendedGNFA
            A new GNFA with one state less.

        Raises
        ------
        ValueError
            If `state` is unknown, or is the initial or the final state.

        Complexity
        ----------
        O(|Q|^2) edges updated, each in O(size of the labels).

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*, section on converting a DFA to a
        regular expression by eliminating states.
        """
        if state not in self.states:
            raise ValueError(f"unknown state: {state!r}")
        if state in (self.initial_state, self.final_state):
            raise ValueError(
                "the initial state and the final state cannot be eliminated"
            )

        remaining = set(self.states) - {state}
        r_loop = self.transitions[state][state]

        new_transitions = {}
        for source in remaining - {self.final_state}:
            paths = {}
            for target in remaining - {self.initial_state}:
                paths[target] = _eliminated_label(
                    self.transitions[source][state],
                    r_loop,
                    self.transitions[state][target],
                    self.transitions[source][target],
                )
            new_transitions[source] = paths
        new_transitions[self.final_state] = {}

        return self.__class__(
            states=remaining,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_state=self.final_state,
        )