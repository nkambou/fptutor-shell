# RacketTutor : troisième instanciation de FPTutor-Shell, sous protocole

Instanciation conduite selon `mesures/PROTOCOLE_instanciation.md`, rédigé et
horodaté avant la première ligne du fournisseur. Les observations sont
consignées dans `mesures/observations.md` dans l'ordre où elles ont été faites,
chacune avant sa correction.

## Base, variation éprouvée, contenu tenu constant

Base : FPTutor-Shell v2 (SHA-256 de l'archive `5cb93223…092fee18`), 27 fichiers
de coquille dont les empreintes sont relevées avant et après
(`mesures/empreintes_coquille_*.txt`). Interprète : Racket 8.10 [cs], réel.

Racket éprouve trois variations absentes de Haskell, de Python et d'OCaml : le
typage dynamique ; l'absence de types sommes, les arbres étant des structures
distinguées par prédicats (`leaf?`) et lues par accesseurs (`node-l`) ; le
déplacement des erreurs de forme de la compilation vers l'exécution.

Le contenu pédagogique est celui d'OCamlTutor, sans changement : concepts
`arbre-pli` et `option-chaine`, familles `F-arbre` et `F-option` du laboratoire
05 d'INF6120, neuf ancrages, six réemplois, mêmes valeurs attendues. Les écarts
entre les deux instances tiennent donc au langage.

## Critères de réussite

| critère | résultat |
|---|---|
| C1 banc d'essai | arbre : 14 écritures, 6 termes, réunion (8) et séparation vérifiées, 10 messages projetés correctement ; absence : 9 écritures, 4 termes, réunion (6) vérifiée |
| C2 références sous Racket réel | 15 sur 15, du premier coup |
| C3 familles | F-arbre 2 points pour 2 annoncés, F-option 1 pour 1, par la console sans modification |
| C4 essai à blanc | séquence identique à OCaml ; 3 sondes de mesure de réemploi exactes ; passage au palier suivant |
| C5 service HTTP | titres, compilateur annoncé, inscription, soumission, étayage et console vérifiés |
| C6 couche commune inchangée | `remontee.py` et `etat_alignement` inchangés ; `decider` modifié par une correction indépendante du langage (O12) |

## Résultat 1 : la reconnaissance transfère sans perte

Le normalisateur lit les déclarations `struct` de la soumission et projette
chaque accesseur sur l'étiquette de son champ. `(node-v t)` et la variable `v`
liée par le motif `(node v l r)` de racket/match rendent toutes deux `C1`. Huit
écritures de la somme sur l'arbre se réunissent en un terme : `cond` sur le cas
vide ou sur le nœud d'abord, `if`, `match`, branches inversées, autres noms,
définition par `lambda`, deux prédicats explicites, et l'ordre libre des
opérandes d'une somme n-aire.

Sur la famille de l'absence, six écritures idiomatiques de Racket se réunissent
en un terme : `(if x A #f)`, `(if (not x) #f A)`, `(and x A)`, `cond`,
`(match … [#f #f] [x A])`, opérandes échangés. OCaml n'en a qu'une naturelle.

Formes canoniques des neuf ancrages, OCaml et Racket :

| ancrage | OCaml (base / pas) | Racket (base / pas) | |
|---|---|---|---|
| count-leaves | 1 / (REC + REC) | 1 / (REC + REC) | = |
| count-internal-nodes | 0 / ((1 + REC) + REC) | 0 / ((1 + REC) + REC) | = |
| sum | 0 / ((C1 + REC) + REC) | 0 / ((C1 + REC) + REC) | = |
| height | 0 / (1 + (max REC REC)) | 0 / (1 + (max REC REC)) | = |
| collect-values | [] / (REC @ (C1 :: REC)) | [] / (REC @ (C1 :: REC)) | = |
| double-tete | NOTHING / (Some (2 * C1)) | NOTHING / (2 * C1) | idiome |
| cent-sur-tete | NOTHING / (division 100 C1) | NOTHING / (division 100 C1) | = |
| pipeline | NOTHING / (CASE (division 100 n) NOTHING) | NOTHING / (CASE (division 100 C1) NOTHING) | voir note |
| longueur-premiere | NOTHING / (Some (String.length C1)) | NOTHING / (string-length C1) | idiome |

Les cinq ancrages de l'arbre rendent le même terme dans les deux langages. Les
écarts de la famille de l'absence tiennent à l'idiome : OCaml enveloppe la
valeur présente dans `Some`, Racket la rend nue. La ligne `pipeline` révèle une
incohérence du normalisateur OCaml, qui laisse la variable du filtrage imbriqué
sous son nom (`n`) au lieu de l'étiqueter.

Conséquence mesurable : l'alignement, les points de variation et l'induction des
obligations sont identiques dans les deux langages, ancrage par ancrage.
L'inducteur ne désigne aucun ancrage porteur dans la famille `F-arbre` actuelle,
en blocs comme en granularité fine ; l'ancre `aplatir` du rapport OCaml portait
sur une version antérieure de la famille. L'obligation du référentiel est
réécrite en conséquence.

La syntaxe préfixe n-aire rend la commutativité moins coûteuse qu'en syntaxe
infixe : trier les opérandes d'une somme plate suffit, sans règle d'appoint.

## Résultat 2 : le typage dynamique déplace l'erreur, pas la catégorie

Les six catégories communes suffisent. Un cas de base absent, signalé à la
compilation par OCaml, se manifeste en Racket à l'exécution d'un test, sous
trois signatures : un `match` sans clause, un accesseur appliqué à la structure
vide, une valeur `#<void>` rendue par un `cond` sans issue. Toutes trois se
projettent sur `missing-base-case`. La catégorie survit ; son moment change, et
les textes d'aide doivent le dire (« l'exécution a rencontré », non « le
compilateur signale »).

