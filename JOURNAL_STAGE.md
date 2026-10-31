# Journal des modifications du stage

Une ligne par changement, avec l'échec observé ou la raison qui l'a motivé
(voir « Rendre compte » dans `GUIDE_STAGIAIRE.md`).

### Ce qui a été changé dans l'instance OCaml


1. **Les exercices suivent le labo 05.**
   - `bintree_sum`, qui n'existe pas dans le labo, a été remplacé par
     `bintree_count_nodes` (compter tous les nœuds, feuilles comprises).
   - L'arbre du labo, `example_tree`, a été ajouté au code de départ de chaque
     exercice, avec un test par exercice : l'étudiant retrouve les résultats de son
     énoncé (9 feuilles, 8 nœuds internes, 17 nœuds, hauteur 4).
   - `bintree_collect_values` accepte maintenant les valeurs dans n'importe quel
     ordre, comme le labo. Avant, seul un ordre précis était accepté, et une
     solution juste selon le labo pouvait échouer dans le tuteur.
   - Les exercices sont servis dans l'ordre du labo (décision 1, plus bas).

2. **Le réemploi est compté correctement.**
   - Le « réemploi », c'est quand l'étudiant réutilise sa fonction générale
     (`fold_tree`) pour résoudre un nouvel exercice, au lieu de tout réécrire à la
     main. C'est la mesure principale de l'étude.
   - J'ai constaté que la page principale utilisait une règle trop simple. Une
     solution qui cachait une récursion écrite à la main dans une fonction
     auxiliaire (`let bintree_min a = aux a`) était comptée comme un réemploi. Dans
     l'interface, un étudiant pouvait ainsi être déclaré « concept acquis » sans
     avoir vraiment réutilisé sa fonction.
   - Pour corriger, la règle stricte, qui existait déjà dans l'extension de suivi, est
     maintenant utilisée aussi par la page principale. Il n'y a plus qu'une seule
     règle pour les deux pages.

3. **Les messages d'erreur sont mieux reconnus.**
   - Le tuteur lit le message d'OCaml et le range dans une catégorie (cas oublié,
     erreur de type, nom inconnu, etc.) pour choisir les bons textes d'aide.
   - Une erreur probablement fréquente, oublier un champ de `Node` (`Node (_, g)`),
     n'entrait dans aucune catégorie et l'étudiant ne recevait aucun indice utile.
     Elle est maintenant rangée avec les erreurs de type.
   - Quand un code contient à la fois un avertissement (cas oublié, qui n'empêche
     pas le code de tourner) et une erreur (qui bloque tout), le tuteur choisissait
     l'avertissement. Il choisit maintenant l'erreur, qui est ce qui bloque réellement
     l'étudiant.

4. **Les textes d'aide sont écrits pour OCaml.**
   - Avant, les étudiants lisaient des textes écrits pour Haskell (GHCi, équations,
     listes). Pour les erreurs entre entier et nombre à virgule, ils ne recevaient
     rien du tout.
   - Chaque catégorie a maintenant une phrase affichée tout de suite (la lecture),
     qui dit ce qui se passe, et trois niveaux d'aide à la demande, dont le degré de guidance augmente 
     graduellement et s'adapte aux erreurs de l'étudiant.
   - Ces textes s'appuient sur les vrais messages d'OCaml, relevés sur 13 erreurs
     typiques. Ils ne contiennent plus l'indice de l'« élément neutre », qui menait
     à une mauvaise réponse pour `count_leaves`.

5. **Les outils de vérification ont été mis à jour** pour suivre ces changements :
   les solutions de référence, l'essai à blanc, la validation des familles et le
   jeu de cas des messages.

### Les modifications dans la coquille (2026-10-20 au 2026-10-25)

Le superviseur a autorisé à prendre les décisions pertinentes, à corriger les
incohérences de la coquille (par exemple les textes écrits pour des listes), et à
rendre l'interface intuitive pour les étudiants. Les parties gelées (`remontee.py`,
`decider` et `etat_alignement` dans `noyau.py`) n'ont pas été modifiées.

