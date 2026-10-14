# OCamlTutor : instanciation depuis FPTutor-Shell, état au terme de la session

## Ce qui a été fait, avec les outils du shell

**Répertoire engendré par l'atelier.** `python3 creer_tuteur.py ml mltutor
--interprete ocaml --extension .ml` a produit `mltutor/` avec le gabarit du
fournisseur, le squelette d'ancrages, une copie du référentiel et la marche à
suivre. Rien du shell n'a été modifié.

**Fournisseur écrit.** `language_ml.py` expose les cinq éléments. L'analyse est
déléguée à `normalisation_ml.py`, comme le fournisseur Haskell délègue à
`normalisation2`. Le vocabulaire rendu est celui du cadre : C1..Cn, REC, COND,
LIST, NOTHING, applications préfixes.

Exemples de formes canoniques obtenues, dans l'ordre recommandé par le LISEZMOI
de l'atelier, c'est-à-dire avant tout branchement :

| définition | base | pas |
|---|---|---|
| `somme` sur arbre | `0` | `((C2 + REC) + REC)` |
| `hauteur` | `0` | `(1 + (max REC REC))` |
| `feuilles` | `1` | `(REC + REC)` |
| chaînage `option` | `NOTHING` | `(Some (String.length C1))` |

**Banc d'essai du shell passé.** `python3 banc_essai.py language_ml --tuteur
mltutor --cas ../mltutor/cas_ml.json` : onze écritures, six termes distincts.
Réunion vérifiée, les six écritures équivalentes rendant le même terme, y compris
l'inversion des opérandes, l'inversion des branches, le renommage des variables,
les annotations de type et l'écriture avec `function`. Séparation vérifiée, les
cinq écritures distinctes rendant des termes distincts : pli de bibliothèque,
accumulateur, absence de filtrage, opération différente, combinaison
dissymétrique. Les quatre messages du compilateur OCaml se projettent sur les
bonnes catégories.

**Familles validées avec le moteur du cadre.** `valider_familles_ml.py` reprend la
chaîne de `normalisation2.aligner_corps` en passant par le fournisseur, et
l'anti-unificateur de `remontee.py` reste inchangé. Résultats : la famille du pli
sur arbre est conforme à deux points de variation en granularité blocs, la famille
du chaînage sur `option` est conforme à un point.

## Trois résultats à consigner pour l'article sur la généricité

**L'inducteur d'obligations désigne `aplatir`, et non `hauteur`.** À la
granularité fine, le retrait d'`aplatir` fait passer l'alignement de deux à quatre
points : c'est le seul ancrage dont le pas a une forme différente, et c'est lui qui
force la généralisation au niveau des blocs. Mon hypothèse de rédaction plaçait
l'ancre porteuse sur `hauteur` et sur `feuilles` ; le moteur les déclare
interchangeables. L'obligation de la famille doit être réécrite d'après ce que
l'inducteur établit.

**Aucune obligation n'est induite pour la famille `option`.** Ni en blocs ni en
fine granularité. L'obligation de l'ancre à trois étapes porte donc sur la
perception du bruit par l'apprenant et non sur l'alignement : elle reste une
justification pédagogique, pas un fait vérifiable par le validateur. C'est à écrire
comme tel plutôt que de laisser croire au lecteur que l'inducteur la confirme.

**`obligations.py` et `generateur.py` ne sont pas agnostiques du fournisseur.**
Tous deux importent `normalisation2` directement, donc l'analyseur Haskell, et ne
peuvent pas valider une famille écrite dans un autre langage. La validation
ci-dessus a exigé un adaptateur de quarante lignes, placé à côté du shell et non
dedans, qui réutilise `remontee.antiunifier` sans le toucher. C'est précisément le
genre de frontière que l'article sur la généricité doit rapporter : la couche de
politique et l'anti-unificateur sont bien indépendants du langage, les deux outils
d'auteur ne le sont pas encore.

## Ce qui reste, dans l'ordre

1. Écrire `activities_ml.py` : les énoncés, amorces et tests des ancrages, en
   reprenant les définitions de type de la séance 6 du cours. C'est l'essentiel de
   l'effort restant, et l'atelier ne le réduit pas.
2. Compiler les solutions de référence et les tests avec le compilateur OCaml de
   la salle, ce qui n'a pas pu être fait ici, faute de compilateur.
3. Vérifier `test_template` contre le compilateur : le gabarit actuel suppose une
   fonction `afficher` ; à remplacer par la conversion propre à chaque type de
   sortie, ou à simplifier en `print_endline (string_of_int ...)` selon les tests.
4. Réécrire l'obligation de la famille du pli d'après l'inducteur.
5. Brancher la couche d'étude sur la journalisation du serveur.

## Remarque sur l'archive transmise

Le dossier `donneesExperimentales/` contient treize fichiers dont le LISEZMOI
précise que les données sont simulées et que seuls les formats comptent. Le fichier
de correspondance marqué comme non transmissible ne contient que sa ligne d'en-tête
et un exemple dont les champs nominatifs sont des marqueurs. Aucune donnée
d'étudiant réelle ne figure donc dans l'archive, et je n'ai ouvert aucun autre
fichier de ce dossier que son LISEZMOI et les en-têtes de colonnes.

## Ancrages écrits, et ce qu'ils donnent

`activities_ml.py` contient neuf ancrages d'instance et cinq réemplois, au format
du quintuplet attendu par le noyau, identifiant, énoncé, signature, amorce et
tests. Les énoncés évitent tout terme qui nommerait le schéma.

Deux conventions propres à OCaml, qui n'existaient pas pour Haskell ni pour
Python. Les déclarations de type figurent dans l'amorce, puisque chaque soumission
est compilée comme un module autonome, et l'énoncé rappelle une fois de ne pas les
modifier ; le normalisateur ignore désormais les déclarations `type` et `open` au
premier niveau, ce qui était nécessaire pour que l'analyse aboutisse sur une
soumission complète. Et chaque expression de test rend une chaîne, OCaml n'ayant
pas d'affichage générique, donc la conversion appartient à l'expression de test et
non au code de l'apprenant. `test_template` est corrigé en conséquence.

Formes canoniques obtenues sur les neuf solutions de référence :

| ancrage | base | pas |
|---|---|---|
| somme | `0` | `((C2 + REC) + REC)` |
| produit | `1` | `((C2 * REC) * REC)` |
| hauteur | `0` | `(1 + (max REC REC))` |
| feuilles | `1` | `(REC + REC)` |
| aplatir | `[]` | `(REC @ (C2 :: REC))` |
| double_tete | `NOTHING` | `(Some (2 * C1))` |
| cent_sur_tete | `NOTHING` | `(division 100 C1)` |
| pipeline | `NOTHING` | `(etape C1)` |
| longueur_premiere | `NOTHING` | `(Some (String.length C1))` |

La détection du réemploi se comporte comme il faut : une solution qui emploie le
schéma est rendue en forme `no-recursion`, donc comptée comme réemploi par
`schema_employe`, tandis qu'une solution qui refait la récursion à la main reste en
forme `constructors` avec `REC` dans son pas.

Le préambule de la famille `option` fournit `premier`, `premiere`, `division` et
`vers_entier` dans l'amorce : sans ces quatre définitions, les énoncés porteraient
sur deux difficultés à la fois, la recherche et la propagation, alors que seule la
seconde est visée.

## Alignement sur le cours, d'apres le site des laboratoires

Trois informations du site changent l'instance, et l'une change le plan.

**Compilateur.** Le cours retient la version LTS d'OCaml, soit 4.14.2, installee
par opam. Le mode script de l'interprete suffit, `ocaml fichier.ml` etant
explicitement employe au laboratoire 01, donc aucune compilation separee n'est
necessaire. `command` devient `["ocaml", "-w", "+8", chemin]` : l'option rend
explicite l'avertissement de filtrage non exhaustif, qui est ce que la categorie
`missing-base-case` projette. Deux precautions logistiques figurent dans le
laboratoire 01 et valent pour la seance : dans les salles du LAMISS, le dossier
personnel etant lent, `OPAMROOT` doit etre deplace vers `/tmp` a chaque
connexion ; et l'interprete en ligne du site officiel est propose comme solution
de repli. Cette seconde possibilite conforte la modalite a distance.

**Type et constructeurs.** Le laboratoire 05 definit `bintree` avec `Leaf` et
`Node`, et `Node` porte la valeur en premier, puis le sous-arbre gauche, puis le
droit. L'instance est corrigee en consequence, de meme que les noms de fonctions,
qui reprennent ceux du cours : `bintree_count_leaves`,
`bintree_count_internal_nodes`, `bintree_sum`, `bintree_height`,
`bintree_collect_values`. Les reemplois deviennent `bintree_min`,
`bintree_all_positive`, et l'item de transfert `ubtree_count_bin`. Les familles
restent conformes avec le moteur de la coquille : deux points de variation en
blocs pour la famille des arbres, un pour la famille `option`.

**Le laboratoire 05 realise deja, a la main, le dispositif que le tuteur
mecanise.** Il fait ecrire une longue serie de definitions recursives
structurellement identiques, compter les feuilles, compter les noeuds internes,
compter les noeuds, la hauteur, la collecte des valeurs, les trois parcours, puis
il demande, dans sa derniere section seulement, d'ecrire `fold_tree` « dont le
fonctionnement generalise celui de `fold_right` pour des arbres binaires », et de
reecrire deux des fonctions precedentes avec elle.

C'est exactement l'ordre que defend l'article, obtenu sans tuteur, et cela a deux
consequences. La premiere est un argument de collaboration : la proposition ne
demande pas a l'enseignant d'adopter une pedagogie, elle mecanise la sienne. La
seconde est une contrainte : le schema est nomme a la fin du laboratoire 05, donc
l'activite doit se placer dans ce laboratoire et non apres. Ce que le tuteur
ajoute alors est precis : il decide du moment de la denomination pour chaque
apprenant, a partir de ses propres solutions, au lieu de le fixer a la derniere
section pour tout le monde.

La question a poser a Samuele Giraudo devient donc : quel jeudi tombe le
laboratoire 05, et accepterait-il que les sections « Compter », « Proprietes » et
« Collectionner » soient faites dans le tuteur, la derniere section restant la
sienne. C'est une demande plus petite que celle d'un creneau entier, et plus
naturelle.

## Essai a blanc, execute

Le compilateur OCaml 4.14.1 a ete installe, soit la version du cours a un
correctif pres, et la chaine complete a tourne.

**Compilation des references.** Les quatorze ancrages, instances et reemplois
compris, compilent et passent leurs tests avec le gabarit du fournisseur et
`ocaml -w +8`. Aucune correction des enonces n'a ete necessaire, une seule des
solutions de reference ayant du etre reecrite, le pipeline a trois etapes, dont
la version initiale imbriquait mal les `match`.

**Session complete, par le noyau du cadre.** `essai_a_blanc.py` rejoue ce que
fait un apprenant, sans interface : evaluation par le compilateur, admission au
corpus, alignement, decision de la politique, atelier, reemplois. Le deroulement
observe est exactement celui que le dispositif prevoit.

Les deux premieres soumissions sont admises et la politique repond « corpus
insuffisant ». La troisieme, ecrite avec `List.fold_left`, est correcte, passe
ses tests, et n'est pas admise : le motif rendu est « correcte mais non alignable
(no-recursion) », et elle part au registre des problemes resolus autrement. A la
quatrieme, le corpus atteint trois solutions et l'alignement vaut deux points,
mais la politique refuse encore, avec le motif « alignement a 2 points mais
instable » : c'est la troisieme conjonction de la porte qui joue. A la cinquieme,
la stabilite est confirmee et l'atelier s'ouvre.

L'atelier affiche les quatre definitions de l'apprenant avec leur cas de base et
leur cas recursif, annonce deux blocs de variation, et sert les trois niveaux
d'etayage, dont aucun ne nomme le schema. La generalisation ecrite est acceptee,
puis les deux items de reemploi sont servis et le concept passe a l'etat suivant.

**Un defaut trouve par l'essai, et corrige.** Une solution de reemploi ecrite a
la main, avec un filtrage sur un couple sans parentheses, n'etait pas analysable
par le fournisseur ; or `schema_employe` traite une forme non analysable comme un
reemploi, de sorte qu'une recursion ecrite a la main etait comptee comme un
emploi du schema. C'est un faux positif sur la mesure principale de l'etude. Le
normalisateur accepte desormais les motifs et les scrutines en n-uplet sans
parentheses, et la meme soumission est correctement rendue en forme
`constructors` avec `REC` dans son pas, donc comptee comme non-reemploi.

Le point merite d'etre rapporte au-dela de la correction : la permissivite de
`schema_employe` devant une forme non analysable transforme un defaut de
couverture du normalisateur en erreur de mesure, et dans le sens qui flatte le
dispositif. Pour l'experimentation, la regle prudente est de compter une forme
non analysable comme un non-reemploi et de la signaler dans le journal.

**Reproduire l'essai.**

    apt-get install -y ocaml-nox        # 4.14.1, ou opam switch 4.14.2
    cd FPTutor/mltutor
    python3 compiler_references.py
    TUTOR_DIR=mltutor TUTOR_LANGUAGE=language_ml python3 essai_a_blanc.py
    python3 valider_familles_ml.py
    cd ../fptutor-shell && python3 banc_essai.py language_ml --tuteur mltutor --cas ../mltutor/cas_ml.json
