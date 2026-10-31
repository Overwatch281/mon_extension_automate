import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_chain_dfa():
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


def test_induced_subautomaton_drops_outgoing_transitions_and_final_states():
    sub = make_chain_dfa().induced_subautomaton({'q0', 'q1'})
    assert sub.states == {'q0', 'q1'}
    assert dict(sub.transitions['q0']) == {'a': 'q1', 'b': 'q0'}
    assert dict(sub.transitions['q1']) == {'b': 'q1'}  # a -> q2 supprimée
    assert sub.final_states == set()  # q2 n'est plus dans l'automate
    assert type(sub) is ExtendedDFA


def test_induced_subautomaton_keeps_final_states_inside():
    sub = make_chain_dfa().induced_subautomaton({'q0', 'q1', 'q2'})
    assert sub.final_states == {'q2'}
    assert sub.accepts('aa') is True


def test_induced_subautomaton_does_not_modify_original():
    dfa = make_chain_dfa()
    dfa.induced_subautomaton({'q0'})
    assert dfa.states == {'q0', 'q1', 'q2', 'q3'}


def test_induced_subautomaton_requires_initial_state():
    with pytest.raises(ValueError):
        make_chain_dfa().induced_subautomaton({'q1', 'q2'})


def test_induced_subautomaton_rejects_unknown_state():
    with pytest.raises(ValueError):
        make_chain_dfa().induced_subautomaton({'q0', 'zzz'})


def test_induced_subautomaton_nfa():
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
    sub = nfa.induced_subautomaton({'q0', 'q1'})
    assert sub.states == {'q0', 'q1'}
    assert dict(sub.transitions['q1']) == {}  # b -> q2 supprimée
    assert type(sub) is ExtendedNFA