"""Fournisseur de langage Racket pour FPTutor-Shell.

Engendre par l'atelier (creer_tuteur.py rkt rackettutor), puis complete. Les
cinq elements de l'interface, et les attributs facultatifs apparus avec OCaml.
L'analyse est deleguee a normalisation_rkt.py.
"""
import os
import re
import shutil

import normalisation_rkt as NR

# ------------------------------------------------------------ identification
name = "rkt"
extension = ".rkt"
titre = "RacketTutor"
langue_defaut = "fr"
compilateur = "Racket"


# ------------------------------------------------------------ execution
def interprete():
    """RACKET_BIN s'il est defini, sinon le PATH."""
    v = os.environ.get("RACKET_BIN")
    if v and os.path.exists(v):
        return v
    trouve = shutil.which("racket")
    if trouve:
        return trouve
    raise SystemExit("\nInterprete Racket introuvable : installez Racket 8.x ou "
                     "definissez RACKET_BIN.\n")


def command(chemin):
    return [interprete(), chemin]


def test_template(code, expressions):
    # Racket a un affichage generique : ~a rend toute valeur sur une ligne, et
    # la conversion n'a pas a figurer dans l'expression de test comme en OCaml.
    tete = "" if code.lstrip().startswith("#lang") else "#lang racket\n"
    lignes = "\n".join("(displayln (~a %s))" % e for e in expressions)
    return "%s%s\n\n%s\n" % (tete, code.rstrip(), lignes)


# ------------------------------------------------------------ analyse
ALIGNABLE_FORMS = ("constructors",)


def analyse(function_name, code):
    return NR.analyser(function_name, code)


def reemploi(function_name, code):
    """Facultatif : consulte par noyau.schema_employe s'il existe."""
    return NR.reemploi(function_name, code)


# ------------------------------------------------------------ categorisation
# Accesseur applique a la structure vide : « node-v: contract violation /
# expected: node? / given: (leaf) », ou « #<leaf> » pour une structure opaque,
# ou « '() » pour first et car. C'est la valeur donnee, une structure ou la liste
# vide, qui distingue ce cas d'une simple erreur de type (« given: 3 »).
ACCESSEUR = re.compile(r"contract violation\s+expected: [\w-]+\?\s+given: "
                       r"(?:\([a-z][\w-]*\)|#<[a-z][\w-]*>|'\(\))")

def categorise(message, compile_mais_faux=False):
    """Racket est type dynamiquement : les erreurs de forme apparaissent a
    l'execution des tests, non a la compilation. Un cas de base absent se
    manifeste de trois facons : un match sans clause, un accesseur applique a
    la structure vide, ou une valeur #<void> rendue par un cond sans issue."""
    if compile_mais_faux:
        return "wrong-result"
    m = message or ""
    if "no matching clause" in m or "given: #<void>" in m:
        return "missing-base-case"
    if ACCESSEUR.search(m):
        return "missing-base-case"          # accesseur sur une autre structure
    if "unbound identifier" in m:
        return "unknown-name"
    if "read-syntax" in m or "bad syntax" in m or "unexpected `)`" in m:
        return "syntax"
    if "contract violation" in m or "arity mismatch" in m \
            or "application: not a procedure" in m:
        return "incompatible-types"
    return "unclassified"


# ------------------------------------------------------------ references
def _references():
    try:
        from compiler_references import SOL, preambule_de
    except Exception:
        return {}
    familles = {
        "F-arbre": ["bintree-count-leaves", "bintree-count-internal-nodes",
                    "bintree-sum", "bintree-height", "bintree-collect-values"],
        "F-option": ["double-tete", "cent-sur-tete", "pipeline", "longueur-premiere"],
    }
    return {f: [(n, preambule_de(n) + "\n" + SOL[n]) for n in noms if n in SOL]
            for f, noms in familles.items()}


REFERENCES = _references()


