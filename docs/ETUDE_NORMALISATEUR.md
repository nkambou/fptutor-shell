# Où va l'effort d'une instanciation, et ce qui serait factorisable

Mesures prises sur les quatre analyseurs existants, lignes de code sans lignes
vides, commentaires ni docstrings. La question posée : la coquille engendre la
politique, l'alignement, le service et les interfaces, mais pas la lecture du
langage ; cette dernière est-elle irréductible ?

## Répartition mesurée

| Rôle | OCaml | Racket | Python | Haskell |
|---|---|---|---|---|
| Lecture du texte vers un arbre | 244 | 104 | 0 | 39 |
| Reconnaissance des formes du langage | 27 | 76 | 0 | 79 |
| Rendu dans le vocabulaire commun | 51 | 67 | 63 | compris ci-dessus |
| Sélection du cas de base et du pas | 32 | 39 | 61 | compris ci-dessus |
| Règle de réemploi | dans l'extension | 30 | 0 | 0 |
| **Total de l'analyse** | **375** | **317** | **124** | **118** |

Python n'a aucune ligne de lecture parce que le module `ast` lui donne l'arbre.
Haskell en a trente-neuf parce que l'analyseur hérité découpe des équations par
expressions régulières, sans construire d'arbre. OCaml en a deux cent
quarante-quatre parce que l'instance réécrit un analyseur syntaxique d'OCaml en
Python.

**Deux tiers du coût de l'instance OCaml tiennent à l'obtention de l'arbre, et
rien de ce travail n'est pédagogique.**

## Ce qui est déjà identique d'une instance à l'autre

La sélection du cas de base et du pas est la même fonction, à une ligne près.
Dans les deux instances elle s'écrit : les équations contenant `REC` sont les
cas récursifs, les bases sont les autres, le pas est la première équation
récursive. Seul diffère le test qui reconnaît une valeur vide, `None` pour
OCaml, `#f` ou la liste vide pour Racket.

Le rendu est la même construction : projeter les champs du motif sur `C1`,
`C2`, remplacer l'appel récursif par `REC`, rendre les opérateurs en infixe,
normaliser la commutativité de l'addition et du produit. Seule diffère la table
des opérateurs, une dizaine de lignes de données.

La reconnaissance des formes, en revanche, n'est pas factorisable : qu'une
distinction de cas s'écrive `match`, `cond`, un prédicat ou des gardes est
propre au langage, et aucune déclaration ne l'engendre.

## Première proposition : un moteur commun de termes

Un module de la coquille prendrait un arbre sous forme de listes et une
déclaration du fournisseur, puis rendrait le terme canonique et la sélection
base/pas. Le fournisseur déclarerait :

    OPERATEURS   = {"+": "+", "*": "*", "@": "@", "::": "::"}
    COMMUTATIFS  = ("+", "*")
    VIDES        = ("None", "[]")
    ACCESSEURS   = ...        # comment un champ se lit dans ce langage

D'après les mesures, ce moteur absorberait le rendu et la sélection, soit
quatre-vingt-trois lignes de l'instance OCaml et cent six de l'instance Racket.
C'est un quart environ d'un analyseur, et c'est une estimation tirée du
découpage ci-dessus, non un résultat mesuré sur une implantation.

Une instance nouvelle resterait donc à quelques centaines de lignes. **Le gain
est réel et il est modeste : il ne transforme pas l'instanciation en
déclaration.**

## Seconde proposition : ne plus écrire d'analyseur syntaxique

Le vrai poste de dépense est ailleurs. L'instance OCaml contient un analyseur
syntaxique d'OCaml écrit en Python, alors que chaque langage visé sait déjà lire
sa propre syntaxe.

Un petit programme écrit dans le langage cible, appelé en sous-processus, peut
rendre l'arbre sous une forme commune, par exemple une s-expression imprimée sur
la sortie standard. Le fournisseur Python s'en passe déjà, par `ast`. En Racket,
`read` fait le travail en une ligne et rendrait inutile un lecteur de soixante
trois lignes. En OCaml, une vingtaine de lignes employant `compiler-libs`
remplaceraient deux cent quarante-quatre lignes.

Autrement dit : **la coquille ne doit pas apprendre à lire les langages, elle
doit leur demander de se lire eux-mêmes.** Le fournisseur se réduirait alors à
un programme de vidage de l'arbre, une déclaration et la reconnaissance des
formes, soit de l'ordre de cent cinquante lignes au lieu de quatre cents.

## Conséquence pour l'article sur la généricité

L'affirmation qu'un tuteur s'engendre presque sans effort n'est pas soutenue par
les mesures : quatre cent quarante lignes pour Racket, quatre cent quarante-cinq
pour OCaml. Elle le serait davantage après ces deux changements, et elle l'est
déjà quand l'analyse préexiste, comme le montre l'instance Haskell avec
quatre-vingt-quatre lignes.

