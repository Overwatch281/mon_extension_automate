# Correspondance avec le cahier des charges

Cette table relie chacun des 62 points du sujet à la méthode qui le réalise.
Les chemins sont relatifs à `automata_extensions/`. Sauf mention contraire,
les méthodes s'appellent sur un `ExtendedDFA` ou un `ExtendedNFA`
(mixins de `fa/mixins/`).

## Niveau 1 : algorithmes sur les automates finis

| N° | Fonctionnalité | Utilisation | Fichier |
|---:|---|---|---|
| 1 | Parcours en profondeur (itératif et récursif) | `dfs()`, `dfs_recursive()` | `traversals.py` |
| 2 | Parcours en largeur | `bfs()`, `bfs_levels()` | `traversals.py` |
| 3 | États accessibles | `accessible_states()` | `analyse.py` |
| 4 | Test d'accessibilité d'un état | `is_accessible_state(q)` | `analyse.py` |
| 5 | États coaccessibles | `coaccessible_states()` | `analyse.py` |
| 6 | Test de coaccessibilité d'un état | `is_coaccessible_state(q)` | `analyse.py` |
| 7 | États utiles | `useful_states()` | `analyse.py` |
| 8 | Émondage | `trim()` | `conversions.py` |
| 9 | Test « automate émondé » | `is_trim()` | `analyse.py` |
| 10 | Composantes fortement connexes (Tarjan) | `strongly_connected_components()` | `cycles.py` |
| 11 | Existence d'un cycle | `has_cycle()` | `cycles.py` |
| 12 | Cycle accessible depuis un état | `has_cycle_from(q)` | `cycles.py` |
| 13 | Langage vide | `is_empty()` | `analyse.py` |
| 14 | Langage infini | `is_infinite()`, `is_finite()` | `cycles.py` |
| 15 | Reconnaissance d'un mot | `accepts(mot)` | `simulation.py` |
| 16 | Trace d'exécution | `trace(mot)` | `simulation.py` |
| 17 | États atteignables depuis un état | `reachable_states_from(q)` | `analyse.py` |
| 18 | Prédécesseurs d'un état | `predecessors(q)`, `states_reaching(q)` | `analyse.py` |
| 19 | Sous-automate induit | `induced_subautomaton(états)` | `conversions.py` |
| 20 | Test « automate complet » | `is_complete()` | `operations.py` |
| 21 | Complétion (état puits) | `complete()` | `operations.py` |
| 22 | Complément | `complement()` | `operations.py` |
| 23 | Produit cartésien paresseux | `product(autre, condition)` | `products.py` |
| 24 | Inclusion de langages | `language_subset(autre)` | `products.py` |
| 25 | Égalité de langages | `language_equals(autre)` | `products.py` |
| 26 | Isomorphisme | `is_isomorphic(autre)` | `relations.py` |
| 27 | Langage préfixe clos | `is_prefix_closed()` | `languages.py` |
| 28 | Plus grand sous-langage préfixe clos | `prefix_closed_sublanguage()` | `languages.py` |
| 29 | États distinguables | `distinguishable_pairs()` | `minimisation.py` |
| 30 | Classes d'équivalence des états | `equivalence_classes()` | `minimisation.py` |
| 31 | Test « automate minimal » | `is_minimal()` | `minimisation.py` |
| 32 | Minimisation | `minimize()` | `minimisation.py` |
| 33 | Test « automate déterministe » | `is_deterministic()` | `determinisation.py` |
| 34 | ε-fermeture | `epsilon_closure(q)`, `epsilon_closure_of_set(S)` | `determinisation.py` |
| 35 | Déterminisation | `determinize()` | `determinisation.py` |
| 36 | Renversement (miroir) | `reverse()` | `transformations.py` |
| 37 | Suppression des ε-transitions | `remove_epsilon_transitions()` | `transformations.py` |
| 38 | Langage universel | `is_universal()` | `languages.py` |
| 39 | Élimination d'un état d'un ε-AFEND normalisé | `to_gnfa()` puis `eliminate_state(q)` | `regex_conversions.py`, `elimination.py` |
| 40 | Export DOT | `dot()` | `visualisation.py` |
| 41 | Export SVG / PDF / PNG / TikZ | `svg()`, `pdf()`, `png()`, `tikz()`, `latex()`, `save(chemin)` | `export.py`, `graphviz_tools.py` |

## Niveau 2 : opérations, expressions régulières

| N° | Fonctionnalité | Utilisation | Fichier |
|---:|---|---|---|
| 42 | Union | `union(autre)` | `language_operations.py` |
| 43 | Intersection | `intersection(autre)` | `language_operations.py` |
| 44 | Différence | `difference(autre)` | `language_operations.py` |
| 45 | Concaténation | `concatenate(autre)` | `language_operations.py` |
| 46 | Étoile de Kleene | `star()` | `language_operations.py` |
| 47 | Quotient à gauche | `left_quotient(mot)` | `quotients.py` |
| 48 | Quotient à droite | `right_quotient(mot)` | `quotients.py` |
| 49 | Dérivées de Brzozowski | `Regex.derivative(a)`, `derivative_word(mot)` | `regex/base.py`, `regex/constructors.py` |
| 50 | Automate de Brzozowski | `brzozowski_automaton()` | `automaton_conversions.py` |
| 51 | Expression régulière vers NFA (Thompson) | `Regex.to_nfa()` | `regex/construction.py` |
| 52 | NFA vers DFA (sous-ensembles) | `to_dfa()` (= `determinize()`) | `automaton_conversions.py` |
| 53 | Automate vers expression, par élimination d'états | `to_regex("elimination")` | `regex_conversions.py` |
| 54 | Automate vers expression, par système d'équations | `to_regex("arden")` | `regex_conversions.py`, `regex/equations.py` |

## Niveau 3 : grammaires et objets algébriques

| N° | Fonctionnalité | Utilisation | Fichier |
|---:|---|---|---|
| 55 | Automate vers grammaire régulière, et inversement | `to_grammar()`, `RegularGrammar.to_nfa()` | `grammaire.py`, `grammar/regular.py` |
| 56 | Arbres de dérivation | `ContextFreeGrammar.parse(mot)`, `ParseTree` | `grammar/parsing.py`, `grammar/parse_tree.py` |
| 57 | Lemme d'Arden | `arden(A, B)` | `regex/equations.py` |
| 58 | Systèmes d'équations rationnelles | `EquationSystem.from_automaton(a).solve()` | `regex/equations.py` |
| 59 | Classes de Myhill-Nerode | `myhill_nerode_classes()`, `nerode_equivalent(u, v)` | `residuals.py` |
| 60 | Automate résiduel | `residual_automaton()` | `residuals.py` |
| 61 | Morphismes d'automates | `AutomatonMorphism`, `merge_states()`, `minimization_morphism()`, `morphism_to()` | `morphisms.py`, `algebra.py` |
| 62 | Monoïde syntaxique | `syntactic_monoid()` | `monoid.py`, `algebra.py` |

## Fonctionnalités ajoutées en plus du sujet

- Conversions : `to_nfa()`, `to_gnfa()`, `Regex.to_dfa()`, `Regex.parse(texte)` ;
- expressions régulières : `nullable()`, `simplify()`, `accepts(mot)`, `symbols()` ;
- grammaires : `ContextFreeGrammar.from_text(...)`, `generates(mot)`,
  `leftmost_derivation(mot)`, `rightmost_derivation(mot)`,
  `ParseTree.from_leftmost_derivation(...)`, `is_right_linear()` ;
- export des arbres de dérivation : `to_dot()`, `to_svg()`, `save(chemin)`.
