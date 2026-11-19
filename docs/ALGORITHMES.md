# Algorithmes et complexités

Notations : *Q* l'ensemble des états, *Σ* l'alphabet, *E* l'ensemble des transitions
(|E| ≤ |Q|·|Σ| pour un DFA), *n* la longueur d'un mot. Les numéros entre parenthèses
renvoient aux points du sujet (voir [CORRESPONDANCE.md](CORRESPONDANCE.md)).

## 1. Parcours et structure du graphe (1 à 14, 17, 18)

- **États accessibles** : parcours en profondeur depuis l'état initial, avec une pile.
  **Coaccessibles** : le même parcours sur le graphe inversé, depuis les états finaux.
  **Utiles** : l'intersection des deux. **Émondage** : sous-automate induit par les états
  utiles. Complexité : O(|Q| + |E|).
- **DFS et BFS** : la version itérative (pile explicite) et la version récursive donnent
  le même ordre, car les successeurs sont toujours visités dans l'ordre alphabétique de
  leur nom. Le BFS utilise une file et regroupe les états par distance. O(|Q| + |E|).
- **Composantes fortement connexes** : algorithme de Tarjan. O(|Q| + |E|).
- **Cycles** : parcours en profondeur avec trois couleurs ; une arête vers un état « en cours »
  est une arête de retour. Le langage est **infini** exactement quand il y a un cycle formé
  d'états utiles. O(|Q| + |E|).
- **Langage vide** : aucun état final n'est accessible.

## 2. Simulation (15, 16)

On suit l'**ensemble des états actifs** (ε-fermeture comprise) après chaque symbole. Pour un
DFA, il contient au plus un état. Le mot est accepté si l'ensemble final contient un état final.
O(n · (|Q| + |E|)).

## 3. Complétion, complément, produit (20 à 25, 38, 42 à 44)

- **Complétion** : les transitions manquantes vont vers un état puits. **Complément** :
  déterminiser, compléter, puis échanger états finaux et non finaux. O(|Q|·|Σ|) pour un DFA ;
  exponentiel pour un NFA (à cause de la déterminisation).
- **Produit** : construit **paresseusement** par un parcours en largeur à partir du couple des
  états initiaux (seuls les couples accessibles sont créés). Un couple est final selon une
  condition sur ses deux composantes : « ou » pour l'union, « et » pour l'intersection,
  « premier et pas second » pour la différence. O(|Q₁|·|Q₂|·|Σ|).
- **Inclusion** L₁ ⊆ L₂ : la différence L₁ \ L₂ est vide. **Égalité** : double inclusion.
  **Universalité** : le complément est vide.

## 4. Minimisation et équivalence (26, 29 à 32, 50)

- **États distinguables** : algorithme du remplissage de table. On marque d'abord les couples
  dont un seul état est final, puis on marque un couple dès que, pour un symbole, ses
  successeurs forment un couple marqué, jusqu'à stabilité. Les couples non marqués sont les
  états équivalents. O(|Q|³·|Σ|).
- **Minimisation** : on garde les états accessibles, on complète, puis on fusionne chaque classe.
  Le résultat est le DFA minimal **complet**, unique à isomorphisme près.
- **Isomorphisme** : parcours simultané des deux automates depuis leurs états initiaux, en
  construisant le renommage ; échec à la première incohérence. O(|Q|·|Σ|).
- **Automate de Brzozowski** : déterminiser, puis deux fois « renverser et construire les
  sous-ensembles ». Le résultat est le DFA minimal complet. Le piège : `reverse()` ajoute un état
  initial artificiel qui créerait des doublons ; on construit donc directement les sous-ensembles
  des transitions inversées, à partir de l'ensemble des états finaux. Exponentiel au pire.

## 5. ε-transitions et déterminisation (33 à 37, 52)

