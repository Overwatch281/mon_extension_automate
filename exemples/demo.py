"""Exemples d'utilisation de automata_extensions.

Lancer avec :  python exemples/demo.py

Chaque exemple affiche des résultats et vérifie avec un `assert` ce qui est
attendu : si le script s'arrête sur une AssertionError, quelque chose ne va pas.
"""

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.grammar import ContextFreeGrammar
from automata_extensions.regex import EquationSystem, parse_regex


def titre(texte):
    print()
    print("=" * 64)
    print(texte)
    print("=" * 64)


# ===== SECTION 1 =====
titre("1. Un DFA : les mots qui ont un nombre pair de 'a'")
pair = ExtendedDFA(
    states={'pair', 'impair'},
    input_symbols={'a', 'b'},
    transitions={
        'pair': {'a': 'impair', 'b': 'pair'},
        'impair': {'a': 'pair', 'b': 'impair'},
    },
    initial_state='pair',
    final_states={'pair'},
)
print("aab accepté ?", pair.accepts("aab"))
print("ab accepté ?", pair.accepts("ab"))
print("trace de aab :", [sorted(etats) for etats in pair.trace("aab")])
assert pair.accepts("aab") and not pair.accepts("ab")

# ===== SECTION 2 =====
titre("2. Minimisation d'un DFA qui a deux états équivalents (s0 et t0)")
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
minimal = redondant.minimize()
print(len(redondant.states), "états ->", len(minimal.states), "états")
assert len(minimal.states) == 3 and minimal.is_minimal()
assert minimal.language_equals(redondant)

# ===== SECTION 3 =====
titre("3. Opérations sur les langages")
finit_par_a = ExtendedDFA(
    states={'s0', 's1'},
    input_symbols={'a', 'b'},
    transitions={
        's0': {'a': 's1', 'b': 's0'},
        's1': {'a': 's1', 'b': 's0'},
    },
    initial_state='s0',
    final_states={'s1'},
)
intersection = pair.intersection(finit_par_a)
print("aa dans (pair ET finit par a) ?", intersection.accepts("aa"))
print("a  dans (pair ET finit par a) ?", intersection.accepts("a"))
assert intersection.accepts("aa") and not intersection.accepts("a")
assert pair.union(finit_par_a).accepts("b")
assert pair.complement().complement().language_equals(pair)

# ===== SECTION 4 =====
titre("4. Un NFA (mots finissant par ab) et sa déterminisation")
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
deterministe = nfa.determinize()
print("états du DFA obtenu :", len(deterministe.states))
assert nfa.accepts("aab") and not nfa.accepts("abb")
assert len(deterministe.states) == 3 and deterministe.is_complete()

# ===== SECTION 5 =====
titre("5. Expressions régulières : dérivées et automates")
expression = parse_regex("(a|b)*abb")
print("expression :", expression)
print("dérivée par a :", expression.derivative("a"))
print("aabb reconnu ?", expression.accepts("aabb"))
print("états du DFA des dérivées :", len(expression.to_dfa().states))
print("états du NFA de Thompson :", len(expression.to_nfa().states))
assert expression.accepts("aabb") and not expression.accepts("ab")
assert len(expression.to_dfa().states) == 4
assert len(expression.to_nfa().states) == 14

# ===== SECTION 6 =====
titre("6. D'un automate à une expression régulière")
par_elimination = pair.to_regex()
par_arden = pair.to_regex("arden")
print("par élimination d'états :", par_elimination)
print("par le lemme d'Arden    :", par_arden)
for resultat in (par_elimination, par_arden):
    assert resultat.to_dfa(alphabet={'a', 'b'}).language_equals(pair)
print("\nSystème d'équations de l'automate :")
print(EquationSystem.from_automaton(pair))

# ===== SECTION 7 =====
titre("7. Grammaires et arbres de dérivation")
grammaire_reguliere = pair.to_grammar()
print(grammaire_reguliere)
assert grammaire_reguliere.generates("abab") == pair.accepts("abab")

an_bn = ContextFreeGrammar.from_text("S -> a S b | ε")
arbre = an_bn.parse("aabb")
print("\narbre de aabb :", arbre)
print("dérivation gauche :", an_bn.leftmost_derivation("aabb"))
assert arbre.text() == "aabb" and arbre.is_valid_for(an_bn)

# ===== SECTION 8 =====
titre("8. Quotients")
apres_a = pair.left_quotient("a")
print("après avoir lu 'a', on est dans l'état :", apres_a.initial_state)
assert apres_a.initial_state == 'impair' and apres_a.accepts("a")

# ===== SECTION 9 =====
titre("9. Automate résiduel : un NFA plus petit que le DFA minimal")
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
)  # la 3e lettre avant la fin est un 'a'
minimal_3 = troisieme.determinize().minimize()
residuel = troisieme.residual_automaton()
print("DFA minimal :", len(minimal_3.states), "états ; automate résiduel :",
      len(residuel.states), "états")
assert len(minimal_3.states) == 8 and len(residuel.states) == 4

# ===== SECTION 10 =====
titre("10. Monoïde syntaxique")
finit_par_ab = redondant.minimize()
monoide = finit_par_ab.syntactic_monoid()
print("mots finissant par ab :", len(monoide), "éléments", monoide.elements())
print("nombre pair de a :", len(pair.syntactic_monoid()), "éléments")
assert len(monoide) == 5 and monoide.is_aperiodic()
assert len(pair.syntactic_monoid()) == 2 and not pair.syntactic_monoid().is_aperiodic()

# ===== SECTION 11 =====
titre("11. Morphisme de fusion d'états")
projection = redondant.merge_states([{'s0', 't0'}, {'s1'}, {'s2'}])
print(projection)
assert projection.is_surjective() and len(projection.target.states) == 3

# ===== SECTION 12 =====
titre("12. Export : description DOT (pour Graphviz)")
print(pair.dot())
print("Pour dessiner : pair.save('automate.png')  (Graphviz doit être installé)")
