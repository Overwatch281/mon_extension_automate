"""Génère les schémas du README dans docs/images/.

Lancer depuis la racine du projet :  python docs/generer_schemas.py
Graphviz doit être installé (programme `dot` dans le PATH).
"""

from pathlib import Path

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.grammar import ContextFreeGrammar
from automata_extensions.regex import parse_regex

DOSSIER = Path(__file__).resolve().parent / "images"
DOSSIER.mkdir(parents=True, exist_ok=True)


def enregistrer(objet, nom):
    """Écrit le dessin de `objet` (automate ou arbre) dans docs/images/."""
    print("écrit :", objet.save(DOSSIER / nom))


# Mots finissant par ab : un DFA et un NFA
finit_par_ab = ExtendedDFA(
    states={'s0', 's1', 's2'},
    input_symbols={'a', 'b'},
    transitions={
        's0': {'a': 's1', 'b': 's0'},
        's1': {'a': 's1', 'b': 's2'},
        's2': {'a': 's1', 'b': 's0'},
    },
    initial_state='s0',
    final_states={'s2'},
)
nfa_finit_par_ab = ExtendedNFA(
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
enregistrer(finit_par_ab, "dfa_finit_par_ab.png")
enregistrer(nfa_finit_par_ab, "nfa_finit_par_ab.png")

# Minimisation : s0 et t0 sont équivalents
redondant = ExtendedDFA(
    states={'s0', 't0', 's1', 's2'},
    input_symbols={'a', 'b'},
    transitions={
        's0': {'a': 's1', 'b': 't0'},
        't0': {'a': 's1', 'b': 's0'},
        's1': {'a': 's1', 'b': 's2'},
        's2': {'a': 's1', 'b': 's0'},
    },
    initial_state='s0',
    final_states={'s2'},
)
enregistrer(redondant, "dfa_redondant.png")
enregistrer(redondant.minimize(), "dfa_minimise.png")

# Expressions régulières : Thompson et automate des dérivées
enregistrer(parse_regex("(a|b)*").to_nfa(), "thompson.png")
enregistrer(parse_regex("(a|b)*abb").to_dfa(), "automate_des_derivees.png")

# Élimination d'états (GNFA) : on supprime l'état s1
enregistrer(finit_par_ab.to_gnfa().eliminate_state('s1'), "gnfa_apres_elimination.png")

# Automate résiduel : la 3e lettre avant la fin est un 'a'
troisieme = ExtendedNFA(
    states={'0', '1', '2', '3'},
    input_symbols={'a', 'b'},
    transitions={
        '0': {'a': {'0', '1'}, 'b': {'0'}},
        '1': {'a': {'2'}, 'b': {'2'}},
        '2': {'a': {'3'}, 'b': {'3'}},
        '3': {},
    },
    initial_state='0',
    final_states={'3'},
)
enregistrer(troisieme, "nfa_3e_lettre_avant_la_fin.png")
enregistrer(troisieme.residual_automaton(), "automate_residuel.png")

# Arbre de dérivation de aabb dans la grammaire S -> a S b | ε
arbre = ContextFreeGrammar.from_text("S -> a S b | ε").parse("aabb")
enregistrer(arbre, "arbre_de_derivation.png")