- **ε-fermeture** : parcours des ε-transitions. **Déterminisation** : construction des
  sous-ensembles, à partir de la fermeture de l'état initial, en ne créant que les sous-ensembles
  accessibles. Le résultat est un DFA complet (l'ensemble vide est le puits). O(2^|Q|·|Σ|) au pire.
- **Suppression des ε** : δ'(p, a) = fermeture(δ(fermeture(p), a)) ; p devient final si sa
  fermeture contient un état final.
- **Miroir** : on inverse toutes les transitions. Comme un NFA n'a qu'un état initial, on ajoute un
  état `init` avec des ε-transitions vers les anciens états finaux. O(|Q| + |E|).

## 6. Opérations sur les langages (45 à 48)

- **Concaténation** : les états des deux automates sont renommés `(0, q)` et `(1, q)` ; chaque état
  final du premier reçoit une ε-transition vers l'état initial du second.
- **Étoile** : un nouvel état à la fois initial et final, avec une ε-transition vers l'ancien état
  initial, et une ε-transition de chaque ancien état final vers lui.
- **Quotient à gauche** par u : on lit u depuis l'état initial, les états atteints deviennent les
  points de départ. **Quotient à droite** par dualité : miroir, quotient à gauche par le mot
  renversé, miroir.

## 7. Expressions régulières (49, 51, 53, 54, 57, 58)

- **Arbre immuable** avec des constructeurs qui **simplifient** : l'union est associative,
  commutative et idempotente (opérandes triés, sans doublon), ε est neutre pour la concaténation,
  ∅ est absorbant, (r\*)\* = r\*. Ces règles garantissent que l'ensemble des dérivées d'une
  expression est **fini**.
- **Dérivée de Brzozowski** : d_a(b) = ε si a = b, d_a(r|s) = d_a(r)|d_a(s),
  d_a(rs) = d_a(r)s | d_a(s) si r contient ε (d_a(r)s sinon), d_a(r\*) = d_a(r)r\*. Un mot est accepté
  quand la dérivée par ce mot contient ε. **Automate des dérivées** : les états sont les dérivées.
- **Thompson** : chaque opérateur devient un petit automate avec une entrée et une sortie, reliés
  par des ε-transitions. Au plus deux fois plus d'états que la taille de l'expression. O(taille).
- **Automate vers expression, par élimination d'états** : on passe par un GNFA normalisé
  (transitions étiquetées par des expressions). Supprimer l'état s remplace chaque étiquette
  p → q par `r(p,s) r(s,s)* r(s,q) | r(p,q)`. O(|Q|³) opérations sur les expressions.
- **Automate vers expression, par le lemme d'Arden** : un système d'équations X_q = a·X_p | … | ε
  (une équation par état) est résolu par élimination de Gauss, avec X = A·X | B ⇒ X = A\*·B.
  `EquationSystem.solve()` donne l'expression de **chaque** état. O(|Q|³).

## 8. Grammaires (55, 56)

- **Grammaire régulière vers automate** : un non-terminal devient un état ; `A → aB` donne la
  transition A –a→ B, `A → a` une transition vers un état final unique, `A → ε` une ε-transition.
  Les règles à plusieurs terminaux créent des états intermédiaires. **Automate vers grammaire** :
  l'opération inverse (`p → a q` par transition, `p → ε` par état final).
- **Analyse d'une grammaire algébrique** : une table donne, pour chaque non-terminal et chaque
  partie [i, j) du mot, un arbre de dérivation. On la remplit des parties courtes aux longues, et
  on la complète jusqu'à stabilité pour chaque partie : cela gère les règles vides, les règles
  unitaires (même cycliques) et la récursivité à gauche. Valable pour toute grammaire,
  ambiguë ou non. Polynomial : O(n^(k+1)·|P|) pour des membres droits d'au plus k symboles.
- **Dérivations** : lues sur l'arbre. La dérivation gauche suit un parcours en profondeur (enfants de
  gauche à droite), la dérivation droite le parcours inverse.
  `ParseTree.from_leftmost_derivation` reconstruit l'arbre d'une dérivation donnée.

## 9. Objets algébriques (59 à 62)

- **Classes de Myhill-Nerode** : elles correspondent aux états du DFA minimal ; chaque classe est
  représentée par son mot le plus court (parcours en largeur), et son quotient est le quotient à gauche
  par ce mot.
- **Automate résiduel canonique** : un résiduel (quotient à gauche) est *premier* s'il n'est pas
  l'union des résiduels qu'il contient strictement. Un état par résiduel premier ; transition sur a de R
  vers les résiduels premiers inclus dans a⁻¹R ; états initiaux : les résiduels premiers inclus dans
  le langage ; états finaux : ceux qui contiennent ε. Chaque état reconnaît exactement son résiduel.
  Il peut être bien plus petit que le DFA minimal (4 états contre 8 dans l'exemple du README).
- **Morphismes** : une application des états qui conserve l'état initial, la finalité et les
  transitions (existence comprise). `merge_states` fusionne les blocs d'une congruence et renvoie la
  projection ; `minimization_morphism` est la projection sur le DFA minimal ; `morphism_to` cherche le
  morphisme en explorant les deux automates en parallèle (l'image de chaque état est imposée).
- **Monoïde syntaxique** : chaque mot induit une transformation des états du DFA minimal. On engendre
  toutes les transformations par un parcours en largeur sur les lettres. Le produit de deux éléments est
  l'élément de la concaténation. Au plus |Q|^|Q| éléments (en pratique bien moins). Le monoïde est
  **apériodique** exactement quand le langage est « sans étoile » (théorème de Schützenberger).

## 10. Visualisation (40, 41)

- **DOT** : produit en Python pur, de façon déterministe (états triés par nom lisible).
- **SVG, PDF, PNG** : le programme `dot` de Graphviz est appelé en sous-processus.
- **TikZ** : Graphviz calcule la disposition (`dot -Tplain`), puis chaque état devient un cercle, chaque
  transition une courbe de Bézier suivie d'une pointe de flèche dessinée à la main. Le résultat n'a besoin
  que du paquet LaTeX `tikz`.
