# Concordance avec le laboratoire 05 d'INF6120

Énoncés du cours, à lire en ligne et non recopiés ici :

- Laboratoire 05, arbres binaires : https://inf6120.uqam.ca/labos/labo05/
- Laboratoire 06, théorèmes et révisions : https://inf6120.uqam.ca/labos/labo06/

Version de l'hiver 2026, reconduite à l'automne. Le type du cours est
`type bintree = Leaf | Node of int * bintree * bintree`, celui de l'instance
aussi : la concordance des types et des noms est acquise.

## Ancrages servis et sections du laboratoire

| Ancrage du tuteur | Section du laboratoire 05 | État |
|---|---|---|
| `bintree_count_leaves` | Compter, exercice 1 | concorde |
| `bintree_count_internal_nodes` | Compter, exercice 2 | concorde |
| `bintree_sum` | aucune | **absent du laboratoire** |
| `bintree_height` | Propriétés, exercice 1 | concorde, autre section |
| `bintree_collect_values` | Collectionner, exercice 1 | concorde, autre section |

Les réemplois servis après la généralisation (`bintree_count_even`,
`bintree_min`, `bintree_all_positive`, `ubtree_count_bin`) ne figurent pas dans
le laboratoire. Sa dernière section demande en revanche de récrire
`bintree_count_internal_nodes` et `bintree_collect_internal_nodes` avec
`fold_tree`, ce qui est exactement la mesure de réemploi.

## Écarts à traiter

**`bintree_sum` n'est pas au laboratoire.** Trois candidats y sont, tous dans la
section « Compter », tous de la même famille : `bintree_count_nodes`,
`bintree_count_right`, `bintree_count_left`. Le premier se plie sans réserve.
Les deux autres examinent la forme des sous-arbres et ne donnent probablement
pas un terme alignable : à passer au banc d'essai avant de décider, le résultat
vaut d'être connu dans les deux cas.

**L'ordre de service ne suit pas celui du laboratoire.** Le tuteur enchaîne
cinq ancrages pris à trois sections différentes. Pour vingt minutes, l'ordre
décide de ce que la plupart des étudiants verront : les deux premiers doivent se
résoudre vite et différer assez pour que la comparaison ait un objet.

**Les quatre réemplois sont à remplacer** par les deux de la dernière section du
laboratoire, qui mesurent la même chose sur le matériel que l'étudiant
connaîtra.

**Les valeurs attendues** du laboratoire portent sur son `example_tree`, dont
l'énoncé donne les résultats : 9 feuilles, 8 nœuds internes, 17 nœuds, hauteur
4. Reprendre cet arbre dans les amorces évite à l'étudiant de travailler sur
deux jeux de données.

## Le laboratoire 06 et la deuxième séance

Le laboratoire 06 porte sur les preuves par induction et la révision d'intra. Il
ne parle pas d'arbres, et il revient sur `fold_left` et `fold_right` sur les
listes.

La deuxième séance s'y ajoute comme un complément d'énoncé et une occasion de
révision, avec l'accord de l'enseignant : quinze minutes en début de séance,
trois exercices puis un court questionnaire, et les étudiants reviennent ensuite
au laboratoire prévu. Le détail est dans `docs/SEANCE2.md`.

L'exposition au schéma est contrôlée par trois dispositions, arrêtées avec
l'enseignant. Le corrigé de sa dernière section n'est pas publié avant la
fermeture de la phase 1, son énoncé restant en ligne. Le tuteur sert l'exercice
de transfert dès l'ouverture de l'atelier, donc avant toute présentation en
classe pour qui généralise pendant le créneau. Et l'heure de cette présentation
est relevée, ce qui permet d'étiqueter chaque soumission de réemploi en amont ou
en aval de l'exposition.

Les exercices qui nomment `fold_tree` ne rejoignent le pool qu'à la bascule, la
veille du laboratoire 06 ; ils mesurent la capacité à employer le schéma et la
persistance, non son emploi spontané.
