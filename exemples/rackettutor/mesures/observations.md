# Observations consignées pendant l'instanciation (avant toute correction)

## E1 engendrement
- O1 (atelier) : aucun referentiel.json copié. La v2 n'en a pas à la racine et
  creer_tuteur ne cherche qu'un niveau sous la racine ; l'omission est silencieuse.
- O2 (atelier) : le gabarit d'activités décrit et engendre des quadruplets
  (nom, enonce, amorce, tests) alors que noyau et serveur indexent des quintuplets
  (nom, enonce, signature, amorce, tests) : act[4] lèverait IndexError.
- O3 (atelier) : le LISEZMOI engendré prescrit `python3 fptutor rackettutor`,
  commande inexistante dans l'archive.

## E4 banc d'essai (fournisseur Racket, première passe)
- Réunion arbre : 8 écritures équivalentes, 1 terme (prédicats, match, if, branches
  inversées, ordre libre des opérandes n-aires, lambda). Aucune correction.
- O4 (atelier, banc) : SÉPARATION ÉCHEC entre « accumulateur (let nommé) » et
  « boucle for/sum », toutes deux de forme `iterative`. Or deux formes non
  alignables sont toutes deux refusées au corpus : leur coïncidence est sans
  effet sur l'alignement. Le banc exige une séparation qui n'a pas d'objet hors
  des formes admissibles. L'instance OCaml passait ce contrôle par accident : son
  accumulateur rendait un `pas` résiduel, « (aux 0 a) », qui le distinguait.
- O5 (fournisseur) : RÉUNION ÉCHEC option, `(* n 2)` contre `(* 2 x)`. La
  commutativité du fournisseur, calquée sur OCaml, ne déplace que les REC.
  Correction locale au fournisseur : tri complet des opérandes des sommes et
  produits plats, sûr pour + et * sur les nombres.
- O6 (fuite du langage, banc) : sans « messages » dans le jeu de cas, le banc
  éprouve le fournisseur sur des messages de GHC (« non-exhaustive patterns »,
  « Variable not in scope ») et déclare trois échecs pour un fournisseur non
  Haskell. Septième fuite de Haskell dans le cadre commun.

## E7 familles et obligations (coquille non modifiée)
- Console (noyau.etat_des_familles, patch 7 de la v2) : F-arbre 2 points pour 2
  annoncés, F-option 1 pour 1, conformes. Aucune modification.
- O7 (fuite du langage, outil d'auteur) : `obligations.py` ignore TUTOR_LANGUAGE
  et induit les obligations des familles Haskell (F-fold, maximumS, moyenneS…)
  sans erreur ni avertissement. Le défaut était signalé par le rapport OCaml,
  contourné là par un adaptateur de 40 lignes hors coquille, et non corrigé dans
  la v2 : sans correction, chaque instance doit récrire cet adaptateur, ou
  croire à un résultat qui porte sur un autre langage.
- O8 (fuite du langage, outil d'auteur) : `generateur.py`, prescrit par le
  LISEZMOI engendré comme « vérification finale », échoue faute de
  referentiel.json à la racine et reste lié à l'analyseur Haskell. La console
  en tient désormais lieu ; le LISEZMOI doit y renvoyer.

## E8 essai à blanc (mesure de réemploi de la coquille v2)
- Politique : séquence identique à l'essai OCaml, sans écart. Corpus insuffisant
  (1, puis 2), mise à l'écart d'une solution par `foldl` (no-recursion),
  alignement à 2 points mais instable à 3 solutions, atelier ouvert à 4.
- O9 (défaut de mesure, récurrent) : deux faux positifs sur la mesure de
  réemploi. Une enveloppe `(define (bintree-count-even t) (compte t))` autour
  d'une récursion écrite à la main est comptée comme réemploi ; une définition
  par `define/contract`, que l'analyse ne lit pas, l'est aussi. Ce sont les deux
  défauts trouvés par l'instance OCaml. Ils y avaient été corrigés dans
  l'instance (normalisateur et extension de suivi), non dans la coquille :
  `noyau.schema_employe` compte toujours une forme non analysable comme un
  réemploi et ne demande aucune abstraction d'ordre supérieur. Une correction
  faite dans une instance ne protège pas la suivante.
- O10 (fournisseur, trouvé par l'essai et non par le banc) : l'accesseur appliqué
  à une feuille était classé `incompatible-types`. Le jeu de cas avait été écrit
  d'après une structure opaque (« given: #<leaf> ») ; les structures du cours
  sont `#:transparent` et Racket écrit alors « given: (leaf) ». Règle réécrite
  sur la forme de l'accesseur, et le message réel ajouté au jeu de cas. Le banc
  ne vaut que par les messages qu'on lui donne : ils doivent être relevés sur
  l'interprète, avec les déclarations mêmes de l'amorce.

## E8 étayage sur erreur
- O11 (fuite du langage, la plus visible pour l'apprenant) : l'échelle d'aide du
  noyau est écrite pour Haskell et pour les listes. Sous Racket, un cas de base
  absent reçoit « il vous manque une équation dont le motif est [] » ; une erreur
  de type, « demandez à GHCi le type de la fonction citée, avec :t » ; une
  parenthèse manquante, « une équation tient sur une ligne, ou ses suites sont
  indentées ». Les catégories sont communes, les textes qui leur sont attachés ne
  le sont pas. L'instance OCaml recevait les mêmes textes. Même nature pour les
  lectures immédiates (« le compilateur… ») et pour la charpente du mode exposé,
  écrite `f (x:xs) = …`.

## E9 service HTTP
- Titres « RacketTutor — parcours » et « RacketTutor4Teacher — console »,
  « compilées par Racket », inscription par pseudonyme, soumission erronée
  classée `missing-base-case` avec la lecture et l'aide Racket, console :
  familles conformes. Aucune modification pour cela.
- O12 (défaut de la couche de politique, indépendant du langage, trouvé par
  l'essai HTTP et invisible à l'essai à blanc) : la condition de stabilité est
  neutralisée par toute lecture de l'état. `decider` enregistre le compte
  d'alignement à chaque appel, et `vue_apprenant` l'appelle à chaque
  `/api/etat`. Or la page étudiante relit l'état après chaque soumission
  réussie (avance automatique). À la troisième solution, la soumission rend
  « le tuteur vérifie sur une solution de plus », puis la relecture qui suit
  compare le compte à lui-même et ouvre l'atelier. Vérifié : trois soumissions
  puis trois lectures de /api/etat donnent « abstraction » dès la première
  lecture, corpus de 3. Sans lecture intermédiaire, l'atelier s'ouvre à 4.
  L'essai à blanc appelle `decider` une fois par soumission et ne pouvait pas le
  voir. Le défaut touche toutes les instances déployées, dont OCamlTutor.
