import os
import shutil
import subprocess

import pytest

from automata_extensions.fa import ExtendedDFA, graphviz_tools
from automata_extensions.fa.graphviz_tools import latex_escape, plain_to_tikz

needs_graphviz = pytest.mark.skipif(
    shutil.which("dot") is None, reason="Graphviz is not installed"
)

SAMPLE_PLAIN = """graph 1 2.2 1.0
node __start 0.025 0.5 0.05 0.05 "" invis point black lightgrey
node n0 0.8 0.5 0.6 0.6 q_0 solid circle black lightgrey
node n1 1.8 0.5 0.7 0.7 q1 solid doublecircle black lightgrey
edge __start n0 4 0.05 0.5 0.1 0.5 0.25 0.5 0.4 0.5 solid black
edge n0 n1 4 1.1 0.5 1.3 0.5 1.4 0.5 1.5 0.5 "a,b" 1.3 0.6 solid black
stop
"""


def make_dfa():
    """DFA over {a, b}: a and b both lead from q0 to q1 (final)."""
    return ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q1'},
            'q1': {'a': 'q1', 'b': 'q1'},
        },
        initial_state='q0',
        final_states={'q1'},
    )


# ------------------------------------------------- translation to TikZ (pure)

def test_plain_to_tikz_translates_nodes_edges_and_labels():
    tikz = plain_to_tikz(SAMPLE_PLAIN)
    assert tikz.startswith('\\begin{tikzpicture}')
    assert tikz.endswith('\\end{tikzpicture}\n')
    assert '(n0)' in tikz and '(n1)' in tikz
    assert '__start' not in tikz  # le point de départ est invisible
    assert 'q\\_0' in tikz  # caractère spécial LaTeX échappé
    assert tikz.count('circle (') == 1  # cercle intérieur de l'état final
    assert tikz.count('.. controls') == 2  # une courbe par arête
    assert tikz.count('\\fill') == 2  # une pointe de flèche par arête
    assert '{a,b}' in tikz  # étiquette entre guillemets dans la sortie plain


def test_latex_escape_and_apostrophes_in_labels():
    assert latex_escape('a_b#{c}|ε∅') == (
        'a\\_b\\#\\{c\\}\\textbar{}$\\varepsilon$$\\emptyset$'
    )
    plain = "node n0 0.5 0.5 0.6 0.6 q' solid circle black lightgrey\nstop\n"
    assert "{q'}" in plain_to_tikz(plain)


def test_run_graphviz_reports_a_missing_graphviz(monkeypatch):
    monkeypatch.setattr(graphviz_tools.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError):
        graphviz_tools.run_graphviz("digraph {}", "svg")


def test_save_rejects_an_unsupported_extension(tmp_path):
    target = tmp_path / "automaton.jpg"
    with pytest.raises(ValueError):
        make_dfa().save(target)
    assert not target.exists()


# ---------------------------------------------------- real Graphviz exports

@needs_graphviz
def test_svg_contains_the_drawing():
    svg = make_dfa().svg()
    assert '<svg' in svg
    assert 'q0' in svg


@needs_graphviz
def test_pdf_and_png_have_the_right_signature():
    dfa = make_dfa()
    assert dfa.pdf().startswith(b'%PDF')
    assert dfa.png().startswith(b'\x89PNG')


@needs_graphviz
def test_tikz_draws_every_state():
    tikz = make_dfa().tikz()
    assert tikz.startswith('\\begin{tikzpicture}')
    assert tikz.count('\\node[circle') == 2
    assert '(n0)' in tikz and '(n1)' in tikz


@needs_graphviz
def test_save_writes_each_supported_format(tmp_path):
    dfa = make_dfa()
    for extension in ('.dot', '.svg', '.pdf', '.png', '.tex'):
        written = dfa.save(tmp_path / f'automaton{extension}')
        assert written.exists()
        assert written.stat().st_size > 0
    tex = (tmp_path / 'automaton.tex').read_text(encoding='utf-8')
    assert tex.startswith('\\documentclass')


@needs_graphviz
def test_a_gnfa_can_be_exported_too():
    gnfa = make_dfa().to_gnfa().eliminate_state('q0')
    assert '<svg' in gnfa.svg()
    assert '\\begin{tikzpicture}' in gnfa.tikz()


@pytest.mark.skipif(
    shutil.which("dot") is None
    or shutil.which("pdflatex") is None
    or not os.environ.get("RUN_LATEX_TESTS"),
    reason="set RUN_LATEX_TESTS=1 (with Graphviz and pdflatex installed) to run",
)
def test_latex_document_compiles_with_pdflatex(tmp_path):
    make_dfa().save(tmp_path / 'automaton.tex')
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'automaton.tex'],
        cwd=tmp_path,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0
    assert (tmp_path / 'automaton.pdf').exists()