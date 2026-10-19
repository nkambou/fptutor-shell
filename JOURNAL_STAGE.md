# Journal des modifications du stage

Une ligne par changement, avec l'échec observé ou la raison qui l'a motivé
(voir « Rendre compte » dans `GUIDE_STAGIAIRE.md`).

| Date | Fichier | Changement | Raison |
|---|---|---|---|
| 2026-10-17 | exemples/ocamltutor/activities_ml.py | `bintree_sum` remplacé par `bintree_count_nodes` pour un premier essai | absent du labo 05 (`docs/CONCORDANCE_LABO.md`) |
| 2026-10-17 | exemples/ocamltutor/compiler_references.py | `bintree_count_nodes` : `x + …` → `1 + …` | la fonction additionnait les valeurs au lieu de compter les nœuds |
| 2026-10-17 | exemples/ocamltutor/activities_ml.py | `example_tree` du labo ajouté à `ARBRES`, un test par exercice sur cet arbre | aligner les valeurs attendues sur celles de l'énoncé du labo |
| 2026-10-17 | exemples/ocamltutor/activities_ml.py | `bintree_collect_values` : énoncé « dans un ordre quelconque », tests triés par `List.sort compare` | le labo accepte tout ordre ; une solution en préfixe (correcte selon le labo) échouait au tuteur |
| 2026-10-18 | exemples/ocamltutor/essai_a_blanc.py, language_ml.py, referentiel.json, valider_familles_ml.py | dernières mentions de `bintree_sum` remplacées par `bintree_count_nodes` ; dans l'essai à blanc, la variante « bibliothèque » devient `List.fold_left (fun n _ -> n + 2) 1 (bintree_collect_values a)` | l'essai à blanc (étape 4 de la batterie) soumettait un exercice qui n'existe plus. `valider_familles_ml.py` : F-arbre reste conforme (2 blocs, 2 attendus), et l'alignement vaut déjà 2 sur les 2 puis les 3 premiers exercices |
| 2026-10-17 | exemples/ocamltutor/activities_ml.py | ajout de l'arbre example_tree | tel que requis |
| 2026-10-18 | exemples/ocamltutor/activities_ml.py | ordre servi : leaves - internal_nodes - **height** - count_nodes - collect_values (height avancé de la 4e à la 3e place) | avec l'ordre précédent, l'atelier s'ouvrait sur trois exercices qui n'emploient que l'addition et sont donc relativement similaires. Seul ordre testé où l'atelier s'ouvre au 3e exercice avec une combinaison qui varie (`+` puis `max`) ; voir "Mesures sur l'ordre" plus bas pour plus de détails(à valider) |
| 2026-10-18 | exemples/ocamltutor/essai_a_blanc.py | `SCENARIO` aligné sur le nouvel ordre : leaves, internal_nodes (bibliothèque puis référence), height, count_nodes. Variante bibliothèque ajoutée pour internal_nodes : `List.fold_left (fun n _ -> n + 1) 0 (bintree_collect_values a)` | la variante hors forme doit porter sur un exercice servi avant l'ouverture de l'atelier ; height, désormais 3e, n'a pas de solution non récursive simple |

## Défauts répérés (non corrigés : coquille)

