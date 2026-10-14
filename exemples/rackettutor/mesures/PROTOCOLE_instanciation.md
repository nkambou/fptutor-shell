# Protocole d'instanciation de FPTutor-Shell, appliqué à Racket

Rédigé et horodaté avant la première ligne du fournisseur Racket. Toute
déviation en cours d'exécution est consignée dans le rapport, avec sa raison ;
le protocole lui-même n'est pas modifié après coup.

## Objet

Mesurer ce que coûte l'engendrement d'un tuteur pour un nouveau langage
fonctionnel à partir de FPTutor-Shell v2, ce qui reste inchangé, et ce qui
cède. Racket est retenu parce qu'il éprouve trois variations absentes des
instances antérieures : le typage dynamique, l'absence de types sommes (les
arbres sont des structures, distinguées par prédicats et lues par accesseurs),
et le déplacement des erreurs de forme de la compilation vers l'exécution.

## Base de départ

FPTutor-Shell v2, archive `FPTutor-Shell_v2.zip`, empreinte SHA-256
`5cb93223…092fee18`. Les empreintes des 27 fichiers de la coquille (hors
`exemples/`) sont relevées avant le début dans
`mesures/empreintes_coquille_avant.txt`.

## Contenu pédagogique tenu constant

Mêmes concepts, mêmes familles, mêmes ancrages et mêmes réemplois que
l'instance OCaml (`F-arbre` et `F-option`, laboratoire 05 d'INF6120), mêmes
valeurs attendues aux tests. Les différences de coût entre les deux instances
tiennent ainsi au langage et non au contenu. Seules changent les conventions
propres à Racket : noms à traits d'union, structures au lieu de constructeurs,
`#f` au lieu de `None`.

## Étapes

E1. Engendrement du répertoire par `creer_tuteur.py`.
E2. Écriture de l'analyse (normalisateur et `analyse`), contrôlée à l'œil sur
    trois ou quatre solutions de référence avant tout branchement.
E3. `command`, `test_template`, `categorise`.
E4. Jeu de cas du banc d'essai, puis banc.
E5. Ancrages, réemplois et amorces (`activities_rkt.py`).
E6. Solutions de référence exécutées par l'interprète Racket réel.
E7. Validation des familles et induction des obligations.
E8. Essai à blanc d'une session complète par le noyau.
E9. Service HTTP : démarrage, pages, une soumission de bout en bout.

## Mesures

M1. Lignes écrites par élément du fournisseur et par fichier de l'instance,
    comptées sans lignes vides ni commentaires, en distinguant le code de
    l'analyse, le code d'intégration et le contenu d'auteur (énoncés, amorces,
    tests).

M2. Temps par étape, borné par horodatage de début et de fin
    (`mesures/journal_temps.tsv`). L'instanciation est conduite par un agent
    automatique (Claude) sous la direction de l'auteur ; les durées mesurent la
    répartition de l'effort entre étapes et ne se comparent pas en valeur
    absolue aux heures d'un auteur humain.

M3. Modifications forcées de la coquille. Une modification n'est apportée
    qu'après observation d'un échec sur la coquille non modifiée ; l'échec est
    consigné avant la correction. Chaque modification est classée : fuite du
    langage, défaut de l'atelier, défaut de mesure, point d'extension. Les
    empreintes finales sont comparées aux empreintes de départ.

M4. Réemploi de l'instance OCaml : fichiers repris et adaptés, distingués des
    fichiers écrits de novo.

## Critères de réussite

C1. Banc d'essai : réunion et séparation vérifiées, projection des messages
    correcte.
C2. Toutes les solutions de référence passent leurs tests sous Racket réel.
C3. Familles conformes au nombre de points de variation annoncé par le
    référentiel.
C4. Essai à blanc : la séquence prévue par la politique est parcourue sans
    écart (corpus insuffisant, mise à l'écart d'une solution hors forme,
    alignement instable, ouverture de l'atelier, réemplois, passage au palier
    suivant).
C5. Serveur : démarrage, titre RacketTutor dans les deux interfaces, une
    soumission évaluée par HTTP.
C6. Couche de politique et anti-unificateur inchangés (empreintes de
    `remontee.py` et des fonctions `decider`, `etat_alignement` de `noyau.py`).

## Règle d'arrêt

Si un critère ne peut être atteint sans modifier la couche de politique ou
l'anti-unificateur, l'instanciation s'arrête et l'échec devient le résultat.
