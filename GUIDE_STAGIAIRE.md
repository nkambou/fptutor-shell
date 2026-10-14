# Guide du stagiaire : préparer l'expérimentation OCamlTutor

## Objet du stage

OCamlTutor est servi dans les séances de laboratoire d'INF6120. L'expérimentation
se tient en deux créneaux courts de vingt minutes pris en séance. Votre travail
est de rendre l'instance OCaml prête pour ces créneaux : exercices accordés au
laboratoire du cours, textes d'aide écrits pour OCaml, réglages de politique
arrêtés, et toute la batterie de vérification au vert.

Vous ne travaillez pas sur la coquille. Si un réglage demande de la modifier,
c'est un résultat à signaler, pas un détour à prendre.

## Prise en main

    git clone <dépôt>
    cd FPTutor-Shell
    python3 --version                 # 3.10 ou plus
    ocaml -version                    # 4.14.2, la version du cours

Si OCaml vient d'opam, `eval $(opam env)` avant toute chose. Sinon, donnez le
chemin absolu de l'interprète par `OCAML_BIN`.

Lancez la batterie, puis le serveur :

    outils/verifier.sh exemples/ocamltutor language_ml cas_ml.json
    TUTOR_DIR=exemples/ocamltutor TUTOR_LANGUAGE=language_ml PORT=8081 python3 serveur.py

Ouvrez `http://localhost:8081/`, inscrivez-vous par pseudonyme, et faites une
session entière : une soumission fausse, trois ou quatre solutions justes, une
solution par `List.fold_left`, puis l'atelier d'abstraction. Vous ne comprendrez
le reste qu'après avoir vu cela une fois.

Si le bandeau rouge « MODE ESSAI : compilateur simulé » apparaît, le serveur a
été lancé avec `OCAML_BIN` pointant sur le substitut. Arrêtez-le, corrigez la
variable, relancez : l'environnement d'un processus est figé à son démarrage.

## Comment lire le code, dans l'ordre

1. `exemples/ocamltutor/activities_ml.py` : les exercices, c'est là que votre
   travail commence.
2. `exemples/ocamltutor/referentiel.json` : familles, paliers, seuils.
3. `exemples/ocamltutor/language_ml.py` : le fournisseur de langage, cinq
   fonctions et quelques attributs facultatifs.
4. `noyau.py`, fonctions `decider`, `etat_alignement`, `aide` : la politique.
5. `remontee.py` : l'anti-unification, à lire en dernier et à ne pas toucher.

`CONFIGURATION.md` dit où se règle quoi. `exemples/rackettutor/RAPPORT_instanciation.md`
explique ce qui a cédé lors de la dernière instanciation, et vous évitera de
retrouver les mêmes défauts par vous-même.

## Travaux à mener

### 1. Accorder les exercices au laboratoire 05

Les ancrages actuels reprennent les sections « Compter », « Propriétés » et
« Collectionner ». Vérifiez un par un : noms de fonctions, type `bintree` avec
`Leaf` et `Node`, énoncés, valeurs attendues. L'étudiant doit reconnaître son
laboratoire sans hésiter.

Les créneaux font vingt minutes. L'ordre des deux ou trois premiers ancrages
décide donc de ce que la plupart des étudiants verront : placez en tête ceux qui
se résolvent vite et qui diffèrent assez pour que la comparaison ait un objet.

### 2. Écrire les textes d'aide en OCaml

C'est le travail le plus utile. L'instance ne déclare pas encore `AIDES_ERREUR`
ni `LECTURES` : un étudiant d'OCaml lit aujourd'hui des indices écrits pour
Haskell, qui parlent de GHCi, d'équations et du motif `[]`.

Écrivez les trois niveaux pour les six catégories, en suivant
`exemples/rackettutor/language_rkt.py`. Règles à tenir :

- le niveau 1 nomme ce que le compilateur signale, sans dire quoi faire ;
- le niveau 2 oriente la lecture du message ou rappelle la structure du type ;
- le niveau 3 donne la charpente, jamais le corps ;
- aucun niveau ne nomme `fold_tree`, ni le schéma, ni le mot « généralisation ».

Relisez-les à voix haute en vous mettant à la place d'un étudiant bloqué depuis
cinq minutes. Un indice qui ne débloque rien est un indice à récrire.

### 3. Arrêter les réglages de politique

Proposez des valeurs pour les deux créneaux, et sachez les justifier. Le point de
jugement est `off_form` : que faire d'une solution juste mais non comparable.
Essayez les trois valeurs sur une session complète avant de choisir.

### 4. Éprouver avant la séance

- La batterie complète au vert.
- Une session complète par l'interface, du premier exercice au réemploi.
- Une session avec une erreur de chaque catégorie, pour lire les six textes.
- Un essai à plusieurs postes en même temps, pour voir le service tenir.
- Un essai dans une salle du LAMISS, avec le compte d'un étudiant.

## À ne jamais faire

- Versionner `etat.json`, `journal.jsonl` ou un export : ce sont des données de
  séance. `.gitignore` les exclut, ne les forcez pas.
- Remettre l'état à zéro quand `COLLECTE_EN_COURS` existe dans le répertoire de
  l'instance. Ce fichier protège les données d'une séance en cours.
- Servir le substitut de compilateur à des étudiants.
- Modifier `remontee.py`, ni `decider` et `etat_alignement` dans `noyau.py`.
  Si vous croyez devoir le faire, écrivez-moi avant.

## Rendre compte

Tenez un journal court des modifications, une ligne par changement, avec
l'échec observé qui l'a motivée. Les commits séparent le contenu pédagogique
(exercices, textes) des corrections de code. Signalez immédiatement tout
comportement du tuteur qui vous surprend, même si vous l'avez contourné : les
défauts les plus intéressants ont tous été trouvés ainsi.
