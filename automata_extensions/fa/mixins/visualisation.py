"""Visualisation of automata: export to the Graphviz DOT language.

The DOT text is produced in pure Python, so no external program is needed
to obtain it. State labels are built so that the output is deterministic
(the same automaton always gives the same text).
"""

EPSILON = "ε"


def _state_label(state):
    """
    Return a readable and deterministic text for a state.

    Sets of states (after a determinization) are shown as ``{q0,q1}`` with
    their elements sorted, the empty set as ``∅``, and tuples (after a
    product) as ``(p,q)``.
    """
    if isinstance(state, (set, frozenset)):
        if not state:
            return "∅"
        return "{" + ",".join(sorted(_state_label(item) for item in state)) + "}"
    if isinstance(state, tuple):
        return "(" + ",".join(_state_label(item) for item in state) + ")"
    return str(state)


def _dot_escape(text):
    """Escape a text so that it can be put between double quotes in DOT."""
    return (
        text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    )


class VisualisationMixin:
    """Mixin providing the DOT description of an automaton."""

    def _dot_edges(self):
        """
        Return the edges to draw, as (source, target, label) triples.

        For a DFA or an NFA, the label is the input symbol (the empty
        string for an epsilon transition). A subclass whose transitions
        have another format overrides this method.
        """
        edges = []
        for state in self.states:
            for symbol, destination in self.transitions.get(state, {}).items():
                for target in self._destination_states(destination):
                    edges.append((state, target, symbol))
        return edges

    def dot(self):
        """
        Return the Graphviz DOT description of the automaton.

        The initial state is marked by an arrow coming from nowhere, the
        final states are drawn with a double circle, and the symbols of
        parallel transitions are grouped on a single edge (``a,b``). The
        empty word is drawn as ε.

        Returns
        -------
        str
            The text of a DOT graph, ready to be given to Graphviz.

        Complexity
        ----------
        O(|Q| log |Q| + |E| log |E|)

        References
        ----------
        Graphviz documentation, The DOT Language.
        """
        labels = {state: _state_label(state) for state in self.states}
        ordered = sorted(self.states, key=lambda state: labels[state])
        ids = {state: f"n{index}" for index, state in enumerate(ordered)}

        grouped = {}
        for source, target, label in self._dot_edges():
            text = EPSILON if label == "" else str(label)
            grouped.setdefault((source, target), set()).add(text)

        lines = [
            "digraph automaton {",
            "    rankdir=LR;",
            "    node [shape=circle];",
            '    __start [shape=point, style=invis, label=""];',
            f"    __start -> {ids[self.initial_state]};",
        ]

        for state in ordered:
            attributes = f'label="{_dot_escape(labels[state])}"'
            if state in self.final_states:
                attributes += ", shape=doublecircle"
            lines.append(f"    {ids[state]} [{attributes}];")

        edge_keys = sorted(
            grouped, key=lambda pair: (labels[pair[0]], labels[pair[1]])
        )
        for source, target in edge_keys:
            texts = sorted(text for text in grouped[(source, target)] if text != EPSILON)
            if EPSILON in grouped[(source, target)]:
                texts.append(EPSILON)
            label = _dot_escape(",".join(texts))
            lines.append(f'    {ids[source]} -> {ids[target]} [label="{label}"];')

        lines.append("}")
        return "\n".join(lines) + "\n"