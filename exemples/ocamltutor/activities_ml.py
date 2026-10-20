"""Ancrages executables pour l'instanciation OCaml de FPTutor-Shell.

Chaque ancrage : identifiant, enonce, signature, amorce, tests (expression, attendu).
Les enonces evitent tout terme qui nommerait le schema vise : ni « pli », ni
« repli », ni « fold », ni « monade », ni « propagation ».

Deux conventions propres a OCaml.

Les declarations de type figurent dans l'amorce, puisque chaque soumission est
compilee comme un module autonome. L'apprenant ne doit pas les supprimer, ce que
l'enonce rappelle une fois.

Chaque expression de test rend une chaine de caracteres, OCaml n'ayant pas
d'affichage generique. La conversion fait donc partie de l'expression de test et
non du code de l'apprenant.
"""

# Type et constructeurs du cours : voir le laboratoire 05, ou Node porte la
# valeur en premier, puis le sous-arbre gauche, puis le sous-arbre droit.
TYPE_ARBRE = ("type bintree = Leaf | Node of int * bintree * bintree\n"
              "(* ne pas modifier la ligne ci-dessus *)\n\n")

TYPE_ARBRE_UB = ("type ubtree = UbLeaf | Un of ubtree | Bin of ubtree * ubtree\n"
                 "(* ne pas modifier la ligne ci-dessus *)\n\n")

PRELUDE_OPTION = ("let premier (l : int list) : int option =\n"
                  "  match l with [] -> None | x :: _ -> Some x\n\n"
                  "let premiere (l : string list) : string option =\n"
                  "  match l with [] -> None | s :: _ -> Some s\n\n"
                  "let division (a : int) (b : int) : int option =\n"
                  "  if b = 0 then None else Some (a / b)\n\n"
                  "let vers_entier (s : string) : int option = int_of_string_opt s\n"
                  "(* ne pas modifier les quatre definitions ci-dessus *)\n\n")

# arbres de test, ajoutes aux amorces de la famille des arbres
ARBRES = ("let t0 = Leaf\n"
          "let t1 = Node (3, Leaf, Leaf)\n"
          "let t2 = Node (2, Node (1, Leaf, Leaf), Node (4, Leaf, Leaf))\n"
          "let t3 = Node (2, Node (1, Node (5, Leaf, Leaf), Leaf), Leaf)\n"
          "let example_tree = Node (2, Node (2, Leaf, Node (6, Node (5, Leaf, Leaf), Node (6, Leaf, Leaf))),\n"
          "                           Node (4, Leaf, Node (1, Node (2, Leaf, Leaf), Leaf)))\n\n")


def _amorce_arbre(signature, nom, params="a"):
    return "%s%s(* %s *)\nlet rec %s %s = failwith \"a completer\"\n" % (
        TYPE_ARBRE, ARBRES, signature, nom, params)

