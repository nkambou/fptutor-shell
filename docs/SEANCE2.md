# Deuxième séance : quinze minutes au laboratoire 06

Complément à l'énoncé du laboratoire 06, présenté aux étudiants comme une
révision sur les arbres avant un laboratoire consacré aux preuves et à l'intra.
Trois exercices, un court questionnaire, puis retour au laboratoire prévu.

## Minutage du créneau

Le créneau donne l'amorce ; l'accès reste ouvert sept jours après, de sorte
qu'un apprenant qui n'a pas fini les trois exercices les reprend de chez lui et
répond alors au questionnaire.

| Minute | Ce qui se passe |
|---|---|
| 0–1 | Reprise avec le même pseudonyme, le dossier est conservé |
| 1–11 | Les trois exercices, dans l'ordre servi |
| 11–15 | Questionnaire |

Dix minutes pour trois exercices est serré. L'ordre est donc fait pour que le
troisième soit atteint : les deux premiers sont des réécritures dont la forme est
donnée, le troisième est le seul qui demande une décision. Un étudiant qui
n'arrive qu'au deuxième a tout de même produit la mesure principale, puisque
celle-ci se lit sur chacun des trois.

## Les deux phases du réemploi

Le pool `REEMPLOIS` est servi dans l'ordre du fichier, dès que l'atelier
d'abstraction s'est ouvert. Son contenu décide donc de ce qui est mesuré avant
que l'enseignant ait présenté `fold_tree` en classe.

### Phase 1, dès l'ouverture de l'atelier

Un seul exercice dans le pool : **le transfert sans consigne de méthode**, par
exemple `bintree_count_even`, le nombre de nœuds internes portant un entier
pair, avec la mention que toute solution correcte est acceptée. Il est servi
dans la minute qui suit la généralisation, donc dans la même trajectoire, et
c'est lui qui porte la mesure principale.

Les exercices qui nomment `fold_tree` restent hors du fichier à ce stade : les
servir reviendrait à donner le schéma avant que l'apprenant ait eu à y penser
seul.

Aucune solution de `fold_tree` n'est rendue publique avant la fin du second
créneau, et l'enseignant ne traite pas sa dernière section en classe avant ce
moment. Selon l'option retenue, la section reste dans l'énoncé du laboratoire 05
ou passe à celui du laboratoire 06 : voir `OPTIONS_EXPOSITION.md`.

### Bascule, la veille du laboratoire 06

Trois exercices s'ajoutent au pool :

1. `bintree_count_internal_nodes` avec `fold_tree`, réécriture de la dernière
   section du laboratoire, qui sert de mise en train au second créneau.
2. `bintree_collect_internal_nodes` avec `fold_tree`, même consigne explicite,
   mais le résultat passe d'un entier à une liste.
3. Un second exercice de transfert, sans consigne de méthode, qui porte la
   mesure de réemploi différé.

Procédure : ajouter les trois quintuplets à `REEMPLOIS` dans
`activities_ml.py`, puis relancer en conservant l'état.

    ./relancer.sh --garder

Le tuteur sert un exercice que l'apprenant n'a pas encore reçu, repéré par son
nom : les nouveaux arrivent donc en tête des suivants, sans toucher aux dossiers
déjà constitués. À éprouver sur une copie d'essai avant la bascule réelle.

### Ce qu'il ne faut pas changer

`reemploi_requis` vaut deux. Avec un seul exercice de transfert disponible en
phase 1, le tuteur annoncera un réemploi sur deux et s'arrêtera là : c'est le
comportement voulu.

Aucun verrou de date n'est ajouté à la coquille. La fermeture de la phase 1 se
fait par la bascule et par l'annonce aux apprenants.

Le corrigé de la dernière section n'est pas déposé dans le dépôt avant la
fermeture.

## Questionnaire

Trois à quatre minutes, sept questions, dans la page du tuteur après le
troisième exercice. Aucune donnée nominative : le pseudonyme sert de clé, rien
d'autre n'est demandé.

1. Question d'exposition, dont la formulation dépend de l'option retenue pour
   l'énoncé du laboratoire 05. Les deux libellés sont dans
   `OPTIONS_EXPOSITION.md`, et l'un d'eux est repris tel quel ici une fois
   l'option tranchée.
2. Au troisième exercice, avez-vous pensé à employer `fold_tree` avant de
   commencer à écrire ? (oui, non, j'y ai pensé en cours d'écriture)
3. Si vous ne l'avez pas employé, pourquoi ? (une ligne)
4. Quelles ressources avez-vous consultées pour ces exercices ? Plusieurs
   réponses possibles, et aucune n'est un problème : la documentation d'OCaml,
   les notes ou le corrigé du laboratoire, un ou une condisciple, un assistant
   conversationnel, une recherche sur le web, aucune.
5. L'écran qui montrait vos solutions côte à côte vous a-t-il aidé à voir ce
   qu'elles avaient en commun ? (échelle à quatre degrés)
6. Les indices reçus vous ont-ils débloqué ? (échelle à quatre degrés, plus
   « je n'en ai pas demandé »)
7. Une chose à changer dans l'outil. (une ligne)

La première question renseigne sur ce que l'apprenant connaissait du schéma
avant de généraliser, et sert de covariable sous l'option A. La quatrième
renseigne sur les conditions de travail hors séance, que la fenêtre ouverte rend
inégales d'un apprenant à l'autre.

Trois règles de rédaction pour la quatrième, à tenir si elle est reformulée.
Elle est factuelle et ne qualifie jamais la conduite : ni « aide extérieure »,
ni « seul », et surtout aucun mot du registre de la triche. Elle propose la
réponse plutôt qu'elle ne l'extorque, en énumérant les ressources, y compris
celles que personne n'hésiterait à déclarer, ce qui normalise les autres. Et
elle dit en toutes lettres qu'aucune réponse n'est un problème, la participation
étant sans effet sur la note.

## Statut des données

Le certificat d'éthique de l'UQAM est délivré pour cette étude. Les réponses au
questionnaire et les traces du tuteur sont donc recueillies comme données de
recherche, sous pseudonyme, et pourront être analysées et publiées.

Avant le questionnaire, les étudiants entendent ce que le certificat prévoit :
la participation est volontaire et sans effet sur la note, les données sont
recueillies sous pseudonyme sans nom ni code permanent, et un étudiant peut
demander le retrait des siennes. Le formulaire de consentement approuvé est la
référence : ce document ne s'y substitue pas.

## Mise en œuvre

Les exercices vont dans `REEMPLOIS` de `activities_ml.py`, celui de phase 1
avant la première séance, les trois autres à la bascule. Le questionnaire passe
par le point d'extension de l'instance, celui qui porte déjà la séance de suivi,
sans modification de la coquille.

L'export doit porter, pour chaque soumission de réemploi, une étiquette de
phase : avant exposition, après exposition, ou différée. Elle se calcule en
comparant l'horodatage de la soumission à l'heure relevée de la présentation en
classe. Voir le protocole de recherche pour l'usage qui en est fait.
