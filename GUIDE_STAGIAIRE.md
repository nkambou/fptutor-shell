# Guide du stagiaire : préparer l'expérimentation OCamlTutor

## Objet du stage

OCamlTutor est expérimenté dans les séances de laboratoire du cours INF6120. L'expérimentation se déroule en deux créneaux courts de vingt minutes pris en séance mais aussi en ligne pour les étudiants à distance. Votre travail
est de rendre l'instance OCaml prête pour ces créneaux : exercices proposés au
laboratoire du cours, textes d'aide écrits pour OCaml, réglages de politique
arrêtés, validation du comportement du système, etc.

Vous ne travaillez pas sur la coquille. Si un réglage demande de la modifier, il faut en discuter au préalable.

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

### 1. Arrimer les exercices au laboratoire 05 du cours (https://inf6120.uqam.ca/labos/labo05/)

`docs/CONCORDANCE_LABO.md` donne l'état de la concordance, ancrage par ancrage,
et les écarts à traiter. Le type et les noms concordent déjà ; les exercices
servis, non : `bintree_sum` ne figure pas au laboratoire, l'ordre de service ne
suit pas celui des sections, et les quatre réemplois sont à remplacer par les
deux que demande la dernière section du laboratoire.

Commencez par là, puis vérifiez un par un : énoncés, amorces, valeurs attendues.
L'étudiant doit reconnaître son laboratoire sans hésiter.

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

### 3. Monter les deux phases du réemploi

`docs/SEANCE2.md` en donne le plan. Le point à comprendre avant de toucher au
fichier : le pool `REEMPLOIS` est servi dès l'ouverture de l'atelier, donc son
contenu décide de ce qui est mesuré avant que l'enseignant ait présenté
`fold_tree` en classe.

Avant la première séance, le pool ne contient qu'un exercice, le transfert sans
consigne de méthode, qui porte la mesure principale. Les exercices qui nomment
`fold_tree` et le second transfert s'ajoutent à la bascule, la veille du
laboratoire 06, par mise à jour du fichier et relance conservant l'état.

Éprouvez la bascule sur une copie d'essai : ajouter un exercice en cours de
route ne doit rien changer à un dossier déjà constitué. Chronométrez aussi les
exercices du second créneau avant de les figer.

Deux options d'exposition sont préparées, décrites dans
`docs/OPTIONS_EXPOSITION.md`, et l'une sera retenue après discussion avec
l'enseignant. Elles ne changent ni les exercices ni les réglages : seuls le
libellé de la première question du questionnaire et une variable d'analyse en
dépendent. Montez les deux libellés, et n'en activez qu'un, une fois la décision
consignée.

Ne touchez pas à `reemploi_requis`, qui vaut deux : en phase 1, le tuteur
annoncera un réemploi sur deux et s'arrêtera là, et c'est le comportement voulu.
N'ajoutez aucun verrou de date dans la coquille. Et ne déposez pas le corrigé de
la dernière section du laboratoire dans ce dépôt.

### 4. Arrêter les réglages de politique

Proposez des valeurs pour les deux créneaux, et sachez les justifier. Le point de
jugement est `off_form` : que faire d'une solution juste mais non comparable.
Essayez les trois valeurs sur une session complète avant de choisir.

### 5. Éprouver avant la séance

- La batterie complète
- Une session complète par l'interface, du premier exercice au réemploi.
- Une session avec une erreur de chaque catégorie, pour lire les six textes.
- Un essai à plusieurs postes en même temps, pour voir le service tenir.
- Un essai dans une salle du LAMISS, avec le compte d'un étudiant (à voir avec le démonstrateur - son compte plutôt que celui d’un étudiant??)

## Le noyau commun, gelé pendant l'expérimentation

`remontee.py` et les fonctions `decider` et `etat_alignement` de `noyau.py` sont
le mécanisme que l'expérimentation mesure. Les ablations publiées et les
comparaisons entre les instances OCaml, Racket et Python portent sur cette
version du code : la modifier rend les données de la séance incomparables au
reste.

Vous restez libre de les lire, de les instrumenter, d'écrire des tests, et de
proposer une correction sur une branche séparée. Si vous y trouvez un défaut,
signalez-le, et nous déciderons ensemble de corriger avant ou
après l'expérimentation. Le seul geste à éviter est un changement non signalé
dans la branche servie aux étudiants.

Tout le reste de l'environnement est le vôtre : exercices, textes d'aide,
référentiel, fournisseur de langage, scripts de vérification, outillage.

## Les trois autres règles

- Ne versionnez jamais `etat.json`, `journal.jsonl` ni un export : ce sont des
  données de séance, et `.gitignore` les exclut déjà.
- Ne remettez pas l'état à zéro quand `COLLECTE_EN_COURS` existe dans le
  répertoire de l'instance : ce fichier protège les données d'une séance.
- Ne servez jamais le substitut de compilateur à des étudiants. S'il est actif,
  le bandeau « MODE ESSAI » le dit.

## Rôle en séance

Vous serez présente aux deux créneaux. Deux personnes dans la salle : l'auxiliaire du cours prend les problèmes de salle et de
compilateur (s’il y a lieu), vous prenez la console et les décisions, vous prenez les questions sur 'interface et le relevé de ce qui bloque. L’auxilliaire parle du
contenu des exercices. Un protocole sera élébaoré.

L’auxilliare vous présentera en une phrase, pour que les étudiants sachent que
vous n'êtes ni correctrice ni évaluatrice. Vous ne regardez pas les écrans
par-dessus les épaules et vous ne corrigez rien.

Vous tenez le serveur, puisque c'est vous qui l'aurez préparé. Si le service
tombe (ce qui est oeu probable), l’auxilliaire occupe la salle pendant que vous réparez, et le laboratoire reprend son cours au bout de trois minutes si la réparation échoue.

À préparer pour cela : `docs/FICHE_SALLE.md`, remplie et imprimée, et
`docs/GRILLE_RELEVE.md` pour le relevé. Faites une répétition complète dans la
salle du LAMISS, avec un compte d'étudiant (ou de l’auxilliare) et non le vôtre.

## Rendre compte

Tenez un journal court des modifications, une ligne par changement, avec
l'échec observé qui l'a motivée. Les commits séparent le contenu pédagogique
(exercices, textes) des corrections de code. Signalez immédiatement tout
comportement du tuteur qui vous surprend, même si vous l'avez contourné : les
défauts les plus intéressants ont tous été trouvés ainsi.
