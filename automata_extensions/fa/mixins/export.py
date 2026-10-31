"""Export of automata to SVG, PDF, PNG and TikZ, through Graphviz.

The DOT text comes from VisualisationMixin.dot(); the layout and the image
formats come from the Graphviz program ``dot``, which must be installed
and reachable from the PATH.
"""

from pathlib import Path

from automata_extensions.fa.graphviz_tools import plain_to_tikz, run_graphviz


class ExportMixin:
    """Mixin providing image and LaTeX exports of an automaton."""

    def svg(self):
        """
        Return the drawing of the automaton as SVG text.

        Returns
        -------
        str
            An SVG document.

        Raises
        ------
        RuntimeError
            If Graphviz is not installed.

        Complexity
        ----------
        Depends on the Graphviz layout algorithm.
        """
        return run_graphviz(self.dot(), "svg").decode("utf-8")

    def pdf(self):
        """
        Return the drawing of the automaton as a PDF document.

        Returns
        -------
        bytes
            The content of a PDF file.

        Raises
        ------
        RuntimeError
            If Graphviz is not installed.
        """
        return run_graphviz(self.dot(), "pdf")

    def png(self):
        """
        Return the drawing of the automaton as a PNG image.

        Returns
        -------
        bytes
            The content of a PNG file.

        Raises
        ------
        RuntimeError
            If Graphviz is not installed.
        """
        return run_graphviz(self.dot(), "png")

    def tikz(self):
        """
        Return the drawing of the automaton as a TikZ picture.

        Graphviz computes the layout, which is then translated into a
        ``tikzpicture`` environment. To use it in a LaTeX document, load
        the package with ``\\usepackage{tikz}``.

        Returns
        -------
        str
            A ``tikzpicture`` environment.

        Raises
        ------
        RuntimeError
            If Graphviz is not installed.
        """
        return plain_to_tikz(run_graphviz(self.dot(), "plain").decode("utf-8"))

    def latex(self):
        """
        Return a complete LaTeX document containing the TikZ picture.

        The document uses the ``standalone`` class, so compiling it with
        pdflatex gives a PDF page cropped around the automaton.

        Returns
        -------
        str
            The source of a LaTeX document.

        Raises
        ------
        RuntimeError
            If Graphviz is not installed.
        """
        return (
            "\\documentclass[tikz,border=5pt]{standalone}\n"
            "\\begin{document}\n"
            f"{self.tikz()}"
            "\\end{document}\n"
        )

    def save(self, path):
        """
        Write the automaton to a file, in the format given by its extension.

        Supported extensions: ``.dot``, ``.svg``, ``.pdf``, ``.png`` and
        ``.tex`` (a complete LaTeX document).

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

        text_exports = {".dot": self.dot, ".svg": self.svg, ".tex": self.latex}
        binary_exports = {".pdf": self.pdf, ".png": self.png}

        if extension in text_exports:
            path.write_text(text_exports[extension](), encoding="utf-8")
        elif extension in binary_exports:
            path.write_bytes(binary_exports[extension]())
        else:
            raise ValueError(
                f"unsupported extension {extension!r}: "
                "use .dot, .svg, .pdf, .png or .tex"
            )
        return path