"""Systems of regular equations and Arden's lemma.

An automaton gives a system of equations, one for each state q::

    X_q = a1 X_p1 | a2 X_p2 | ... | (epsilon if q is final)

where X_q is the language of the words accepted starting from q, and
a_i X_p_i comes from the transition q --a_i--> p_i. Solving the system
with Arden's lemma gives a regular expression for each state.
"""

from automata_extensions.regex.constructors import (
    concat,
    empty,
    epsilon,
    star,
    symbol,
    union,
)
from automata_extensions.regex.nodes import Empty


def arden(coefficient, constant):
    """
    Solve the equation X = A X | B with Arden's lemma (#57).

    The smallest solution is X = A* B. (When A does not contain the empty
    word, it is the only solution.)

    Parameters
    ----------
    coefficient : Regex
        The expression A.
    constant : Regex
        The expression B.

    Returns
    -------
    Regex
        The expression A* B.

    Complexity
    ----------
    O(size of the expressions)

    References
    ----------
    Arden, D. N. (1961). "Delayed-logic and finite-state machines."
    """
    return concat(star(coefficient), constant)


class EquationSystem:
    """
    A system of right-linear equations over regular expressions (#58).

    The equation of the variable X_i is::

        X_i = c_i1 X_1 | c_i2 X_2 | ... | b_i

    `coefficients[i][j]` is the expression c_ij (missing when it is the
    empty language) and `constants[i]` is the expression b_i.
    """

    def __init__(self, coefficients, constants):
        self.coefficients = {
            variable: dict(row) for variable, row in coefficients.items()
        }
        self.constants = dict(constants)

    @classmethod
    def from_automaton(cls, automaton):
        """
        Build the system of equations of a DFA or an NFA.

        There is one variable per state. A transition q --a--> p adds the
        term ``a X_p`` to the equation of q (an epsilon transition adds
        ``X_p``), and a final state q gets the constant epsilon.

        Parameters
        ----------
        automaton : Automaton
            An extended DFA or NFA.

        Returns
        -------
        EquationSystem
            The system whose variables are the states.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        coefficients = {}
        constants = {}
        for state in automaton.states:
            row = {}
            for input_symbol, destination in automaton.transitions.get(state, {}).items():
                term = epsilon() if input_symbol == '' else symbol(input_symbol)
                for target in automaton._destination_states(destination):
                    row[target] = union(row.get(target, empty()), term)
            coefficients[state] = row
            constants[state] = epsilon() if state in automaton.final_states else empty()
        return cls(coefficients, constants)

    def solve(self, order=None):
        """
        Solve the system, variable by variable, with Arden's lemma.

        For each variable X_i in turn: the self-reference is removed with
        Arden's lemma (X_i = A X_i | R becomes X_i = A* R), then X_i is
        replaced by its expression in all the other equations. When every
        variable has been treated, each equation is only a constant: this
        is the solution. The system itself is never modified.

        Parameters
        ----------
        order : iterable, optional
            The order in which the variables are treated (all of them,
            once). By default, sorted by name.

        Returns
        -------
        dict
            For each variable, a regular expression.

        Raises
        ------
        ValueError
            If `order` does not list every variable exactly once.

        Complexity
        ----------
        O(n^3) operations on expressions, for n variables.

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        if order is None:
            from automata_extensions.fa.mixins.visualisation import _state_label

            variables = sorted(self.coefficients, key=_state_label)
        else:
            variables = list(order)
            if len(variables) != len(self.coefficients) or set(variables) != set(self.coefficients):
                raise ValueError("the order must list every variable exactly once")

        coefficients = {v: dict(row) for v, row in self.coefficients.items()}
        constants = dict(self.constants)

        for variable in variables:
            # Arden: X = A X | R  becomes  X = A* R
            loop = coefficients[variable].pop(variable, empty())
            factor = star(loop)
            coefficients[variable] = {
                other: concat(factor, coefficient)
                for other, coefficient in coefficients[variable].items()
            }
            constants[variable] = concat(factor, constants[variable])

            # Replace X in the other equations by its expression.
            for other_variable, row in coefficients.items():
                if other_variable == variable or variable not in row:
                    continue
                multiplier = row.pop(variable)
                if isinstance(multiplier, Empty):
                    continue
                for other, coefficient in coefficients[variable].items():
                    row[other] = union(
                        row.get(other, empty()), concat(multiplier, coefficient)
                    )
                constants[other_variable] = union(
                    constants[other_variable],
                    concat(multiplier, constants[variable]),
                )

        return constants

    def __str__(self):
        from automata_extensions.fa.mixins.visualisation import _state_label

        lines = []
        for variable in sorted(self.coefficients, key=_state_label):
            terms = []
            row = self.coefficients[variable]
            for other in sorted(row, key=_state_label):
                coefficient = row[other]
                if isinstance(coefficient, Empty):
                    continue
                text = str(coefficient)
                if coefficient._precedence() < 2:
                    text = f"({text})"
                terms.append(f"{text}X_{_state_label(other)}")
            if not isinstance(self.constants[variable], Empty):
                terms.append(str(self.constants[variable]))
            lines.append(f"X_{_state_label(variable)} = {' | '.join(terms) if terms else '∅'}")
        return "\n".join(lines)