# différentes sections : compter, collecter et propriétés
ACTIVITES = {
 "F-arbre": [
  ("bintree_count_leaves",
   "Un arbre binaire sur les entiers : combien a-t-il de feuilles ? Écrivez la "
   "définition en distinguant le cas de la feuille du cas du nœud interne.",
   "bintree_count_leaves : bintree -> int",
   _amorce_arbre("bintree_count_leaves : bintree -> int", "bintree_count_leaves"),
   [("string_of_int (bintree_count_leaves t0)", "1"),
    ("string_of_int (bintree_count_leaves t1)", "2"),
    ("string_of_int (bintree_count_leaves t2)", "4"),
    ("string_of_int (bintree_count_leaves example_tree)", "9")]),

  ("bintree_count_internal_nodes",
   "Le même arbre : combien a-t-il de nœuds internes ?",
   "bintree_count_internal_nodes : bintree -> int",
   _amorce_arbre("bintree_count_internal_nodes : bintree -> int",
                 "bintree_count_internal_nodes"),
   [("string_of_int (bintree_count_internal_nodes t0)", "0"),
    ("string_of_int (bintree_count_internal_nodes t1)", "1"),
    ("string_of_int (bintree_count_internal_nodes t2)", "3"),
    ("string_of_int (bintree_count_internal_nodes example_tree)", "8")]),

# Ordre du laboratoire 05 : les trois exercices de la section « Compter », puis
# height (section « Proprietes »), puis collect_values (« Collectionner »).
# L'atelier s'ouvre a la 4e solution comparable : height, avec son max, figure
# donc parmi les solutions comparees (voir JOURNAL_STAGE.md, « Details sur l'ordre »).
# bintree_count_nodes remplace bintree_sum, absent du laboratoire.
  ("bintree_count_nodes",
   "Le même arbre : combien a-t-il de nœuds ?",
   "bintree_count_nodes : bintree -> int",
   _amorce_arbre("bintree_count_nodes : bintree -> int", "bintree_count_nodes"),
   [("string_of_int (bintree_count_nodes t0)", "1"),
    ("string_of_int (bintree_count_nodes t1)", "3"),
    ("string_of_int (bintree_count_nodes t2)", "7"),
    ("string_of_int (bintree_count_nodes example_tree)", "17")]),

  ("bintree_height",
   # definition de la profondeur reprise du laboratoire 05
   "Le même arbre : donnez sa hauteur, c'est-à-dire la plus grande profondeur "
   "parmi tous ses nœuds. La profondeur de la racine est 0, celle de ses éventuels "
   "enfants est 1, etc. Une feuille seule est donc de hauteur zéro.",
   "bintree_height : bintree -> int",
   _amorce_arbre("bintree_height : bintree -> int", "bintree_height"),
   [("string_of_int (bintree_height t0)", "0"),
    ("string_of_int (bintree_height t1)", "1"),
    ("string_of_int (bintree_height t3)", "3"),
    ("string_of_int (bintree_height example_tree)", "4")]),

  ("bintree_collect_values",
   "Le même arbre : donnez la liste des entiers portés par ses nœuds internes, "
   "dans un ordre quelconque.",
   "bintree_collect_values : bintree -> int list",
   _amorce_arbre("bintree_collect_values : bintree -> int list",
                 "bintree_collect_values"),
   # la liste est triee avant comparaison car le laboratoire accepte tout ordre
   [("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_values t0)))", ""),
    ("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_values t1)))", "3"),
    ("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_values t2)))", "1;2;4"),
    ("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_values example_tree)))", "1;2;2;2;4;5;6;6")]),
 ],

 "F-option": [
  ("double_tete",
   "Une liste d'entiers éventuellement vide. En utilisant premier, donnez le "
   "double du premier entier, ou l'absence de résultat si la liste est vide. "
   "Écrivez le filtrage de motifs à la main, sans les fonctions du module Option.",
   "double_tete : int list -> int option",
   PRELUDE_OPTION + "(* double_tete : int list -> int option *)\n"
   "let double_tete (l : int list) : int option = failwith \"a completer\"\n",
   [("(match double_tete [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match double_tete [4; 1] with None -> \"rien\" | Some x -> string_of_int x)", "8")]),

  ("cent_sur_tete",
   "La même liste. En utilisant premier puis division, donnez cent divisé par le "
   "premier entier. La liste peut être vide, et cet entier peut être nul.",
   "cent_sur_tete : int list -> int option",
   PRELUDE_OPTION + "(* cent_sur_tete : int list -> int option *)\n"
   "let cent_sur_tete (l : int list) : int option = failwith \"a completer\"\n",
   [("(match cent_sur_tete [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match cent_sur_tete [0] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match cent_sur_tete [4] with None -> \"rien\" | Some x -> string_of_int x)", "25")]),

  ("pipeline",
   "Une liste de chaînes. En utilisant premiere, puis vers_entier, puis division, "
   "donnez cent divisé par l'entier écrit dans la premiere chaîne. Chacune des "
   "trois étapes peut échouer.",
   "pipeline : string list -> int option",
   PRELUDE_OPTION + "(* pipeline : string list -> int option *)\n"
   "let pipeline (l : string list) : int option = failwith \"a completer\"\n",
   [("(match pipeline [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match pipeline [\"abc\"] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match pipeline [\"0\"] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match pipeline [\"5\"] with None -> \"rien\" | Some x -> string_of_int x)", "20")]),

  ("longueur_premiere",
   "Une liste de chaînes. En utilisant premiere, donnez la longueur de la "
   "premiere chaîne.",
   "longueur_premiere : string list -> int option",
   PRELUDE_OPTION + "(* longueur_premiere : string list -> int option *)\n"
   "let longueur_premiere (l : string list) : int option = failwith \"a completer\"\n",
   [("(match longueur_premiere [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match longueur_premiere [\"xy\"] with None -> \"rien\" | Some x -> string_of_int x)", "2")]),
 ],
}

