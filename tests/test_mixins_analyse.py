import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_chain_dfa():
    """
    Complete DFA over {a, b}:
    q3 -a-> q0 -a-> q1 -a-> q2 (sink, final), with self-loops on b
    (q0 -b-> q0, q1 -b-> q1, q3 -b-> q3) and on q2.
    """
    return ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q2', 'b': 'q1'},
            'q2': {'a': 'q2', 'b': 'q2'},
            'q3': {'a': 'q0', 'b': 'q3'},
        },
        initial_state='q0',
        final_states={'q2'},
    )


def test_reachable_states_from_general_case():
    dfa = make_chain_dfa()
    assert dfa.reachable_states_from('q1') == {'q1', 'q2'}
    assert dfa.reachable_states_from('q3') == {'q0', 'q1', 'q2', 'q3'}


def test_reachable_states_from_sink_state():
    dfa = make_chain_dfa()
    assert dfa.reachable_states_from('q2') == {'q2'}


def test_reachable_states_from_initial_state_is_accessible_states():
    dfa = make_chain_dfa()
    assert dfa.reachable_states_from('q0') == dfa.accessible_states()


def test_predecessors_general_case():
    dfa = make_chain_dfa()
    assert dfa.predecessors('q0') == {'q0', 'q3'}
    assert dfa.predecessors('q1') == {'q0', 'q1'}
    assert dfa.predecessors('q2') == {'q1', 'q2'}


def test_predecessors_of_state_with_only_a_self_loop():
    dfa = make_chain_dfa()
    # q3 n'est atteint que par sa propre boucle
    assert dfa.predecessors('q3') == {'q3'}


def test_states_reaching_general_case():
    dfa = make_chain_dfa()
    assert dfa.states_reaching('q1') == {'q0', 'q1', 'q3'}
    assert dfa.states_reaching('q3') == {'q3'}


def test_predecessors_nfa_with_sets_of_destinations():
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
    assert nfa.predecessors('q1') == {'q0'}
    assert nfa.predecessors('q0') == {'q0'}
    assert nfa.predecessors('q2') == {'q1'}


def test_state_queries_reject_unknown_state():
    dfa = make_chain_dfa()
    with pytest.raises(ValueError):
        dfa.reachable_states_from('zzz')
    with pytest.raises(ValueError):
        dfa.predecessors('zzz')
    with pytest.raises(ValueError):
        dfa.states_reaching('zzz')
    with pytest.raises(ValueError):
        dfa.has_cycle_from('zzz')