import shutil
import subprocess

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_two_state_dfa():
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


def test_dot_describes_states_initial_arrow_and_final_states():
    dot = make_two_state_dfa().dot()
    assert dot.startswith('digraph automaton {')
    assert dot.rstrip().endswith('}')
    assert '__start -> n0;' in dot
    assert 'n0 [label="q0"];' in dot
    assert 'n1 [label="q1", shape=doublecircle];' in dot


def test_dot_groups_the_symbols_of_parallel_transitions():
    dot = make_two_state_dfa().dot()
    assert 'n0 -> n1 [label="a,b"];' in dot
    assert 'n1 -> n1 [label="a,b"];' in dot


def test_dot_draws_epsilon_transitions_as_epsilon():
    nfa = ExtendedNFA(
        states={'q0', 'q1'},
        input_symbols={'a'},
        transitions={'q0': {'': {'q1'}}, 'q1': {'a': {'q1'}}},
        initial_state='q0',
        final_states={'q1'},
    )
    assert 'n0 -> n1 [label="ε"];' in nfa.dot()


def test_dot_names_set_states_readably_and_is_deterministic():
    dfa = ExtendedDFA(
        states={frozenset(), frozenset({'t0', 's0'})},
        input_symbols={'a'},
        transitions={
            frozenset(): {'a': frozenset({'t0', 's0'})},
            frozenset({'t0', 's0'}): {'a': frozenset()},
        },
        initial_state=frozenset(),
        final_states={frozenset({'t0', 's0'})},
    )
    dot = dfa.dot()
    assert 'label="∅"' in dot
    assert 'label="{s0,t0}"' in dot
    assert dot == dfa.dot()


def test_dot_escapes_quotes_in_state_names():
    dfa = ExtendedDFA(
        states={'say "hi"'},
        input_symbols={'a'},
        transitions={'say "hi"': {'a': 'say "hi"'}},
        initial_state='say "hi"',
        final_states={'say "hi"'},
    )
    assert 'label="say \\"hi\\""' in dfa.dot()


def test_dot_of_a_gnfa_shows_regex_labels():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0', 'b': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    gnfa = dfa.to_gnfa().eliminate_state('q0')
    assert '[label="(a|b)*"];' in gnfa.dot()


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz is not installed")
def test_dot_output_is_accepted_by_graphviz():
    result = subprocess.run(
        ["dot", "-Tsvg"],
        input=make_two_state_dfa().dot().encode("utf-8"),
        capture_output=True,
    )
    assert result.returncode == 0
    assert b"<svg" in result.stdout