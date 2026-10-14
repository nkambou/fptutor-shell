# Configuration d'une instance

Quatre endroits, et un seul par type de réglage. Tout ce qui touche au contenu
pédagogique est dans le répertoire de l'instance ; la coquille n'est pas à
modifier pour configurer un tuteur.

## 1. Exercices : `exemples/<instance>/activities_<langue>.py`

`ACTIVITES` donne les ancrages servis en phase d'instance, `REEMPLOIS` ceux
servis après la généralisation. Un ancrage est un quintuplet :

    (identifiant, énoncé, signature, amorce, [(expression de test, valeur attendue), ...])

L'ordre du fichier est l'ordre de service : `prochaine_activite` sert le premier
ancrage de la famille que l'apprenant n'a pas encore reçu. Changer l'ordre se
fait en déplaçant les tuples.

Trois règles pour l'énoncé. Il ne nomme jamais le schéma visé, sans quoi la
découverte n'a plus d'objet. Il nomme les fonctions auxiliaires que l'apprenant
doit employer. Il dit ce qui est demandé, pas comment l'écrire.

L'amorce porte les déclarations de types ou de structures, le préambule, et la
définition à compléter. En Racket, l'analyse dépend des déclarations `struct` de
l'amorce, puisque ce sont elles qui disent quel accesseur désigne quel champ.

Les expressions de test sont exécutées par le compilateur réel et leur sortie
est comparée ligne à ligne. Une valeur attendue s'écrit comme le langage
l'affiche : `#f` en Racket, `None` en OCaml, `(1 2 4)` pour une liste Racket.

Après toute modification, les solutions de référence correspondantes sont à
mettre à jour dans `compiler_references.py` du même répertoire, puis la batterie
à relancer.

## 2. Familles et paliers : `exemples/<instance>/referentiel.json`

    reglages          instances_min, instances_max, reemploi_requis,
                      seuil_correction_pour_alignement, guidage_apres_echec
    paliers[].concepts  id, libellé, prérequis, famille, generalisation,
                      acquisition, reuse
    familles[]        règle, axes de variation autorisés et interdits,
                      ancrages (exemple, base, pas), obligation,
                      solution de référence, validation

`reglages.instances_min` est le nombre de solutions comparables avant que
l'atelier puisse s'ouvrir, `instances_max` le plafond d'exercices servis, et
`reemploi_requis` le nombre de réemplois avant le passage au palier suivant.

`familles[].validation` annonce `{mode, granularite, attendu}` : le nombre de
points de variation que la famille doit présenter. La console le contrôle à
chaque démarrage. Une famille non conforme produit un plateau, c'est-à-dire une
phase d'abstraction ouverte sur un corpus dont il n'y a rien à extraire.

`generalisation.points_de_variation_attendus` et `granularite` décident de ce
que l'atelier demande à l'apprenant d'écrire.

## 3. Aide et étayage

Trois niveaux au plus, `NIVEAUX_MAX = 3` dans `noyau.py`. Le niveau 1 est
toujours le texte de la catégorie d'erreur ; les niveaux 2 et 3 concatènent le
texte de la catégorie et celui de la famille, quand les deux existent.

La **lecture immédiate** du message du compilateur n'est pas un indice et ne
compte pas dans l'étayage : elle dit en français ce que le compilateur vient de
signaler.

Les textes sont attachés à six catégories communes : `missing-base-case`,
`incompatible-types`, `unknown-name`, `syntax`, `wrong-result`,
`unclassified`. Les catégories sont communes à tous les langages, les textes
non : ceux de la coquille parlent de GHCi, d'équations et de listes.

Le fournisseur de langage déclare donc, dans `language_<langue>.py` :

| Attribut | Rôle |
|---|---|
| `AIDES_ERREUR` | trois niveaux d'indices par catégorie, remplaçant ceux du cadre |
| `LECTURES` | la lecture immédiate, une ligne par catégorie |
| `squelette(forme)` | la charpente du mode exposé, dans la syntaxe du langage |
| `reemploi(nom, code)` | ce qui compte comme emploi du schéma plutôt que récursion explicite |

Ce que le fournisseur ne déclare pas garde le texte du cadre, catégorie par
catégorie. `exemples/rackettutor/language_rkt.py` montre les quatre attributs
écrits en entier et sert de modèle.

Les indices propres à une famille sont dans `AIDES_FAMILLE` de `noyau.py`, pour
les familles sur les listes. Une famille nouvelle sans entrée reçoit les textes
de catégorie seuls, ce qui convient.

## 4. Politique : contrats, depuis la console

Concept par concept, en séance et sans redémarrage, sur `/enseignant`. Les
valeurs par défaut sont celles de `DEFAUT_CONTRAT` dans `serveur.py`.

| Réglage | Valeurs | Défaut |
|---|---|---|
| `assistance` | `none`, `on-request`, `guidance` | `on-request` |
| `abstraction` | `discovery`, `guided`, `exposed` | `discovery` |
| `regime` | `free`, `solo`, `pair`, `team` | `free` |
| `sequence` | `free`, `must-complete` | `free` |
| `off_form` | `explain_and_rewrite`, `explain_and_continue`, `confront` | `explain_and_continue` |
| `verification` | `never`, `on-doubt`, `always` | `on-doubt` |
| `delai_minutes` | entier | `0` |

`assistance: none` met le plafond d'aide à zéro, ce qui éteint les trois
niveaux. `off_form` décide du sort d'une solution juste mais non comparable,
par exemple un pli de bibliothèque : expliquer et conserver à part, demander une
réécriture, ou confronter l'apprenant à la différence.

## Ce qui ne se configure pas

La décision d'ouvrir l'atelier, l'anti-unification et le vocabulaire commun des
termes. Ce sont les parties communes à toutes les instances : les modifier
change le dispositif lui-même, pas sa configuration.