| Date | Fichier | Constat | Effet pour un étudiant | Suite |
|---|---|---|---|---|
| 2026-10-18 | noyau.py, `RAISONS` et `commentaire_hors_forme` (l. 289-389) | les messages pour une solution juste mais non comparable parlent de listes ("distinguez le cas de la liste vide et le cas où elle a au moins un élément") et sont notamment affichés dans l'interface. Observé notamment dans l'interface sur `count_nodes`, avec la solution `List.fold_left` | sur un exercice d'arbre, la consigne de réécriture désigne des cas qui n'existent pas ; il faudrait « le cas `Leaf` et le cas `Node` » | le fournisseur de langage ne permet pas de remplacer ces textes car la correction demande de modifier la coquille |
| 2026-10-18 | noyau.py, `AIDES_ERREUR` et `LECTURES` (l. 185-265) | textes par défaut hérités de HaskellTutor (GHCi, équations, motif `[]`) | ce sont eux qui s'affichent car `language_ml.py` ne déclare pas les siens | pour la tâĉhe 2 |
| 2026-10-18 | serveur.py, route `/api/aide` (l. 579-602) | le compteur d'étayage est tenu par exercice, toutes erreurs confondues. Observé sur `count_leaves` : 3 niveaux pris sur un résultat faux, puis plus aucune aide sur un cas manquant et les indices générés lors du premier essai sont encore affichés, ce qui pourrait induire l'étudiant en erreur | un étudiant qui épuise l'aide sur une première erreur n'a plus rien pour une seconde erreur, différente, sur le même exercice | peut-être voulu (rois niveaux, jamais davantage , noyau.py ligne 180) |
| 2026-10-18 | serveur.py, route `/api/aide` (l. 592-597) | une fois l'étayage épuisé, le « rappel » recalcule les 3 niveaux avec la *dernière* erreur et les affiche, sans appel à `journaliser` | l'étudiant lit à nouveau les indices précédents, et ce résultat n'est pas loggé dans journal.jsonl ce qui en soit est normal car une nouvelle aide n'a pas été générée | impact assez élevé |
| 2026-10-18 | noyau.py, `AIDES_ERREUR["missing-base-case"]`, niveau 3 | « Sa valeur est celle qui ne change rien à l'opération que vous employez » semble désigner l'élément neutre (0 pour `+`) | pour `count_leaves` et `count_nodes`, la bonne valeur de `Leaf` est 1 mais l'indice mène à `Leaf -> 0`, donc au résultat faux | - |
| 2026-10-18 | noyau.py, `questions_sur`, question 2 "Dans votre cas récursif, quelle expression désigne le résultat déjà calculé sur le reste ?"  | seul le dernier appel récursif trouvé est retenu comme bonne réponse (`appels[-1]`). Observé sur `count_internal_nodes` : réponse attendue `bintree_count_internal_nodes d`, alors que `… g` est aussi un résultat déjà calculé | la question suppose un seul appel récursif, comme sur une liste. Sur un arbre, la bonne réponse proposée semble incomplète | - |
| 2026-10-18 | noyau.py, `signaux_de_doute` (l. 353) | une solution collée(ou générée en moins de 1 minute sans erreur préalable ou une mise en forme inhabituelle (353-362 dans noyau,py)) déclenche la vérification à chaque soumission (moins de 25 s, aucune tentative ni aide) | sans effet sur les étudiants qui écrivent leur code normalement | plus d'impact sur les essais|
| 2026-10-18 | affichage du message du compilateur | le chemin du fichier temporaire (`/tmp/tmp…/Soumission.ml`) s'affiche dans le message d'erreur | du bruit pour l'étudiant | faible priorité |
| 2026-10-18 | serveur.py, route `/api/generalisation` (l. 491-500) | la généralisation écrite dans l'atelier n'est ni compilée ni vérifiée; tout texte non vide est accepté et fait passer le concept à l'état « generalised » | un étudiant qui tape n'importe quoi passe aux réemplois comme s'il avait généralisé . l'état « generalised » ne garantit pas qu'une définition correcte a été écrite | peut-être voulu (la preuve viendrait du réemploi), mais à confirmer, car les données de l'étude s'appuient sur cet état |
| 2026-10-18 | exemples/ocamltutor/language_ml.py (instance) et noyau.py, `schema_employe` (l. 644-657) | la règle stricte de réemploi OCaml (pas d'appel récursif à la fonction demandée **et** une fonction passée à une abstraction) n'existe que dans l'extension, `suivi_serveur.reemploi` (l. 230). `language_ml.py` ne déclare pas `reemploi`, alors que `language_rkt.py` le fait (« la règle de l'instance OCaml, portée en Racket »). Sans elle, `schema_employe` applique la règle commune, il suffit alors qu'il n'y ait pas d'appel récursif | par la route `/api/soumettre` du noyau, une enveloppe `let bintree_count_even a = aux a` autour d'une récursion écrite à la main serait comptée comme réemploi. selon le chemin suivi par les soumissions de réemploi (noyau ou extension), la mesure principale n'est pas la même | ça a un impact assez considérable. Vérifier avec `banc_suivi.py` et une soumission « enveloppe » dans l'interface quel chemin compte réellement. Correction possible sans toucher la coquille serait par eg de  déclarer `reemploi` dans `language_ml.py` en réutilisant la règle de l'extension, comme Racket ; à décider |