# ------------------------------------------------------------ etayage
# Textes attaches aux categories communes, remplacant ceux du cadre, ecrits pour
# Haskell. Racket etant type dynamiquement, un cas de base absent ou une erreur
# de type se revelent a l'execution d'un test, non a la compilation.
AIDES_ERREUR = {
 "missing-base-case": [
   "L'execution a rencontre une forme d'entree que votre definition ne traite pas.",
   "Un arbre est soit une feuille, soit un noeud. Votre definition ne prevoit que "
   "le second cas, et un accesseur comme node-v a ete applique a une feuille.",
   "Il vous manque une clause pour (leaf? t). Sa valeur est celle qui ne change "
   "rien a l'operation que vous employez."],
 "incompatible-types": [
   "Racket a recu une valeur d'une autre nature que celle attendue. Le message "
   "nomme la fonction, ce qu'elle attendait (expected) et ce qu'elle a recu (given).",
   "Cherchez dans votre code l'appel de la fonction nommee et demandez-vous ce que "
   "vaut son argument a cet endroit, pour chacun des cas.",
   "Verifiez que chaque clause de votre cond rend une valeur de meme nature : un "
   "nombre dans un cas et une chaine dans l'autre suffisent a produire ce message."],
 "unknown-name": [
   "Un nom employe n'est pas defini.",
   "Verifiez l'orthographe, traits d'union compris : node-v et node-val sont deux "
   "noms differents.",
   "Les accesseurs d'une structure sont formes du nom de la structure et du nom "
   "du champ, tels qu'ils figurent dans la declaration struct de l'amorce."],
 "syntax": [
   "Le fichier ne se lit pas : le probleme est en amont du sens.",
   "Comptez les parentheses et les crochets de la definition signalee : chacun "
   "doit etre ferme, et dans l'ordre.",
   "Une definition a la forme (define (nom parametre) corps) ; chaque clause d'un "
   "cond a la forme [condition valeur]."],
}

LECTURES = {
 "missing-base-case": "L'execution a atteint un cas que votre definition ne traite pas.",
 "incompatible-types": "Une fonction a recu une valeur d'une autre nature que celle attendue.",
 "unknown-name": "Un nom employe dans votre code n'est defini nulle part.",
 "syntax": "Le fichier ne se lit pas : une parenthese manque ou est en trop.",
 "wrong-result": "Votre code s'execute. L'erreur n'est pas de forme mais de calcul.",
 "unclassified": "Racket a refuse votre definition.",
}


_INV = {"+": "+", "-": "-", "*": "*", "&&": "and", "||": "or", "@": "append",
        "::": "cons", "^": "string-append", "div": "quotient", "mod": "modulo"}


def _prefixe(forme):
    """Terme du vocabulaire commun, infixe, reecrit en syntaxe prefixe Racket."""
    toks = re.findall(r"\(|\)|[^\s()]+", forme)
    pos = 0

    def lire():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t != "(":
            return t
        items = []
        while toks[pos] != ")":
            items.append(lire())
        pos += 1
        return items

    def ecrire(e):
        if isinstance(e, str):
            return {"C1": "(node-v t)", "REC": "(f ...)", "NOTHING": "#f"}.get(e, e)
        if len(e) == 3 and isinstance(e[1], str) and e[1] in _INV:
            op, g, d = _INV[e[1]], e[0], e[2]
            # une somme gauche imbriquee se rend a plat, comme on l'ecrit
            args = [ecrire(d)]
            while isinstance(g, list) and len(g) == 3 and g[1] == e[1] and op in ("+", "*"):
                args.insert(0, ecrire(g[2])); g = g[0]
            return "(%s %s %s)" % (op, ecrire(g), " ".join(args))
        return "(%s)" % " ".join(ecrire(x) for x in e)
    try:
        return ecrire(lire())
    except (IndexError, TypeError):
        return forme


def squelette(forme):
    """Charpente du mode expose, en syntaxe Racket."""
    return "(define (f t)\n  (cond [(leaf? t) ?0]\n        [else %s]))" % _prefixe(forme)