# ---------------------------------------------------------------- reemplois
# EXERCICES_REEMPLOI est la reserve de tous les exercices proposes apres l'atelier.
# Le tuteur ne sert que ceux de REEMPLOIS, defini plus bas selon la phase ;
# l'extension de suivi (seance 2) choisit les siens dans cette reserve (liste
# ORDRE de suivi_serveur.py). Avant, l'extension lisait REEMPLOIS : reduire la
# phase 1 lui aurait retire ses exercices.
EXERCICES_REEMPLOI = {
 "F-arbre": [
  ("bintree_count_even",
   "Un arbre binaire sur les entiers : combien de ses nœuds internes portent un "
   "entier pair ? Toute solution correcte est acceptée.",
   "bintree_count_even : bintree -> int",
   _amorce_arbre("bintree_count_even : bintree -> int", "bintree_count_even"),
   [("string_of_int (bintree_count_even t0)", "0"),
    ("string_of_int (bintree_count_even t1)", "0"),
    ("string_of_int (bintree_count_even t2)", "2"),
    ("string_of_int (bintree_count_even t3)", "1"),
    ("string_of_int (bintree_count_even (Node (6, Node (8, Leaf, Leaf), Node (5, Leaf, Leaf))))", "2"),
    ("string_of_int (bintree_count_even (Node (3, Node (-2, Leaf, Leaf), Node (7, Leaf, Node (4, Leaf, Leaf)))))", "2")]),

  ("bintree_min",
   "Un arbre binaire sur les entiers : donnez le plus petit entier porte par un "
   "nœud interne, ou l'absence de résultat si l'arbre est une feuille. Vous "
   "pouvez employer ce que vous venez d'écrire, ou reprendre la récursion à la main.",
   "bintree_min : bintree -> int option",
   _amorce_arbre("bintree_min : bintree -> int option", "bintree_min"),
   [("(match bintree_min t0 with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match bintree_min t1 with None -> \"rien\" | Some x -> string_of_int x)", "3"),
    ("(match bintree_min t2 with None -> \"rien\" | Some x -> string_of_int x)", "1"),
    ("(match bintree_min (Node (5, Node (7, Leaf, Leaf), Node (3, Leaf, Leaf))) with None -> \"rien\" | Some x -> string_of_int x)", "3"),
    ("(match bintree_min (Node (4, Node (6, Node (-2, Leaf, Leaf), Leaf), Leaf)) with None -> \"rien\" | Some x -> string_of_int x)", "-2"),
    ("(match bintree_min (Node (1, Node (5, Leaf, Leaf), Node (8, Leaf, Leaf))) with None -> \"rien\" | Some x -> string_of_int x)", "1")]),

  ("bintree_all_positive",
   "Le même arbre : tous les entiers portés par ses nœuds internes sont-ils "
   "strictement positifs ?",
   "bintree_all_positive : bintree -> bool",
   _amorce_arbre("bintree_all_positive : bintree -> bool", "bintree_all_positive"),
   [("string_of_bool (bintree_all_positive t0)", "true"),
    ("string_of_bool (bintree_all_positive t2)", "true"),
    ("string_of_bool (bintree_all_positive t3)", "true"),
    ("string_of_bool (bintree_all_positive (Node (-1, Leaf, Leaf)))", "false"),
    ("string_of_bool (bintree_all_positive (Node (2, Node (3, Leaf, Leaf), Node (-4, Leaf, Leaf))))", "false"),
    ("string_of_bool (bintree_all_positive (Node (2, Node (0, Leaf, Leaf), Leaf)))", "false")]),

  ("ubtree_count_bin",
   "On considère maintenant un arbre dont chaque nœud a un ou deux sous-arbres. "
   "Combien a-t-il de nœuds à deux sous-arbres ?",
   "ubtree_count_bin : ubtree -> int",
   TYPE_ARBRE_UB +
   "let u0 = UbLeaf\nlet u1 = Bin (UbLeaf, UbLeaf)\n"
   "let u2 = Un (Bin (Un UbLeaf, UbLeaf))\n\n"
   "(* ubtree_count_bin : ubtree -> int *)\n"
   "let rec ubtree_count_bin a = failwith \"a completer\"\n",
   [("string_of_int (ubtree_count_bin u0)", "0"),
    ("string_of_int (ubtree_count_bin u1)", "1"),
    ("string_of_int (ubtree_count_bin u2)", "1"),
    ("string_of_int (ubtree_count_bin (Bin (Bin (UbLeaf, UbLeaf), Un (Bin (UbLeaf, UbLeaf)))))", "3"),
    ("string_of_int (ubtree_count_bin (Un (Un UbLeaf)))", "0")]),

  # Les deux exercices de la derniere section du laboratoire 05 (« Fonctions
  # d'ordre superieur »), servis seulement apres la bascule : ils nomment
  # fold_tree. Suffixe _fold pour les distinguer, dans les donnees, des exercices
  # de meme sujet du debut. Aucune solution employant fold_tree n'est deposee
  # dans le depot (consigne du guide : le corrige n'y figure pas).
  ("bintree_count_internal_nodes_fold",
   "Réécrivez la fonction qui compte les nœuds internes en employant fold_tree. "
   "Définissez d'abord fold_tree (vous pouvez reprendre la définition que vous "
   "avez écrite), puis bintree_count_internal_nodes_fold, qui ne doit pas "
   "s'appeler elle-même.",
   "bintree_count_internal_nodes_fold : bintree -> int",
   TYPE_ARBRE + ARBRES +
   "(* Definissez fold_tree, puis la fonction ci-dessous en l'employant *)\n"
   "(* bintree_count_internal_nodes_fold : bintree -> int *)\n"
   "let bintree_count_internal_nodes_fold a = failwith \"a completer\"\n",
   [("string_of_int (bintree_count_internal_nodes_fold t0)", "0"),
    ("string_of_int (bintree_count_internal_nodes_fold t1)", "1"),
    ("string_of_int (bintree_count_internal_nodes_fold t2)", "3"),
    ("string_of_int (bintree_count_internal_nodes_fold example_tree)", "8")]),

  ("bintree_collect_internal_nodes_fold",
   "Réécrivez la fonction qui donne la liste des entiers portés par les nœuds "
   "internes, dans un ordre quelconque, en employant fold_tree. Définissez d'abord "
   "fold_tree, puis bintree_collect_internal_nodes_fold, qui ne doit pas "
   "s'appeler elle-même.",
   "bintree_collect_internal_nodes_fold : bintree -> int list",
   TYPE_ARBRE + ARBRES +
   "(* Definissez fold_tree, puis la fonction ci-dessous en l'employant *)\n"
   "(* bintree_collect_internal_nodes_fold : bintree -> int list *)\n"
   "let bintree_collect_internal_nodes_fold a = failwith \"a completer\"\n",
   # liste triee avant comparaison, comme pour collect_values
   [("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_internal_nodes_fold t0)))", ""),
    ("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_internal_nodes_fold t1)))", "3"),
    ("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_internal_nodes_fold t2)))", "1;2;4"),
    ("String.concat \";\" (List.map string_of_int (List.sort compare (bintree_collect_internal_nodes_fold example_tree)))", "1;2;2;2;4;5;6;6")]),
 ],

 "F-option": [
  ("mille_sur_tete",
   "Une liste d'entiers : donnez mille divisé par le premier. Vous pouvez employer "
   "ce que vous venez d'écrire, ou reprendre les cas à la main.",
   "mille_sur_tete : int list -> int option",
   PRELUDE_OPTION + "(* mille_sur_tete : int list -> int option *)\n"
   "let mille_sur_tete (l : int list) : int option = failwith \"a completer\"\n",
   [("(match mille_sur_tete [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match mille_sur_tete [0] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match mille_sur_tete [8] with None -> \"rien\" | Some x -> string_of_int x)", "125")]),

  ("lier",
   "On remplace l'absence de resultat par un resultat porteur d'un message : "
   "type ('a, 'e) resultat = Ok of 'a | Erreur of 'e. Ecrivez la fonction qui "
   "enchaine une etape sur ce type.",
   "lier : ('a, 'e) resultat -> ('a -> ('b, 'e) resultat) -> ('b, 'e) resultat",
   "type ('a, 'e) resultat = Ok of 'a | Erreur of 'e\n"
   "(* ne pas modifier la ligne ci-dessus *)\n\n"
   "let montrer r = match r with Ok n -> string_of_int n | Erreur m -> m\n\n"
   "(* lier : ('a, 'e) resultat -> ('a -> ('b, 'e) resultat) -> ('b, 'e) resultat *)\n"
   "let lier r f = failwith \"a completer\"\n",
   [("montrer (lier (Ok 4) (fun x -> Ok (2 * x)))", "8"),
    ("montrer (lier (Erreur \"vide\") (fun x -> Ok (2 * x)))", "vide")]),
 ],
}


