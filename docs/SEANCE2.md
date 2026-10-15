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

Servi par l'extension de l'instance, dans `suivi.html`, dès les trois exercices
terminés, et enregistré par la route `/api/questionnaire` dans l'état du suivi.
Huit questions, trois à quatre minutes. Le pseudonyme sert de clé, rien d'autre
n'est demandé.

| # | Question | Clé enregistrée |
|---|---|---|
| 1 | Exposition au schéma avant ces exercices ; le libellé dépend de l'option retenue | `exposition` |
| 2 | Ces exercices avaient-ils quelque chose en commun avec ceux de la séance précédente, et quoi | `reconnaissance` |
| 3 | Avez-vous réutilisé quelque chose écrit ou appris lors de cette séance, et quoi | `reutilisation`, `reutilisation_detail` |
| 4 | Pour les exercices où vous avez écrit la récursion vous-même, pourquoi | `raison_recursion_main`, `items_recursion_main` |
| 5 | Quelles ressources avez-vous consultées, plusieurs réponses possibles | `ressources` |
| 6 | Le moment où le tuteur a demandé d'écrire ce que vos définitions avaient en commun est arrivé trop tôt, au bon moment, trop tard | `moment_generalisation` |
| 7 | Les indices reçus vous ont-ils débloqué | `aide_utile` |
| 8 | Que retenez-vous de cette activité, en une phrase, facultatif | `retenu` |

La quatrième ne s'affiche que si l'apprenant a effectivement écrit une récursion
à la main, ce que la page sait de ses soumissions, et la liste de ces exercices
part avec la réponse.

La première renseigne sur ce que l'apprenant connaissait du schéma avant de
généraliser. Son libellé et ses choix viennent du serveur, selon l'option
d'exposition retenue, donnée au lancement :

    SUIVI_OPTION_EXPOSITION=B

Sans cette variable, l'option A s'applique. Les deux libellés sont dans
`OPTIONS_EXPOSITION.md`.

La cinquième renseigne sur les conditions de travail hors séance, que la fenêtre
ouverte rend inégales d'un apprenant à l'autre. Elle est factuelle et ne
qualifie jamais la conduite : ni « aide extérieure », ni « seul », et aucun mot
du registre de la triche. Elle énumère les ressources, y compris celles que
personne n'hésiterait à déclarer, et dit en toutes lettres qu'aucune réponse
n'est un problème.

La sixième et la septième portent sur la réception du dispositif, la sixième
renseignant directement sur la condition de déclenchement de l'atelier.

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
avant la première séance, les autres à la bascule. L'extension de l'instance
choisit ceux qu'elle sert, et leur ordre, dans sa propre liste `ORDRE` : elle
sert aujourd'hui `bintree_count_even`, puis `bintree_all_positive`, puis
`ubtree_count_bin`, gradation voulue où la forme reste celle du laboratoire,
puis le type du résultat change, puis le type de l'arbre change. Aucun des trois
ne nomme `fold_tree`.

Le questionnaire est servi et enregistré par l'extension, sans modification de
la coquille. Reste à l'exporter : `table_questionnaire` dans
`export_donnees.py`, qui lit l'état du suivi et sort une ligne par participant,
la question des ressources éclatée en colonnes binaires.

L'export doit aussi porter, pour chaque soumission de réemploi, une étiquette de
phase : immédiate, différée, ou post-exposition. Voir le protocole de recherche
pour l'usage qui en est fait.
