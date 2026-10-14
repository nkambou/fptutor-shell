"""Ancrages executables pour l'instanciation Racket de FPTutor-Shell.

Meme contenu pedagogique qu'OCamlTutor : memes familles, memes ancrages, memes
reemplois, memes valeurs attendues. Seules changent les conventions de Racket.

Chaque ancrage est un quintuplet : identifiant, enonce, signature, amorce, tests
(expression, valeur attendue). Les enonces evitent tout terme qui nommerait le
schema vise.

Trois conventions propres a Racket.

Les structures sont declarees dans l'amorce, comme les types en OCaml, et
l'analyse en depend : c'est la declaration (struct node (v l r)) qui dit que
node-l designe le deuxieme champ. L'apprenant ne doit pas la modifier.

Les expressions de test sont ecrites telles quelles : le gabarit du fournisseur
affiche toute valeur avec ~a, sans conversion dans l'expression.

L'absence s'ecrit #f, et les valeurs attendues en portent la forme affichee.
"""

TYPE_ARBRE = (";; ne pas modifier les deux declarations ci-dessous\n"
              "(struct leaf () #:transparent)\n"
              "(struct node (v l r) #:transparent)\n\n")

TYPE_ARBRE_UB = (";; ne pas modifier les trois declarations ci-dessous\n"
                 "(struct ub-leaf () #:transparent)\n"
                 "(struct un (t) #:transparent)\n"
                 "(struct bin (l r) #:transparent)\n\n")

PRELUDE_OPTION = (";; ne pas modifier les quatre definitions ci-dessous\n"
                  "(define (premier l) (if (null? l) #f (first l)))\n"
                  "(define (premiere l) (if (null? l) #f (first l)))\n"
                  "(define (division a b) (if (= b 0) #f (quotient a b)))\n"
                  "(define (vers-entier s)\n"
                  "  (let ([n (string->number s)]) (and (exact-integer? n) n)))\n\n")

ARBRES = ("(define t0 (leaf))\n"
          "(define t1 (node 3 (leaf) (leaf)))\n"
          "(define t2 (node 2 (node 1 (leaf) (leaf)) (node 4 (leaf) (leaf))))\n"
          "(define t3 (node 2 (node 1 (node 5 (leaf) (leaf)) (leaf)) (leaf)))\n\n")

ENTETE = "#lang racket\n"


def _amorce(prelude, signature, nom, param):
    return "%s%s;; %s\n(define (%s %s)\n  (error \"a completer\"))\n" % (
        ENTETE, prelude, signature, nom, param)


def _arbre(signature, nom):
    return _amorce(TYPE_ARBRE + ARBRES, signature, nom, "t")


def _option(signature, nom):
    return _amorce(PRELUDE_OPTION, signature, nom, "l")


