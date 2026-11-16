"""Display and export of derivation trees (text, DOT, SVG, PDF, PNG)."""

from pathlib import Path

from automata_extensions.fa.graphviz_tools import run_graphviz
from automata_extensions.fa.mixins.visualisation import _dot_escape

EPSILON = "ε"


class TreeExportMixin:
    """Mixin providing the display and the export of a ParseTree."""

    def __str__(self):
        if self.is_terminal:
            return self.symbol
        inside = " ".join(str(child) for child in self.children) or EPSILON
        return f"{self.symbol}({inside})"

    def to_dot(self):
        """
        Return the Graphviz DOT description of the tree.

        Nonterminals are ellipses, terminals are boxes, and a nonterminal
        rewritten into the empty word gets an epsilon leaf. The children
        are listed from left to right.

        Returns
        -------
        str
            The text of a DOT graph.

        Complexity
        ----------
        O(size of the tree)
        """
        lines = ["digraph tree {"]
        counter = [0]

        def new_identifier():
            identifier = f"n{counter[0]}"
            counter[0] += 1
            return identifier

        def visit(node):
            identifier = new_identifier()
            attributes = f'label="{_dot_escape(node.symbol)}"'
            if node.is_terminal:
                attributes += ", shape=box"
            lines.append(f"    {identifier} [{attributes}];")
            if not node.is_terminal and not node.children:
                leaf = new_identifier()
                lines.append(f'    {leaf} [label="{EPSILON}", shape=plaintext];')
                lines.append(f"    {identifier} -> {leaf};")
            for child in node.children:
                child_identifier = visit(child)
                lines.append(f"    {identifier} -> {child_identifier};")
            return identifier

        visit(self)
        lines.append("}")
        return "\n".join(lines) + "\n"

    def to_svg(self):
        """
        Return the drawing of the tree as SVG text (needs Graphviz).

        Raises
        ------
        RuntimeError
            If Graphviz is not installed.
        """
        return run_graphviz(self.to_dot(), "svg").decode("utf-8")

    def save(self, path):
        """
        Write the tree to a file, in the format given by its extension
        (``.dot``, ``.svg``, ``.pdf`` or ``.png``).

        Parameters
        ----------
        path : str or Path
            The file to write.

        Returns
        -------
        Path
            The path of the written file.

        Raises
        ------
        ValueError
            If the extension is not supported.
        RuntimeError
            If Graphviz is needed and not installed.
        """
        path = Path(path)
        extension = path.suffix.lower()
        if extension == ".dot":
            path.write_text(self.to_dot(), encoding="utf-8")
        elif extension == ".svg":
            path.write_text(self.to_svg(), encoding="utf-8")
        elif extension in (".pdf", ".png"):
            path.write_bytes(run_graphviz(self.to_dot(), extension[1:]))
        else:
            raise ValueError(
                f"unsupported extension {extension!r}: use .dot, .svg, .pdf or .png"
            )
        return path