La formulation juste est donc : la coquille porte tout ce qui est commun, et le
coût résiduel d'une instance est celui de la lecture du langage, lequel dépend
de ce que ce langage offre pour se lire lui-même.

## Limites

Les chiffres portent sur les instances telles qu'elles sont écrites, et non sur
ce qu'elles pourraient être : un analyseur plus compact aurait d'autres totaux.
L'estimation du gain du moteur commun est une projection, pas une mesure ; elle
n'est pas éprouvée tant qu'une instance n'a pas été réécrite dessus. Et le gain
du vidage d'arbre suppose que le langage cible est disponible sur le serveur, ce
qui est déjà le cas puisque les soumissions y sont compilées.

## Résultat de l'expérience

Les deux propositions ont été mises en œuvre sur l'instance Racket et mesurées.

`moteur_termes.py`, dans la coquille, porte le rendu et la sélection du cas de
base, pilotés par une déclaration : table des opérateurs, commutatifs,
associatifs à droite, cas vides, atomes, et noms des formes conditionnelles, de
liaison et d'abstraction. Quatre-vingts lignes, partagées par toutes les
instances.

`vidage.rkt`, dix-neuf lignes de Racket, demande à Racket de lire sa propre
syntaxe et rend l'arbre en JSON. Le lecteur de s-expressions écrit en Python
disparaît.

`normalisation_rkt2.py` est l'analyseur Racket réécrit sur ces deux pièces. Il
ne contient plus que ce qui ne se déclare pas : repérer les structures et les
définitions, et reconnaître ce qui tient lieu de distinction de cas.

| | v1 | v2 |
|---|---|---|
| Analyseur de l'instance | 317 | 173 |
| Vidage dans le langage cible | 0 | 19 |
| **Total dans l'instance** | **317** | **192** |
| Moteur commun, dans la coquille | 0 | 80 |

**Trente-neuf pour cent de l'analyseur de l'instance disparaissent**, et ce qui
reste dans la coquille est partagé par les instances suivantes.

L'équivalence a été vérifiée, non supposée. Les deux versions rendent exactement
la même forme, la même base et le même pas sur les vingt-trois écritures des
deux jeux de cas et sur les quinze solutions de référence : zéro écart. Le banc
rend les mêmes verdicts, réunion de huit écritures en un terme pour les arbres,
de six pour l'absence, séparation vérifiée dans les deux cas.

## Le coût en temps, et sa correction

Le vidage lance Racket à chaque analyse : trois cent trente-quatre millisecondes
contre moins d'une avec le lecteur en Python. Sur un alignement de cinq
solutions relu à chaque décision, c'est inacceptable.

Une solution déposée ne change plus, et l'alignement relit le même corpus : le
résultat du vidage est donc gardé en mémoire, indexé par le texte soumis. Le coût
tombe alors à un vidage par soumission, soit un tiers de seconde une fois, à
côté d'une compilation qui en coûte déjà autant. Après le premier passage, les
passages suivants sur les quinze références prennent une demi-milliseconde au
total.

## Ce que l'expérience ne règle pas

Le moteur commun travaille sur un arbre en listes. L'instance Racket s'y prête
parce que `read` rend exactement cela ; l'instance OCaml devrait d'abord convertir
son arbre, et le gain y est à vérifier. Les deux cent quarante-quatre lignes de
son analyseur syntaxique ne tomberaient qu'avec un vidage écrit en OCaml, par
`compiler-libs`, ce qui reste à faire.

La reconnaissance des formes du langage, soixante-seize lignes en Racket, n'a pas
bougé et ne bougera pas : c'est la part irréductible, celle qui sait que Racket
distingue les cas par des prédicats.

## Suite

Le contrôle qui a transformé l'estimation en mesure est fait, et il est
reproductible :

    python3 - <<'EOF'
    import json, sys; sys.path.insert(0, "exemples/rackettutor")
    import normalisation_rkt as V1, normalisation_rkt2 as V2
    for f in ("cas_rkt.json", "cas_rkt_option.json"):
        cas = json.load(open("exemples/rackettutor/" + f))
        for g in ("equivalentes", "distinctes"):
            for c in cas[g]:
                a, b = V1.analyser(cas["fonction"], c["code"]), V2.analyser(cas["fonction"], c["code"])
                assert (a["forme"], a.get("base"), a.get("pas")) == (b["forme"], b.get("base"), b.get("pas")), c["etiquette"]
    print("aucun ecart")
    EOF

Reste à porter le même traitement à l'instance OCaml, où le gain attendu est le
plus grand, et à décider si la seconde version remplace la première ou reste une
expérience documentée. Tant que l'expérimentation est en cours, elle reste une
expérience : l'instance servie aux étudiants ne change pas.