## Résultat 3 : ce qui a cédé

Sept modifications de la coquille, numérotées à la suite des sept de la v2 et
détaillées dans `LISEZMOI_v3.md` à la racine.

**Trois fuites du langage.** Le banc éprouvait tout fournisseur sur des messages
de GHC (O6). L'inducteur d'obligations ignorait le fournisseur et rendait, sans
avertissement, les obligations des familles Haskell (O7). L'échelle d'étayage,
les lectures immédiates et la charpente du mode exposé sont écrites pour
Haskell et pour les listes : sous Racket, un cas de base absent recevait « il
vous manque une équation dont le motif est [] », une erreur de type « demandez à
GHCi le type avec :t », une parenthèse manquante une consigne d'indentation
(O11). Les catégories sont communes ; les textes qui leur sont attachés ne
l'étaient pas. Avec les six de la v2, neuf fuites en trois instanciations.

**Un défaut de mesure récurrent.** Les deux faux positifs de la mesure de
réemploi trouvés par OCaml réapparaissent sur Racket : une enveloppe autour d'une
récursion écrite à la main, et une forme que l'analyse ne lit pas
(`define/contract`), toutes deux comptées comme réemploi (O9). OCaml les avait
corrigés dans son instance, non dans la coquille. **Une correction faite dans
une instance ne protège pas la suivante** : elle doit remonter dans la coquille,
et l'instanciation suivante est le seul contrôle qui le vérifie.

**Un défaut de la couche de politique, indépendant du langage.** La condition
de stabilité était neutralisée par toute lecture de l'état (O12). `decider`
enregistre le compte d'alignement à chaque appel, `vue_apprenant` l'appelle à
chaque lecture, et la page étudiante relit l'état après chaque soumission
réussie. À la troisième solution, la soumission annonce « le tuteur vérifie sur
une solution de plus », puis la relecture compare le compte à lui-même et ouvre
l'atelier. Sonde HTTP (`sonde_http.py`) : sur la coquille v2, atelier ouvert à
la solution 3 avec relecture et 4 sans ; après correction, 4 dans les deux cas.
L'essai à blanc, qui appelle `decider` une fois par soumission, ne pouvait pas
le voir. Les ablations de l'article TLT, calculées sur le générateur, ne sont
pas affectées ; le système servi l'était, dans toutes ses instances.

**Des défauts de l'atelier.** Gabarit d'activités à quatre éléments quand le
noyau en lit cinq (O2), référentiel non copié et silence sur l'omission (O1),
commande de lancement inexistante (O3), vérification finale renvoyant à un
outil lié à Haskell (O8), banc exigeant la séparation entre formes que le corpus
refuse de toute façon (O4).