## Notes pour les décisions à venir

| Date | Décision | Constat | Ce que ça suggère |
|---|---|---|---|
| 2026-10-18 | ordre des exercices (tâche 1) | session dans l'interface : l'atelier s'ouvre sur leaves, internal_nodes, count_nodes. internal_nodes et count_nodes ont le même cas récursif (`(1 + REC) + REC`) ; seule l'addition apparaît dans les trois | l'étudiant risque une généralisation trop étroite selon moi (« ajouter 1 ou non » au lieu d'une fonction de combinaison). Placer `height` (avec `max`) parmi les trois premiers rendrait visible la variation de l'opération |
| 2026-10-18 | `off_form` (tâche 4) | avec `explain_and_continue` (défaut), la solution `List.fold_left` sur `count_nodes` est reconnue juste, écartée du corpus, et le tuteur passe à la suite | comportement conforme. reste à essayer `explain_and_rewrite` et `confront` sur une session complète |


## Détails sur l'ordre (2026-10-18)

Calcul fait avec l'analyse et l'anti-unification de la coquille (`language_ml.analyse`
et `valider_familles_ml.aligner`), sur les solutions de référence, sans compilateur.
L'atelier ne s'ouvre que si l'alignement des solutions vaut exactement le nombre de
points de variation attendu par le référentiel, soit 2 pour F-arbre (`decider`,
noyau.py l. 610) ; à 3, le tuteur répond « alignement à 3 points, le référentiel en
attend 2 ».

| Trois premiers exercices | Points de variation | Atelier au 3e | Ce qui varie à l'écran |
|---|---|---|---|
| leaves > internal > nodes (ancien ordre) | 2 | oui | seulement l'addition |
| **leaves > internal > height (retenu)** | **2** | **oui** | l'addition **et** `max` |
| leaves > height > internal | 3 | **non** | bloqué |
| internal > height > leaves | 3 | **non** | bloqué |
| leaves > internal > collect | 2 | oui | un entier puis une liste, plus long à écrire |
| leaves > internal > right | 2 | oui | seulement l'addition |

**`bintree_count_left` et `bintree_count_right`** (écart de `docs/CONCORDANCE_LABO.md`) :
contrairement à ce que la concordance anticipait, ils sont alignables. L'analyse rend
la forme `constructors`, base `0`, pas `(((CASE 0 1) + REC) + REC)` : le `match`
imbriqué sur le sous-arbre devient un bloc `CASE` que l'anti-unification absorbe.
Mais placés en 3e, ils n'apportent pas plus de contraste que `count_nodes` (seule
l'addition varie), et leur `match` imbriqué est plus difficile à écrire en vingt
minutes. Ils ne valent pas mieux que `height` pour autant. Solutions de
référence utilisées pour le calcul (non ajoutées au dépôt) :

    let rec bintree_count_right a = match a with
      | Leaf -> 0
      | Node (_, g, d) -> (match d with Leaf -> 0 | Node _ -> 1)
                          + bintree_count_right g + bintree_count_right d

    (count_left : même chose avec `match g`)

Sur `example_tree`, elles donnent 4 et 3, les valeurs de l'énoncé : `count_right`
compte les nœuds dont le sous-arbre droit est un nœud interne.