6. **Les textes qui parlaient de listes sont corrigés.**
   - Le message pour une solution juste mais écrite autrement disait « distinguez le
     cas de la liste vide et le cas où elle a au moins un élément ». Il dit
     maintenant, pour OCaml, « le cas de la feuille (Leaf) et le cas du nœud (Node) ».
   - Les questions « expliquez votre code » parlaient d'« entrée vide », de « reste
     de l'entrée » et proposaient `True` (du Haskell). Elles demandent maintenant
     « Que rend votre fonction sur une feuille (Leaf) ? », avec des choix en OCaml.
   - La question sur l'appel récursif n'acceptait qu'un des deux appels (`… d`), alors
     qu'un arbre en a deux. La bonne réponse réunit maintenant les deux appels.
   - L'explication qui renvoyait à l'« élément neutre » (et contredisait une réponse
     juste comme `Leaf -> 1`) est remplacée.
   - La bonne réponse était toujours le premier choix ; l'ordre est maintenant mélangé.
   - Le noyau a désormais des textes neutres (« cas de base », « cas récursif »),
     valables pour toutes les instances, et chaque langage peut les préciser. OCaml
     les précise pour les arbres dans `language_ml.py`. Les instances Racket, Haskell
     et Python continuent de fonctionner.

7. **Le rappel des indices ne donne plus d'aide en cachette.** Une fois les trois
   indices pris, le rappel réaffiche ceux que l'étudiant a vraiment reçus, au lieu de
   fabriquer trois nouveaux indices pour sa dernière erreur, sans les enregistrer.