ACTIVITES = {
 "F-arbre": [
  ("bintree-count-leaves",
   "Un arbre binaire sur les entiers : combien a-t-il de feuilles ? Ecrivez la "
   "definition en distinguant le cas de la feuille du cas du noeud interne.",
   "bintree-count-leaves : bintree -> entier",
   _arbre("bintree-count-leaves : bintree -> entier", "bintree-count-leaves"),
   [("(bintree-count-leaves t0)", "1"), ("(bintree-count-leaves t1)", "2"),
    ("(bintree-count-leaves t2)", "4")]),

  ("bintree-count-internal-nodes",
   "Le meme arbre : combien a-t-il de noeuds internes ?",
   "bintree-count-internal-nodes : bintree -> entier",
   _arbre("bintree-count-internal-nodes : bintree -> entier", "bintree-count-internal-nodes"),
   [("(bintree-count-internal-nodes t0)", "0"), ("(bintree-count-internal-nodes t1)", "1"),
    ("(bintree-count-internal-nodes t2)", "3")]),

  ("bintree-sum",
   "Un arbre binaire sur les entiers : donnez le total des entiers portes par "
   "ses noeuds internes.",
   "bintree-sum : bintree -> entier",
   _arbre("bintree-sum : bintree -> entier", "bintree-sum"),
   [("(bintree-sum t0)", "0"), ("(bintree-sum t1)", "3"), ("(bintree-sum t2)", "7")]),

  ("bintree-height",
   "Le meme arbre : donnez sa hauteur, c'est-a-dire la plus grande profondeur "
   "parmi tous ses noeuds. Une feuille est de hauteur zero.",
   "bintree-height : bintree -> entier",
   _arbre("bintree-height : bintree -> entier", "bintree-height"),
   [("(bintree-height t0)", "0"), ("(bintree-height t1)", "1"), ("(bintree-height t3)", "3")]),

  ("bintree-collect-values",
   "Le meme arbre : donnez la liste des entiers portes par ses noeuds internes, "
   "le sous-arbre gauche d'abord, puis le noeud, puis le sous-arbre droit.",
   "bintree-collect-values : bintree -> liste d'entiers",
   _arbre("bintree-collect-values : bintree -> liste d'entiers", "bintree-collect-values"),
   [("(bintree-collect-values t0)", "()"), ("(bintree-collect-values t1)", "(3)"),
    ("(bintree-collect-values t2)", "(1 2 4)")]),
 ],

 "F-option": [
  ("double-tete",
   "Une liste d'entiers eventuellement vide. En utilisant premier, donnez le "
   "double du premier entier, ou #f si la liste est vide. Distinguez les deux "
   "cas vous-meme.",
   "double-tete : liste d'entiers -> entier ou #f",
   _option("double-tete : liste d'entiers -> entier ou #f", "double-tete"),
   [("(double-tete '())", "#f"), ("(double-tete '(4 1))", "8")]),

  ("cent-sur-tete",
   "La meme liste. En utilisant premier puis division, donnez cent divise par le "
   "premier entier. La liste peut etre vide, et cet entier peut etre nul.",
   "cent-sur-tete : liste d'entiers -> entier ou #f",
   _option("cent-sur-tete : liste d'entiers -> entier ou #f", "cent-sur-tete"),
   [("(cent-sur-tete '())", "#f"), ("(cent-sur-tete '(0))", "#f"),
    ("(cent-sur-tete '(4))", "25")]),

  ("pipeline",
   "Une liste de chaines. En utilisant premiere, puis vers-entier, puis division, "
   "donnez cent divise par l'entier ecrit dans la premiere chaine. Chacune des "
   "trois etapes peut echouer.",
   "pipeline : liste de chaines -> entier ou #f",
   _option("pipeline : liste de chaines -> entier ou #f", "pipeline"),
   [("(pipeline '())", "#f"), ("(pipeline '(\"abc\"))", "#f"),
    ("(pipeline '(\"0\"))", "#f"), ("(pipeline '(\"5\"))", "20")]),

  ("longueur-premiere",
   "Une liste de chaines. En utilisant premiere, donnez la longueur de la "
   "premiere chaine.",
   "longueur-premiere : liste de chaines -> entier ou #f",
   _option("longueur-premiere : liste de chaines -> entier ou #f", "longueur-premiere"),
   [("(longueur-premiere '())", "#f"), ("(longueur-premiere '(\"xy\"))", "2")]),
 ],
}


