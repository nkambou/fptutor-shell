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
   "Un arbre binaire sur les entiers : combien a-t-il de feuilles ? Ecrivez la "
   "definition en distinguant le cas de la feuille du cas du noeud interne.",
   "bintree_count_leaves : bintree -> int",
   _amorce_arbre("bintree_count_leaves : bintree -> int", "bintree_count_leaves"),
   [("string_of_int (bintree_count_leaves t0)", "1"),
    ("string_of_int (bintree_count_leaves t1)", "2"),
    ("string_of_int (bintree_count_leaves t2)", "4"),
    ("string_of_int (bintree_count_leaves example_tree)", "9")]),

  ("bintree_count_internal_nodes",
   "Le meme arbre : combien a-t-il de noeuds internes ?",
   "bintree_count_internal_nodes : bintree -> int",
   _amorce_arbre("bintree_count_internal_nodes : bintree -> int",
                 "bintree_count_internal_nodes"),
   [("string_of_int (bintree_count_internal_nodes t0)", "0"),
    ("string_of_int (bintree_count_internal_nodes t1)", "1"),
    ("string_of_int (bintree_count_internal_nodes t2)", "3"),
    ("string_of_int (bintree_count_internal_nodes example_tree)", "8")]),

# height en troisième
# avec une operation de combinaison qui varie (+ puis max pour augmenter les points de variation) (voir JOURNAL_STAGE.md pour détails)
  ("bintree_height",
   "Le meme arbre : donnez sa hauteur, c'est-a-dire la plus grande profondeur "
   "parmi tous ses noeuds. Une feuille est de hauteur zero.",
   "bintree_height : bintree -> int",
   _amorce_arbre("bintree_height : bintree -> int", "bintree_height"),
   [("string_of_int (bintree_height t0)", "0"),
    ("string_of_int (bintree_height t1)", "1"),
    ("string_of_int (bintree_height t3)", "3"),
    ("string_of_int (bintree_height example_tree)", "4")]),

# remplacement de bintree_sum par les différents candidats pour le banc d'essai
  ("bintree_count_nodes",
   "Le même arbre : combien a-t-il de noeuds? "
   ,
   "bintree_count_nodes : bintree -> int",
   _amorce_arbre("bintree_count_nodes : bintree -> int", "bintree_count_nodes"),
   [("string_of_int (bintree_count_nodes t0)", "1"),
    ("string_of_int (bintree_count_nodes t1)", "3"),
    ("string_of_int (bintree_count_nodes t2)", "7"),
    ("string_of_int (bintree_count_nodes example_tree)", "17")]),

  ("bintree_collect_values",
   "Le meme arbre : donnez la liste des entiers portes par ses noeuds internes, "
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
   "Une liste d'entiers eventuellement vide. En utilisant premier, donnez le "
   "double du premier entier, ou l'absence de resultat si la liste est vide. "
   "Ecrivez le filtrage de motifs a la main, sans les fonctions du module Option.",
   "double_tete : int list -> int option",
   PRELUDE_OPTION + "(* double_tete : int list -> int option *)\n"
   "let double_tete (l : int list) : int option = failwith \"a completer\"\n",
   [("(match double_tete [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match double_tete [4; 1] with None -> \"rien\" | Some x -> string_of_int x)", "8")]),

  ("cent_sur_tete",
   "La meme liste. En utilisant premier puis division, donnez cent divise par le "
   "premier entier. La liste peut etre vide, et cet entier peut etre nul.",
   "cent_sur_tete : int list -> int option",
   PRELUDE_OPTION + "(* cent_sur_tete : int list -> int option *)\n"
   "let cent_sur_tete (l : int list) : int option = failwith \"a completer\"\n",
   [("(match cent_sur_tete [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match cent_sur_tete [0] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match cent_sur_tete [4] with None -> \"rien\" | Some x -> string_of_int x)", "25")]),

  ("pipeline",
   "Une liste de chaines. En utilisant premiere, puis vers_entier, puis division, "
   "donnez cent divise par l'entier ecrit dans la premiere chaine. Chacune des "
   "trois etapes peut echouer.",
   "pipeline : string list -> int option",
   PRELUDE_OPTION + "(* pipeline : string list -> int option *)\n"
   "let pipeline (l : string list) : int option = failwith \"a completer\"\n",
   [("(match pipeline [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match pipeline [\"abc\"] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match pipeline [\"0\"] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match pipeline [\"5\"] with None -> \"rien\" | Some x -> string_of_int x)", "20")]),

  ("longueur_premiere",
   "Une liste de chaines. En utilisant premiere, donnez la longueur de la "
   "premiere chaine.",
   "longueur_premiere : string list -> int option",
   PRELUDE_OPTION + "(* longueur_premiere : string list -> int option *)\n"
   "let longueur_premiere (l : string list) : int option = failwith \"a completer\"\n",
   [("(match longueur_premiere [] with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match longueur_premiere [\"xy\"] with None -> \"rien\" | Some x -> string_of_int x)", "2")]),
 ],
}


REEMPLOIS = {
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
   "noeud interne, ou l'absence de resultat si l'arbre est une feuille. Vous "
   "pouvez employer ce que vous venez d'ecrire, ou reprendre la recursion a la main.",
   "bintree_min : bintree -> int option",
   _amorce_arbre("bintree_min : bintree -> int option", "bintree_min"),
   [("(match bintree_min t0 with None -> \"rien\" | Some x -> string_of_int x)", "rien"),
    ("(match bintree_min t1 with None -> \"rien\" | Some x -> string_of_int x)", "3"),
    ("(match bintree_min t2 with None -> \"rien\" | Some x -> string_of_int x)", "1"),
    ("(match bintree_min (Node (5, Node (7, Leaf, Leaf), Node (3, Leaf, Leaf))) with None -> \"rien\" | Some x -> string_of_int x)", "3"),
    ("(match bintree_min (Node (4, Node (6, Node (-2, Leaf, Leaf), Leaf), Leaf)) with None -> \"rien\" | Some x -> string_of_int x)", "-2"),
    ("(match bintree_min (Node (1, Node (5, Leaf, Leaf), Node (8, Leaf, Leaf))) with None -> \"rien\" | Some x -> string_of_int x)", "1")]),

  ("bintree_all_positive",
   "Le meme arbre : tous les entiers portes par ses noeuds internes sont-ils "
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
   "On considere maintenant un arbre dont chaque noeud a un ou deux sous-arbres. "
   "Combien a-t-il de noeuds a deux sous-arbres ?",
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
 ],

 "F-option": [
  ("mille_sur_tete",
   "Une liste d'entiers : donnez mille divise par le premier. Vous pouvez employer "
   "ce que vous venez d'ecrire, ou reprendre les cas a la main.",
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