8. **Deux défauts d'origine, trouvés en testant, sont réparés.**
   - `bintree_collect_values` ne pouvait jamais être réussi; son premier test attend
     une ligne vide (la liste des valeurs d'une feuille est vide), et le tuteur
     supprimait cette ligne avant de comparer. Une solution juste était refusée.
   - Le bouton « Pas encore » de l'atelier n'avait aucun effet : il appelait une
     fonction absente de la page. Il sert maintenant un exercice de plus, puis
     l'atelier revient.

9. **L'interface étudiante est simplifiée.**
   - Disposition : l'exercice est en haut, en pleine largeur. Les panneaux secondaires
     (progression, ce que vous apprenez, indices, solutions, groupe, activité) sont en
     dessous. Les détails techniques (décision du tuteur, solutions comparées) sont
     repliés dans « Détails techniques (pour l'enseignant) ».
   - Vocabulaire : « Régime » devient « Mode de travail », « Activité engendrée »
     devient « Exercice », « étayage » devient « indice », « Carte des concepts »
     devient « Ce que vous apprenez », « instance(s) » devient « solution(s) »,
     « verrou » devient « plus tard », « Atelier de remontée » devient « Atelier : ce
     que vos fonctions ont en commun », « réemploi » devient « réutilisation de votre
     découverte ». Les catégories d'erreur sont dites en français (« cas non traité »
     au lieu de `missing-base-case`).
   - Intuitivité et facilité d'utilisation.

10. **Ce qui a changé dans `noyau.py`.** Seules les parties hors gel ont été touchées
    (`decider` et `etat_alignement` sont inchangés).
    - **Points de réglage pour le fournisseur** : `CONSIGNE_FORME`, `VERIF_BASE`,
      `DISTRACTEURS_BASE`, `RAISONS` et `AIDES_REMONTEE` peuvent être déclarés par
      l'instance, comme `AIDES_ERREUR` et `LECTURES`. Sans déclaration, le noyau
      garde des textes neutres (« cas de base », « cas récursif ») au lieu des textes
      de listes de Haskell (« liste vide », « premier élément », `[]`, `True`).
    - **`RAISONS`** : la raison « no-pattern » parle du cas de base et du cas
      récursif au lieu de la liste vide et du premier élément.
    - **`questions_sur`** (questions de vérification) : la question sur le cas de
      base emploie `VERIF_BASE` et `DISTRACTEURS_BASE` ; son explication ne renvoie
      plus à l'« élément neutre », qui contredisait une réponse juste comme
      `Leaf -> 1`. La question sur l'appel récursif réunit tous les appels
      (« f g et f d ») au lieu du dernier seulement, ignore la ligne de définition et
      propose le distracteur « f a » (appel sur l'arbre entier). L'ordre des choix
      est mélangé.
    - **`AIDES_REMONTEE`** (indices de l'atelier) : le niveau 2 renvoie à `REC` dans
      le tableau au lieu des « trous ?n », qui ne sont pas affichés. OCaml remplace
      ces trois textes par les siens.
    - **`aide` et `AIDES_EXERCICE`** : une instance peut déclarer des indices propres
      à un exercice (par exemple `max` pour `bintree_height`), qui remplacent
      l'indice général pour cet exercice, cette catégorie et ce niveau. La route
      d'aide du serveur passe pour cela le nom de l'exercice à `aide`.
    - **`evaluer`** : (1) la sortie des tests n'est plus coupée de sa première ligne
      vide, ce qui rendait `bintree_collect_values` impossible à réussir (point 8) ;
      (2) le chemin du répertoire temporaire est retiré des messages d'OCaml ; (3) le
      délai dépassé est expliqué (« l'exécution ne s'est pas terminée en 25 secondes,
      votre fonction s'appelle peut-être sans fin »).
    - **`commentaire_hors_forme`** : la consigne de forme vient de `CONSIGNE_FORME`.
      Le message dit ce qu'il advient de la solutionelle est conservée dans les
      solutions mais ne compte pas pour la comparaison ; avec `explain_and_rewrite`,
      il annonce qu'une seconde version hors forme fait passer à l'exercice suivant.
      Coquilles « La votre » et « forme-la » corrigées.
    - **Accents** ajoutés à tous les textes affichés (indices, lectures, raisons,
      messages de réussite et de refus, docstrings), sauf dans les parties gelées et
      les exercices Haskell du noyau.


## Décisions prises selon le guide du stagiaire (2026-10-20)

**1. Ordre des exercices : celui du labo 05** (leaves, internal_nodes, count_nodes,
height, collect_values).
- Pourquoi : l'étudiant reconnaît son énoncé, et la concordance le demande.
  L'atelier s'ouvre à la 4e solution comparable : height (avec son `max`) figure
  parmi les 4 exercices montrés.
- Pour changer : déplacer le bloc `bintree_height` dans `ACTIVITES`
  (`activities_ml.py`) et l'ordre du `SCENARIO` d'`essai_a_blanc.py`.

**2. Réemplois de la phase 1 : seulement `bintree_count_even`.**
- tel que demandé dans le guide.

**3. Second transfert : `bintree_all_positive`.**
- Il ne nomme pas `fold_tree` (c'est un vrai transfert, sans consigne de
  méthode), il garde le même type d'arbre, mais le résultat change de type (un booléen
  au lieu d'un entier); il demande d'adapter le schéma, pas de le recopier.
  `bintree_min` a été écarté (la manipulation d'une `option` ajoute une difficulté
  étrangère au schéma, l'extension le notait déjà), `ubtree_count_bin` aussi (un autre
  type d'arbre, plus difficile en 10 minutes).
- Pour changer il suffit de remplacer le dernier nom de `PHASE_2`.


| Date | Fichier | Changement | Raison |
|---|---|---|---|
| 2026-10-17 | exemples/ocamltutor/activities_ml.py | `bintree_sum` remplacé par `bintree_count_nodes` | absent du labo 05 (`docs/CONCORDANCE_LABO.md`) |
| 2026-10-17 | exemples/ocamltutor/compiler_references.py | `bintree_count_nodes` : `x + …` → `1 + …` | la fonction additionnait les valeurs au lieu de compter les nœuds |
| 2026-10-17 | exemples/ocamltutor/activities_ml.py | `example_tree` du labo ajouté à `ARBRES`, un test par exercice sur cet arbre | aligner les valeurs attendues sur celles de l'énoncé du labo |
| 2026-10-17 | exemples/ocamltutor/activities_ml.py | `bintree_collect_values` : énoncé « dans un ordre quelconque », tests triés par `List.sort compare` | le labo accepte tout ordre ; une solution en préfixe (correcte selon le labo) échouait au tuteur |
| 2026-10-18 | exemples/ocamltutor/language_ml.py, referentiel.json, valider_familles_ml.py | dernières mentions de `bintree_sum` remplacées par `bintree_count_nodes` | suite du remplacement de `bintree_sum`. `valider_familles_ml.py` : F-arbre reste conforme (2 blocs, 2 attendus) |
| 2026-10-18 | exemples/ocamltutor/essai_a_blanc.py | `SCENARIO` : `bintree_sum` remplacé par `bintree_count_nodes` ; la variante « bibliothèque » (solution juste mais non comparable) porte sur `bintree_count_internal_nodes` : `List.fold_left (fun n _ -> n + 1) 0 (bintree_collect_values a)` | l'essai à blanc (étape 4 de la batterie) soumettait un exercice qui n'existe plus ; la variante hors forme doit porter sur un exercice servi avant l'ouverture de l'atelier |
| 2026-10-18 | exemples/ocamltutor/normalisation_ml.py, language_ml.py, suivi_serveur.py | règle de réemploi de l'extension déplacée dans `normalisation_ml.reemploi` ; `language_ml.py` la déclare (`reemploi`), comme `language_rkt.py` ; `suivi_serveur.reemploi` délègue à la même fonction (anciennes fonctions auxiliaires retirées). Aucune modification de la coquille | observé dans l'interface : une enveloppe `let bintree_min a = aux a` comptée comme réemploi, concept passé à « acquired ». Vérifié après correction, sans compilateur : enveloppe → non pour le noyau et l'extension ; `fold_tree` → oui pour les deux ; récursion à la main → non ; les cas de `banc_suivi.py` donnent le même verdict de pli qu'avant ; `valider_familles_ml.py` conforme. **Correction faite avant discussion avec le superviseur, à lui présenter** ; **vérifié dans l'interface le 2026-10-19** (serveur redémarré, nouvelle session) : l'enveloppe sur `bintree_count_even` n'est plus comptée comme réemploi |
| 2026-10-19 | exemples/ocamltutor/language_ml.py, `categorise` | le message « The constructor Node expects 3 argument(s), but is applied here to 2 argument(s) » est classé en `incompatible-types` (test `"expects" in m and "argument" in m`) | relevé des messages OCaml : un champ de `Node` oublié tombait en `unclassified`, donc sans indice utile ; erreur probablement fréquente (le labo place la valeur en premier). Relevé refait après correction : les 12 cas testés sont classés comme attendu, seule la boucle infinie reste `unclassified` (le tuteur coupe à 25 s, « délai dépassé ») |
| 2026-10-19 | exemples/ocamltutor/language_ml.py, `AIDES_ERREUR` et `LECTURES` | **textes d'aide écrits pour OCaml** : pour `missing-base-case`, `incompatible-types`, `int-float-mix`, `unknown-name`, `syntax`, `wrong-result` et `unclassified`, une lecture affichée tout de suite (l'effet en langage simple) et trois niveaux d'indice, une idée par indice, environ 20 mots. Niveau 1 : une piste (cas manquant : « Votre match oublie une des deux formes d'arbre : Leaf ou Node. Laquelle n'a pas de cas ? » ; résultat faux : regarder la ligne t0 du tableau des résultats). Niveau 2 : où regarder (partie soulignée du message, ligne `Hint:`, ligne du dessus ; résultat faux : le cas Node combine mal les résultats de g et de d). Niveau 3 : la charpente sans le corps (résultat faux : refaire à la main la première ligne fausse du tableau). Vocabulaire des arbres ; aucun indice d'élément neutre ; jamais `fold_tree` ni le schéma | les étudiants recevaient les textes du noyau, écrits pour Haskell (GHCi, équations, listes, `[]`), et rien pour `int-float-mix` (le noyau n'a que `int-double-mix`) ; l'indice de l'élément neutre menait à `Leaf -> 0` pour `count_leaves`. Textes écrits à partir des messages relevés sur OCaml 4.14.2 (13 erreurs typiques) ; le niveau 1 donne une piste, à la demande du superviseur. Vérifié : le noyau sert ces textes pour les 7 catégories, aucun mot interdit, aucune valeur du cas Leaf donnée |
| 2026-10-19 | exemples/ocamltutor/language_ml.py, `categorise` | quand le message contient une ligne `Error:`, la catégorie est déterminée à partir de cette erreur ; l'avertissement « not exhaustive » (Warning 8) n'est pris en compte que s'il n'y a pas d'erreur | observé dans l'interface : un code avec un cas oublié **et** une valeur flottante (`Leaf -> 1.1`) recevait les aides du cas manquant, alors que c'est l'erreur de type qui empêche le code de s'exécuter (l'avertissement n'empêche pas la compilation). Vérifié : relevé refait, les 12 cas précédents gardent leur catégorie, le nouveau cas « deux erreurs » passe en `int-float-mix` ; le message de `cas_ml.json` (« Error: This pattern-matching is not exhaustive ») reste en `missing-base-case` |
| 2026-10-20 | exemples/ocamltutor/cas_ml.json, section `messages` | 9 messages ajoutés au jeu de cas du banc d'essai, recopiés tels qu'OCaml 4.14.2 les affiche : le vrai avertissement du cas oublié (Warning 8), les deux sens de l'erreur entier/flottant, l'appel avec trop d'arguments, le champ de `Node` oublié, le `rec` oublié, le constructeur mal écrit, la parenthèse non fermée, et le cas « avertissement + erreur ». Les 4 messages d'origine sont conservés | le jeu de cas ne contenait que 4 messages, dont un qui n'est pas celui qu'affiche OCaml (« Error: » au lieu d'un « Warning 8 »). Le banc d'essai vérifie que chaque message est rangé dans la bonne catégorie : il protège maintenant les deux corrections de `categorise` (si quelqu'un les défait, le banc échoue). Vérifié : `banc_essai.py` classe correctement les 13 messages |
| 2026-10-20 | noyau.py (`RAISONS`, `commentaire_hors_forme`, `questions_sur`, `AIDES_REMONTEE`) et exemples/ocamltutor/language_ml.py | textes neutres dans le noyau (« cas de base », « cas récursif ») ; nouveaux points de réglage pour le fournisseur : `CONSIGNE_FORME`, `VERIF_BASE`, `DISTRACTEURS_BASE`, `RAISONS`, `AIDES_REMONTEE` (comme `AIDES_ERREUR` et `LECTURES`). OCaml les précise : « le cas de la feuille (Leaf) et le cas du nœud (Node) », « Que rend votre fonction sur une feuille (Leaf) ? », choix `0, 1, [], true, None`. Questions de vérification : la bonne réponse sur l'appel récursif réunit tous les appels (« f g et f d ») ; un distracteur « f a » (appel sur l'arbre entier) ; l'explication de l'élément neutre est remplacée ; l'ordre des choix est mélangé. Niveau 2 de l'aide de l'atelier : renvoie à `REC` dans le tableau au lieu des « trous ?n », qui ne sont pas affichés | défauts repérés en testant (textes de listes, `True` au lieu de `true`, un seul appel récursif accepté, explication fausse pour `Leaf -> 1`), corrigés avec l'accord du superviseur. Vérifié : le noyau se charge pour les quatre instances (OCaml prend ses textes d'arbres, les autres les textes neutres) ; scénario automatique sur serveur de test |
| 2026-10-20 | serveur.py, route `/api/aide` | le rappel (aide épuisée) réaffiche les indices déjà donnés, gardés dans le dossier (`aides_textes`), au lieu de recalculer les trois niveaux avec la dernière erreur | défaut repéré en testant : trois indices jamais demandés étaient affichés après une nouvelle erreur, sans être journalisés. Vérifié par le scénario : après 3 indices sur « résultat faux » puis une erreur « cas oublié », le rappel montre exactement les 3 indices lus |
| 2026-10-20 | etudiant.html et serveur.py (`/api/refus_atelier`, `vue_apprenant`, `/api/soumettre`) | bouton « Pas encore » réparé : la fonction `refuserAtelier` est ajoutée à la page ; le serveur note la demande (`atelier_differe`) et sert l'exercice suivant de la famille tant qu'il n'est pas réussi, puis l'atelier revient. `decider` n'est pas modifié | **défaut trouvé en refaisant la page** : le bouton appelait une fonction absente (clic sans effet), et la route existante ne faisait que journaliser, alors qu'elle annonçait « une activité de plus vous est servie ». Vérifié par le scénario |
| 2026-10-20 | exemples/ocamltutor/activities_ml.py | `EXERCICES_REEMPLOI` : réserve de tous les exercices après l'atelier (les 4 anciens, plus `bintree_count_internal_nodes_fold` et `bintree_collect_internal_nodes_fold`) ; `REEMPLOIS` construit à partir de `PHASE_1` (`count_even`) et, si `BASCULE_FAITE` vaut `True`, de `PHASE_2` (les deux `_fold` puis `all_positive`) | tâche 3 du guide, décisions 2 et 3 (voir « Décisions prises »). |
| 2026-10-20 | exemples/ocamltutor/suivi_serveur.py | l'extension prend ses exercices dans `EXERCICES_REEMPLOI` ; `ORDRE` = `PHASE_2` ; énoncés ajoutés pour les deux exercices `_fold` | l'extension lisait `REEMPLOIS`, que la phase 1 réduit, et faisait refaire `count_even`. |
| 2026-10-20 | exemples/ocamltutor/compiler_references.py, essai_a_blanc.py, banc_suivi.py | `compiler_references.py` vérifie toute la réserve (les exercices de la bascule doivent être justes avant d'être servis) et reçoit deux références en récursion explicite pour les `_fold` ; l'essai à blanc soumet `count_even` à la main puis avec le schéma (phase 1) ; `banc_suivi.py` lit la réserve, teste les 3 exercices du suivi avec 17 cas, dont l'enveloppe `aux` pour chacun | les outils lisaient `REEMPLOIS` ou des exercices qui ne sont plus servis : la batterie aurait échoué. |
| 2026-10-20 | exemples/ocamltutor/language_ml.py, activities_ml.py, noyau.py, serveur.py, textes.py | **accents ajoutés** à tous les textes affichés aux étudiants : indices et lectures, consigne de forme, énoncés des exercices, messages du tuteur (réussite, hors forme, vérification, refus) et textes par défaut du noyau. Fait par un script ciblé : seules les phrases (chaînes avec espaces) sont modifiées ; jamais les codes de départ ni les expressions de test (`premiere` y est un nom de fonction OCaml), ni les noms de fichiers d'un message d'erreur, ni les parties gelées du noyau (`decider`, `etat_alignement`), ni les exercices Haskell du noyau. Les mêmes corrections sont appliquées aux clés du catalogue de traduction (`textes.py`), pour que la version anglaise retrouve les phrases | demande de la stagiaire (le dépôt était écrit sans accents). Vérifié : syntaxe des 5 fichiers ; noyau et serveur se chargent pour les 4 instances ; la traduction anglaise couvre les mêmes phrases qu'avant (elle était déjà partielle aux mêmes endroits, vérifié contre la version de Git) ; scénario de 28 contrôles ; batterie complète, 17 exercices sur 17 |
| 2026-10-20 | serveur.py (`vue_apprenant`), etudiant.html, textes.py | (1) **après le dernier exercice de réemploi**, le tuteur reste sur « réemploi » et la page affiche un écran « Terminé pour aujourd'hui » (travail enregistré, autres exercices à la prochaine séance, garder pseudonyme et identifiant), sans consigne de méthode ; (2) quand il n'y a plus d'exercice et pas assez de solutions comparables (toutes écrites autrement), l'écran « Rien à faire pour le moment » est remplacé par « Plus de nouvel exercice », qui explique de reprendre un ou deux exercices sous la forme attendue, avec un bouton qui ouvre « Mes solutions » | (1) **défaut trouvé par la stagiaire** : après `count_even` (seul réemploi de la phase 1), le serveur passait en mode guidage, prévu pour un étudiant bloqué *avant* l'atelier, et réaffichait le tableau de comparaison ; SEANCE2.md demande que le tuteur s'arrête après un réemploi sur deux. (2) impasse repérée en analysant le cas d'un étudiant qui écrit toutes ses solutions hors forme : rien ne lui disait comment en sortir. `decider` n'est pas modifié. Vérifié : phase 1 rejouée sur serveur de test (après `count_even` : décision `reuse`, `fin_reemplois`, pas d'atelier) ; scénario de 28 contrôles ; syntaxe JavaScript |
| 2026-10-20 | noyau.py (`aide`, `AIDES_EXERCICE`), serveur.py (`/api/aide`), exemples/ocamltutor/language_ml.py | **indices propres à un exercice** : le fournisseur peut déclarer `AIDES_EXERCICE = {"exercice": {"catégorie": [niveau1, niveau2, niveau3]}}` ; un texte remplace l'indice général pour cet exercice, cette catégorie et ce niveau seulement (`None` garde l'indice général). La route d'aide passe le nom de l'exercice à `aide`. Usage : un indice 3 propre à chaque exercice servi pour le résultat faux (les 5 exercices du début, `count_even`, `all_positive` et les deux exercices `_fold`) : il éclaire sur des exemples du tableau ce que la fonction doit rendre et nomme l'outil d'OCaml dont l'exercice a besoin (`max`, `@`, `mod`, `&&`), sans écrire les cas Leaf et Node. Pour les exercices d'après l'atelier, il dit seulement ce qui est attendu, pas comment résoudre (mesure du réemploi spontané) | remarque de la stagiaire : certains exercices demandent un outil que l'étudiant n'écrit pas lui-même (`max` pour `height`), peut-être inconnu en début de cours, et l'indice 3 général (calcul à la main) éclairait peu ; les indices généraux, communs à tous les exercices, ne peuvent pas nommer cet outil sans égarer sur les autres. Choix fait avec elle : un indice propre à l'exercice plutôt qu'un rappel dans l'énoncé, pour garder l'énoncé du labo et ne montrer l'outil qu'aux étudiants qui bloquent. Vérifié : chaque exercice servi reçoit son niveau 3 ; niveaux 1 et 2 généraux conservés ; quatre instances chargées ; aucun mot interdit (schéma, réemploi…) |
| 2026-10-20 | exemples/ocamltutor/activities_ml.py | énoncé de `bintree_height` : ajout de la définition de la profondeur reprise du labo 05 (« La profondeur de la racine est 0, celle de ses éventuels enfants est 1, etc. ») ; énoncé de `bintree_count_nodes` : espace avant le point d'interrogation | relecture de l'alignement avec l'énoncé du labo 05 : la hauteur y est définie par la profondeur, que notre énoncé ne définissait pas. Bilan de la relecture : exercices de « Compter » (sauf `count_right` et `count_left`, écartés), `height` et `collect_values` (« dans un ordre quelconque ») conformes ; `example_tree` conforme ; exercices de la dernière section servis à la bascule sous les noms suffixés `_fold`. Le labo ne fixe pas d'ordre pour `collect_internal_nodes` : les tests trient la liste |
| 2026-10-20 | docs/FICHE_SALLE.md | liste d'avant séance : valeurs des contrats et `BASCULE_FAITE = False` ; liste de la bascule : passer `BASCULE_FAITE = True` | la fiche décrivait l'ajout manuel de trois exercices dans `REEMPLOIS` |
| 2026-10-22 | exemples/ocamltutor/language_ml.py (`AIDES_REMONTEE`) | **indices de l'atelier propres à OCaml**, à la place des textes neutres du noyau : (1) une seule chose change dans le cas Leaf, une seule dans le cas Node ; la fonction doit recevoir ces deux choses en arguments, en plus de l'arbre ; (2) ce qui change dans le cas Node est un calcul : en OCaml, il se passe en argument sous forme de fonction, par exemple `(fun g d -> g + d)` ; vérifier que `bintree_count_leaves` s'obtient en donnant 1 et cette fonction ; (3) première ligne `let rec nom z f a = match a with ...`, cas Leaf immédiat, se demander ce que `f` doit recevoir, écrire `Node (x, g, d)` et donner aussi `x` à `f` | décidé avec la stagiaire : les niveaux 1 et 2 du noyau répétaient ce que le tableau montre déjà, et aucun ne disait la vraie difficulté (passer un calcul en argument). Aucun ne donne le corps ni le nom `fold_tree`. Le niveau 3 fait garder `x`, dont `bintree_count_even` a besoin. Le noyau prévoyait déjà ce remplacement par le fournisseur ; les autres instances gardent les textes neutres. Vérifié : indices servis par la route d'aide dans l'atelier |

