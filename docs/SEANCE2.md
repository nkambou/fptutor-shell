# Deuxième séance : quinze minutes au laboratoire 06

Complément à l'énoncé du laboratoire 06, présenté aux étudiants comme une
révision sur les arbres avant un laboratoire consacré aux preuves et à l'intra.
Trois exercices, un court questionnaire, puis retour au laboratoire prévu.

## Minutage

| Minute | Ce qui se passe |
|---|---|
| 0–1 | Reprise avec le même pseudonyme, le dossier est conservé |
| 1–11 | Les trois exercices, dans l'ordre servi |
| 11–14 | Questionnaire |
| 14–15 | Fin, retour au laboratoire 06 |

Dix minutes pour trois exercices est serré. L'ordre est donc fait pour que le
troisième soit atteint : les deux premiers sont des réécritures dont la forme est
donnée, le troisième est le seul qui demande une décision. Un étudiant qui
n'arrive qu'au deuxième a tout de même produit la mesure principale, puisque
celle-ci se lit sur chacun des trois.

## Les trois exercices

**1. `bintree_count_internal_nodes` avec `fold_tree`.** L'exercice de la dernière
section du laboratoire 05. La consigne nomme `fold_tree`, donc il ne mesure pas
l'emploi spontané : il vérifie que l'étudiant sait s'en servir, et il sert de
mise en train.

**2. `bintree_collect_internal_nodes` avec `fold_tree`.** Le second exercice de
la même section. Même consigne explicite, mais le résultat est une liste et non
un entier : c'est le passage d'un type de résultat à un autre qui est éprouvé.

**3. Un exercice de transfert, sans consigne de méthode.** Par exemple
`bintree_count_even`, le nombre de nœuds internes portant un entier pair.
L'énoncé dit que toute solution correcte est acceptée. C'est le seul des trois où
l'emploi du schéma est une décision de l'étudiant, donc le seul qui mesure le
réemploi spontané.

Le troisième exercice ne doit pas figurer dans le laboratoire, sans quoi
l'étudiant l'aura peut-être déjà écrit. `bintree_count_even` satisfait cette
condition.

## Questionnaire

Trois minutes, six questions, dans la page du tuteur après le troisième
exercice. Aucune donnée nominative : le pseudonyme sert de clé, rien d'autre
n'est demandé.

1. Avez-vous écrit `fold_tree` vous-même lors de la première séance, ou l'avez-vous
   reçu en classe ? (trois choix : moi-même, en classe, je ne sais plus)
2. Au troisième exercice, avez-vous pensé à employer `fold_tree` avant de
   commencer à écrire ? (oui, non, j'y ai pensé en cours d'écriture)
3. Si vous ne l'avez pas employé, pourquoi ? (une ligne)
4. L'écran qui montrait vos solutions côte à côte vous a-t-il aidé à voir ce
   qu'elles avaient en commun ? (échelle à quatre degrés)
5. Les indices reçus vous ont-ils débloqué ? (échelle à quatre degrés, plus
   « je n'en ai pas demandé »)
6. Une chose à changer dans l'outil. (une ligne)

La première question est celle qui compte le plus pour l'analyse, puisque c'est
elle qui dira, réponse par réponse, laquelle des deux mesures de réemploi on
tient.

## Statut des données

Le certificat d'éthique n'est pas délivré. Les réponses au questionnaire et les
relevés servent à corriger l'outil et ne seront pas exploités comme données de
recherche avant la délivrance. Les étudiants doivent l'entendre, en une phrase,
avant de répondre.

## Mise en œuvre

Les trois exercices vont dans `REEMPLOIS` de `activities_ml.py`, dans cet ordre.
Le questionnaire passe par le point d'extension de l'instance, celui qui porte
déjà la séance de suivi, sans modification de la coquille.
