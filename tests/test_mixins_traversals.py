import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_tree_dfa():
    """
    Complete DFA over {a, b} where the DFS and the BFS orders differ:

        q0 -a-> q1, q0 -b-> q2
        q1 -> q3 (on a and b),  q2 -> q4 (on a and b),  q3 and q4 loop.
    """
    return ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3', 'q4'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q2'},
            'q1': {'a': 'q3', 'b': 'q3'},
            'q2': {'a': 'q4', 'b': 'q4'},
            'q3': {'a': 'q3', 'b': 'q3'},
            'q4': {'a': 'q4', 'b': 'q4'},
        },
        initial_state='q0',
        final_states={'q3'},
    )


def test_dfs_explores_deeply_before_going_to_the_next_branch():
    assert make_tree_dfa().dfs() == ['q0', 'q1', 'q3', 'q2', 'q4']


def test_recursive_dfs_gives_the_same_order_as_the_iterative_one():
    dfa = make_tree_dfa()
    for start in (None, 'q1', 'q2', 'q4'):
        assert dfa.dfs_recursive(start) == dfa.dfs(start)


def test_bfs_explores_level_by_level():
    dfa = make_tree_dfa()
    assert dfa.bfs() == ['q0', 'q1', 'q2', 'q3', 'q4']
    assert dfa.bfs_levels() == [['q0'], ['q1', 'q2'], ['q3', 'q4']]


def test_traversals_can_start_from_any_state():
    dfa = make_tree_dfa()
    assert dfa.dfs('q2') == ['q2', 'q4']
    assert dfa.bfs('q2') == ['q2', 'q4']
    assert dfa.bfs_levels('q2') == [['q2'], ['q4']]


def test_traversals_only_visit_accessible_states():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q5'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q1'}, 'q1': {'a': 'q1'}, 'q5': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q1'},
    )
    assert 'q5' not in dfa.dfs()
    assert set(dfa.dfs()) == dfa.accessible_states()
    assert set(dfa.bfs()) == dfa.accessible_states()


def test_traversals_work_on_an_nfa_and_stop_on_loops():
    nfa = ExtendedNFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': {'q0', 'q1'}, 'b': {'q0'}},
            'q1': {'b': {'q2'}},
            'q2': {},
        },
        initial_state='q0',
        final_states={'q2'},
    )
    assert nfa.dfs() == ['q0', 'q1', 'q2']
    assert nfa.dfs_recursive() == ['q0', 'q1', 'q2']
    assert nfa.bfs_levels() == [['q0'], ['q1'], ['q2']]


def test_traversal_of_a_single_state_automaton():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    assert dfa.dfs() == ['q0']
    assert dfa.dfs_recursive() == ['q0']
    assert dfa.bfs() == ['q0']
    assert dfa.bfs_levels() == [['q0']]


def test_traversals_reject_an_unknown_start_state():
    dfa = make_tree_dfa()
    for method in (dfa.dfs, dfa.dfs_recursive, dfa.bfs, dfa.bfs_levels):
        with pytest.raises(ValueError):
            method('zzz')