# ------------------------------------------------- phases du reemploi
# Phase 1 (labo 05) : un seul exercice, le transfert sans consigne de methode,
# qui porte la mesure principale (docs/SEANCE2.md). Le tuteur annoncera alors un
# reemploi sur deux et s'arretera la : c'est voulu, reemploi_requis reste a 2.
#
# Bascule (la veille du labo 06) : passer BASCULE_FAITE a True, relancer la
# batterie, puis relancer le serveur en gardant l'etat (./relancer.sh --garder).
# S'ajoutent alors, dans cet ordre, les deux reecritures du laboratoire avec
# fold_tree (la forme est donnee) puis le second transfert, sans consigne de
# methode. Le tuteur sert un exercice que l'apprenant n'a pas encore recu : les
# dossiers deja constitues ne changent pas.
BASCULE_FAITE = False

PHASE_1 = ["bintree_count_even"]
PHASE_2 = ["bintree_count_internal_nodes_fold", "bintree_collect_internal_nodes_fold",
           "bintree_all_positive"]


def _selection(famille, noms):
    par_nom = {a[0]: a for a in EXERCICES_REEMPLOI[famille]}
    return [par_nom[n] for n in noms]


REEMPLOIS = {
 "F-arbre": _selection("F-arbre", PHASE_1 + (PHASE_2 if BASCULE_FAITE else [])),
 "F-option": EXERCICES_REEMPLOI["F-option"],
}
