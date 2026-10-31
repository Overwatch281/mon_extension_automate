"""Helpers to call Graphviz and to turn its layout into TikZ code.

Graphviz (the ``dot`` program) computes the layout of the automaton. Its
"plain" output gives the position of every state and the Bezier curve of
every edge: we translate it into a ``tikzpicture`` that reproduces the same
drawing in LaTeX, without needing the dot2tex tool.
"""

import math
import re
import shutil
import subprocess

# Geometry used by Graphviz, in inches.
_ARROW_LENGTH = 0.1389
_ARROW_HALF_WIDTH = 0.0486
_DOUBLE_CIRCLE_GAP = 0.0556

_TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|(\S+)')

_LATEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "|": r"\textbar{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
    "ε": r"$\varepsilon$",
    "∅": r"$\emptyset$",
}


def run_graphviz(dot_text, output_format):
    """
    Run the Graphviz ``dot`` program on a DOT text.

    Parameters
    ----------
    dot_text : str
        The DOT description of a graph.
    output_format : str
        A Graphviz output format: ``svg``, ``pdf``, ``png``, ``plain``...

    Returns
    -------
    bytes
        What Graphviz wrote on its standard output.

    Raises
    ------
    RuntimeError
        If Graphviz is not installed (not in the PATH) or fails.
    """
    executable = shutil.which("dot")
    if executable is None:
        raise RuntimeError(
            "the Graphviz program 'dot' was not found: install Graphviz "
            "and add its 'bin' folder to the PATH"
        )

    result = subprocess.run(
        [executable, f"-T{output_format}"],
        input=dot_text.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"Graphviz failed: {message}")
    return result.stdout


def latex_escape(text):
    """Escape a text so that LaTeX prints it as it is."""
    return "".join(_LATEX_REPLACEMENTS.get(char, char) for char in text)


def _tokens(line):
    """Split a line of Graphviz plain output (double quotes group words)."""
    tokens = []
    for match in _TOKEN.finditer(line):
        if match.group(1) is not None:
            tokens.append(re.sub(r"\\(.)", r"\1", match.group(1)))
        else:
            tokens.append(match.group(2))
    return tokens


def _number(value):
    """Format a coordinate with at most 4 decimals."""
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def _point(x, y):
    """Format a TikZ coordinate."""
    return f"({_number(x)},{_number(y)})"


def _arrow_head(end, before):
    """
    Return the TikZ command drawing the arrow head of an edge.

    Graphviz stops the curve where the arrow head starts, so the head is
    drawn as a small triangle pointing in the direction of the curve.
    """
    dx, dy = end[0] - before[0], end[1] - before[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return None
    ux, uy = dx / length, dy / length
    tip = (end[0] + _ARROW_LENGTH * ux, end[1] + _ARROW_LENGTH * uy)
    left = (end[0] - _ARROW_HALF_WIDTH * uy, end[1] + _ARROW_HALF_WIDTH * ux)
    right = (end[0] + _ARROW_HALF_WIDTH * uy, end[1] - _ARROW_HALF_WIDTH * ux)
    return (
        f"  \\fill {_point(*left)} -- {_point(*tip)} -- "
        f"{_point(*right)} -- cycle;"
    )


def plain_to_tikz(plain_text):
    """
    Translate the "plain" output of Graphviz into a TikZ picture.

    Coordinates are kept in inches (the unit of Graphviz). Each state
    becomes a circle (two for a final state), each edge a Bezier curve
    followed by an arrow head, and each edge label a small text node.
    The picture needs the ``tikz`` package.

    Parameters
    ----------
    plain_text : str
        The output of ``dot -Tplain``.

    Returns
    -------
    str
        A ``tikzpicture`` environment.
    """
    lines = ["\\begin{tikzpicture}[x=1in, y=1in, semithick]"]

    for raw_line in plain_text.splitlines():
        tokens = _tokens(raw_line)
        if not tokens:
            continue

        if tokens[0] == "node":
            name = tokens[1]
            x, y, width = float(tokens[2]), float(tokens[3]), float(tokens[4])
            label, style, shape = tokens[6], tokens[7], tokens[8]
            if style == "invis":
                continue
            lines.append(
                f"  \\node[circle, draw, inner sep=0pt, "
                f"minimum size={_number(width)}in] ({name}) "
                f"at {_point(x, y)} {{{latex_escape(label)}}};"
            )
            if shape == "doublecircle":
                inner = width / 2 - _DOUBLE_CIRCLE_GAP
                lines.append(
                    f"  \\draw {_point(x, y)} circle ({_number(inner)}in);"
                )

        elif tokens[0] == "edge":
            count = int(tokens[3])
            coords = [
                (float(tokens[4 + 2 * i]), float(tokens[5 + 2 * i]))
                for i in range(count)
            ]
            rest = tokens[4 + 2 * count:]

            path = _point(*coords[0])
            for i in range(1, count - 2, 3):
                path += (
                    f" .. controls {_point(*coords[i])} and "
                    f"{_point(*coords[i + 1])} .. {_point(*coords[i + 2])}"
                )
            lines.append(f"  \\draw {path};")

            arrow = _arrow_head(coords[-1], coords[-2])
            if arrow is not None:
                lines.append(arrow)

            if len(rest) >= 5 and rest[0] != "":
                lines.append(
                    f"  \\node[inner sep=1pt] at "
                    f"{_point(float(rest[1]), float(rest[2]))} "
                    f"{{{latex_escape(rest[0])}}};"
                )

    lines.append("\\end{tikzpicture}")
    return "\n".join(lines) + "\n"