REEMPLOIS = {
 "F-arbre": [
  ("bintree-count-even",
   "Un arbre binaire sur les entiers : combien de ses noeuds internes portent un "
   "entier pair ? Toute solution correcte est acceptee.",
   "bintree-count-even : bintree -> entier",
   _arbre("bintree-count-even : bintree -> entier", "bintree-count-even"),
   [("(bintree-count-even t0)", "0"), ("(bintree-count-even t1)", "0"),
    ("(bintree-count-even t2)", "2"), ("(bintree-count-even t3)", "1"),
    ("(bintree-count-even (node 6 (node 8 (leaf) (leaf)) (node 5 (leaf) (leaf))))", "2"),
    ("(bintree-count-even (node 3 (node -2 (leaf) (leaf)) (node 7 (leaf) (node 4 (leaf) (leaf)))))", "2")]),

  ("bintree-min",
   "Un arbre binaire sur les entiers : donnez le plus petit entier porte par un "
   "noeud interne, ou #f si l'arbre est une feuille. Vous pouvez employer ce que "
   "vous venez d'ecrire, ou reprendre la recursion a la main.",
   "bintree-min : bintree -> entier ou #f",
   _arbre("bintree-min : bintree -> entier ou #f", "bintree-min"),
   [("(bintree-min t0)", "#f"), ("(bintree-min t1)", "3"), ("(bintree-min t2)", "1"),
    ("(bintree-min (node 5 (node 7 (leaf) (leaf)) (node 3 (leaf) (leaf))))", "3"),
    ("(bintree-min (node 4 (node 6 (node -2 (leaf) (leaf)) (leaf)) (leaf)))", "-2"),
    ("(bintree-min (node 1 (node 5 (leaf) (leaf)) (node 8 (leaf) (leaf))))", "1")]),

  ("bintree-all-positive",
   "Le meme arbre : tous les entiers portes par ses noeuds internes sont-ils "
   "strictement positifs ?",
   "bintree-all-positive : bintree -> booleen",
   _arbre("bintree-all-positive : bintree -> booleen", "bintree-all-positive"),
   [("(bintree-all-positive t0)", "#t"), ("(bintree-all-positive t2)", "#t"),
    ("(bintree-all-positive t3)", "#t"),
    ("(bintree-all-positive (node -1 (leaf) (leaf)))", "#f"),
    ("(bintree-all-positive (node 2 (node 3 (leaf) (leaf)) (node -4 (leaf) (leaf))))", "#f"),
    ("(bintree-all-positive (node 2 (node 0 (leaf) (leaf)) (leaf)))", "#f")]),

  ("ubtree-count-bin",
   "On considere maintenant un arbre dont chaque noeud a un ou deux sous-arbres. "
   "Combien a-t-il de noeuds a deux sous-arbres ?",
   "ubtree-count-bin : ubtree -> entier",
   _amorce(TYPE_ARBRE_UB + "(define u0 (ub-leaf))\n(define u1 (bin (ub-leaf) (ub-leaf)))\n"
           "(define u2 (un (bin (un (ub-leaf)) (ub-leaf))))\n\n",
           "ubtree-count-bin : ubtree -> entier", "ubtree-count-bin", "t"),
   [("(ubtree-count-bin u0)", "0"), ("(ubtree-count-bin u1)", "1"),
    ("(ubtree-count-bin u2)", "1"),
    ("(ubtree-count-bin (bin (bin (ub-leaf) (ub-leaf)) (un (bin (ub-leaf) (ub-leaf)))))", "3"),
    ("(ubtree-count-bin (un (un (ub-leaf))))", "0")]),
 ],

 "F-option": [
  ("mille-sur-tete",
   "Une liste d'entiers : donnez mille divise par le premier. Vous pouvez employer "
   "ce que vous venez d'ecrire, ou reprendre les cas a la main.",
   "mille-sur-tete : liste d'entiers -> entier ou #f",
   _option("mille-sur-tete : liste d'entiers -> entier ou #f", "mille-sur-tete"),
   [("(mille-sur-tete '())", "#f"), ("(mille-sur-tete '(0))", "#f"),
    ("(mille-sur-tete '(8))", "125")]),

  ("lier",
   "On remplace l'absence de resultat par un resultat porteur d'un message : une "
   "valeur est soit (ok v), soit (erreur m). Ecrivez la fonction qui enchaine une "
   "etape sur ce resultat.",
   "lier : resultat (valeur -> resultat) -> resultat",
   ENTETE + ";; ne pas modifier les deux declarations ci-dessous\n"
   "(struct ok (v) #:transparent)\n(struct erreur (m) #:transparent)\n\n"
   "(define (montrer r) (if (ok? r) (ok-v r) (erreur-m r)))\n\n"
   ";; lier : resultat (valeur -> resultat) -> resultat\n"
   "(define (lier r f)\n  (error \"a completer\"))\n",
   [("(montrer (lier (ok 4) (lambda (x) (ok (* 2 x)))))", "8"),
    ("(montrer (lier (erreur \"vide\") (lambda (x) (ok (* 2 x)))))", "vide")]),
 ],
}
