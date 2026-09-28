from automata_extensions.fa import ExtendedDFA


def test_accessible_states_basic():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1'},
            'q1': {'b': 'q2'},
            'q2': {'a': 'q2'},
        },
        initial_state='q0',
        final_states={'q2'},
        allow_partial=True,
    )
    assert dfa.accessible_states() == {'q0', 'q1', 'q2'}


def test_accessible_states_with_unreachable_state():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q1', 'b': 'q1'},
            'q2': {'a': 'q3', 'b': 'q3'},  # q2 et q3 ne sont jamais atteints
            'q3': {'a': 'q3', 'b': 'q3'},
        },
        initial_state='q0',
        final_states={'q1'},
    )
    assert dfa.accessible_states() == {'q0', 'q1'}


def test_accessible_states_single_state():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    assert dfa.accessible_states() == {'q0'}


def test_coaccessible_states_basic():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1'},
            'q1': {'b': 'q2'},
            'q2': {'a': 'q2'},
        },
        initial_state='q0',
        final_states={'q2'},
        allow_partial=True,
    )
    # q0 -> q1 -> q2, donc les 3 états atteignent q2
    assert dfa.coaccessible_states() == {'q0', 'q1', 'q2'}


def test_coaccessible_states_with_dead_end_state():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q3'},
            'q1': {'a': 'q1', 'b': 'q2'},
            'q2': {'a': 'q2', 'b': 'q2'},  # q2 est un puits final : coaccessible
            'q3': {'a': 'q3', 'b': 'q3'},  # q3 est un puits non final : jamais coaccessible
        },
        initial_state='q0',
        final_states={'q2'},
    )
    # q3 est accessible (depuis q0) mais pas coaccessible (aucun chemin vers q2)
    assert dfa.coaccessible_states() == {'q0', 'q1', 'q2'}


def test_coaccessible_states_single_state():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    assert dfa.coaccessible_states() == {'q0'}

def test_useful_states_excludes_unreachable_and_dead_end():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3', 'q4'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q3'},
            'q1': {'a': 'q1', 'b': 'q2'},
            'q2': {'a': 'q2', 'b': 'q2'},  # final, accessible et coaccessible
            'q3': {'a': 'q3', 'b': 'q3'},  # accessible mais pas coaccessible (puits mort)
            'q4': {'a': 'q4', 'b': 'q4'},  # coaccessible en théorie mais inaccessible (isolé)
        },
        initial_state='q0',
        final_states={'q2'},
    )
    assert dfa.useful_states() == {'q0', 'q1', 'q2'}


def test_useful_states_single_state():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    assert dfa.useful_states() == {'q0'}

def test_trim_removes_dead_end_state():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q3'},
            'q1': {'a': 'q1', 'b': 'q2'},
            'q2': {'a': 'q2', 'b': 'q2'},
            'q3': {'a': 'q3', 'b': 'q3'},  # non utile
        },
        initial_state='q0',
        final_states={'q2'},
    )
    trimmed = dfa.trim()
    assert trimmed.states == {'q0', 'q1', 'q2'}
    assert 'q3' not in trimmed.states


def test_trim_empty_language_returns_single_dead_state():
    dfa = ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q1'}, 'q1': {'a': 'q1'}},
        initial_state='q0',
        final_states=set(),  # aucun état final : langage vide
    )
    trimmed = dfa.trim()
    assert trimmed.states == {'q0'}
    assert trimmed.final_states == set()


def test_trim_does_not_modify_original():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q1', 'b': 'q1'},
            'q2': {'a': 'q2', 'b': 'q2'},  # non utile
        },
        initial_state='q0',
        final_states={'q1'},
    )
    original_states = set(dfa.states)
    dfa.trim()
    assert dfa.states == original_states  # dfa n'a pas changé

def test_is_trim_true_when_all_states_useful():
    dfa = ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q1'}, 'q1': {'a': 'q1'}},
        initial_state='q0',
        final_states={'q1'},
    )
    assert dfa.is_trim() is True


def test_is_trim_false_with_dead_end_state():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q2'},
            'q1': {'a': 'q1', 'b': 'q1'},
            'q2': {'a': 'q2', 'b': 'q2'},  # non utile
        },
        initial_state='q0',
        final_states={'q1'},
    )
    assert dfa.is_trim() is False


def test_is_trim_after_trim_is_always_true():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q3'},
            'q1': {'a': 'q1', 'b': 'q2'},
            'q2': {'a': 'q2', 'b': 'q2'},
            'q3': {'a': 'q3', 'b': 'q3'},
        },
        initial_state='q0',
        final_states={'q2'},
    )
    assert dfa.trim().is_trim() is True

def test_is_accessible_state():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q1', 'b': 'q1'},
            'q2': {'a': 'q2', 'b': 'q2'},  # inaccessible
        },
        initial_state='q0',
        final_states={'q1'},
    )
    assert dfa.is_accessible_state('q1') is True
    assert dfa.is_accessible_state('q2') is False


def test_is_coaccessible_state():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q2'},
            'q1': {'a': 'q1', 'b': 'q1'},  # ne mène jamais à q2 (final)
            'q2': {'a': 'q2', 'b': 'q2'},
        },
        initial_state='q0',
        final_states={'q2'},
    )
    assert dfa.is_coaccessible_state('q2') is True
    assert dfa.is_coaccessible_state('q1') is False