**Deux points d'extension facultatifs du fournisseur**, par lesquels passent les
corrections O9 et O11 : `reemploi(nom, code)`, et `AIDES_ERREUR`, `LECTURES`,
`squelette`. Un fournisseur qui ne les déclare pas garde le comportement du cadre,
rendu prudent pour la mesure (une forme non analysable n'est jamais un réemploi).

Deux corrections restent locales au fournisseur : la commutativité, d'abord
calquée sur OCaml et limitée aux appels récursifs (O5), et la projection de
l'accesseur appliqué à une feuille, que le jeu de cas ne couvrait pas parce que
son message avait été relevé sur une structure opaque et non `#:transparent`
(O10). Le banc ne vaut que par les messages qu'on lui donne : ils doivent être
relevés sur l'interprète, avec les déclarations mêmes de l'amorce.

## Mesures

**M1, lignes de code** (non vides, hors commentaires et docstrings,
`mesures/compter.py`) :

| élément | Racket | OCaml |
|---|---|---|
| normalisateur | 317 | 375 |
| dont lecteur de s-expressions | 63 | (analyseur inclus) |
| dont structures et accesseurs | 41 | sans objet |
| dont rendu en vocabulaire commun | 67 | |
| dont distinction des cas et analyse | 115 | |
| dont règle de réemploi | 30 | dans l'extension de suivi |
| fournisseur (`language_*.py`) | 126 | 70 |
| dont identification, exécution, catégorisation | 38 | |
| dont textes d'étayage et charpente | 66 | absents |
| ancrages et réemplois (contenu d'auteur) | 156 | 178 |
| références exécutées | 67 | 62 |
| essai à blanc | 136 | 95 |
| adaptateur de validation des familles | 0 | 67 |
| jeux de cas du banc (JSON) | 2 fichiers | 1 fichier |

Modifications de la coquille : `noyau.py` +36 −4, `serveur.py` +1 −1,
`obligations.py` +45, `banc_essai.py` +13 −7, `creer_tuteur.py` +37 −30,
`gabarit_language.py` +11. Six fichiers modifiés sur 27, vingt et un inchangés.

**M3, modifications forcées** : sept, classées ci-dessus, chacune précédée de
son échec observé.

**M4, réemploi de l'instance OCaml.** Repris et adaptés : le référentiel
(transformation scriptée), la structure des ancrages et leurs énoncés, le
script des références, l'essai à blanc, la structure du jeu de cas. Écrits de
novo : le normalisateur, la catégorisation, les textes d'étayage, le jeu de cas
de l'absence, la sonde HTTP.

## Limites

**M2 n'a pas produit de donnée exploitable.** Le journal des temps existe, mais
une instanciation conduite par un agent automatique mesure la latence entre ses
appels d'outils et non un effort d'auteur ; l'étape E8 contient en outre
l'intervalle entre deux tours de conversation. C'est un écart au protocole, à
corriger pour la quatrième instance : le coût en temps doit être mesuré sur un
auteur humain, selon le même protocole.

**Écriture du fournisseur par l'agent.** Le nombre de lignes est un résultat
robuste ; la facilité apparente de l'écriture ne l'est pas, et ne se transpose
pas à un auteur qui découvre la coquille.

**Deux familles seulement**, toutes deux en récursion structurelle, et aucune
sur les listes. La couverture de l'analyse se limite au sous-ensemble de Racket
exercé par ces familles (`struct`, `define`, `define/contract`, `cond`, `if`,
`match`, `let`, `and`) ; `for`, le `let` nommé et les fonctions d'ordre
supérieur de la bibliothèque sont reconnus et écartés du corpus.

**Bilinguisme.** Les textes d'étayage déclarés par le fournisseur sont en
français et n'ont pas d'équivalent dans le catalogue de traduction.

**Restes connus** : `generateur.py` demeure lié à l'analyseur Haskell ;
`relancer.sh` à la racine vise OCamlTutor ; les scripts de l'instance OCaml
supposent l'ancienne arborescence (`valider_familles_ml.py` demande
`PYTHONPATH` à la racine). L'instance OCaml ne déclare pas encore de textes
d'étayage et reçoit donc toujours ceux du cadre.

## Reproduire

    apt-get install -y racket          # 8.x
    cd FPTutor-Shell
    python3 exemples/rackettutor/compiler_references.py
    cd fptutor-shell && python3 banc_essai.py language_rkt --tuteur exemples/rackettutor \
        --cas ../exemples/rackettutor/cas_rkt.json && cd ..
    TUTOR_DIR=exemples/rackettutor TUTOR_LANGUAGE=language_rkt python3 obligations.py
    python3 exemples/rackettutor/essai_a_blanc.py
    TUTOR_DIR=exemples/rackettutor TUTOR_LANGUAGE=language_rkt PORT=8093 python3 serveur.py &
    python3 exemples/rackettutor/sonde_http.py http://localhost:8093
