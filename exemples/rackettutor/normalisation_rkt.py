"""Normalisation Racket vers le vocabulaire commun de FPTutor-Shell.

Meme role que normalisation_ml pour OCaml. Deux traits de Racket commandent la
conception, et n'existaient pas dans les instances precedentes.

Il n'y a pas de type somme. Un arbre est une famille de structures, distinguees
par leurs predicats (leaf?, node?) et lues par leurs accesseurs (node-l). Le
normalisateur lit donc les declarations struct de la soumission et projette
chaque accesseur sur l'etiquette de son champ : (node-v t), (node-l t) et
(node-r t) deviennent C1, C2, C3, exactement comme les variables liees par le
motif (node v l r) de racket/match. Deux ecritures, par predicats ou par
filtrage, rendent ainsi le meme terme.

L'absence s'ecrit #f et non None. L'enchainement sur l'absence prend quatre
formes idiomatiques, (if x A #f), (if (not x) #f A), (and x A) et
(match x [#f #f] [v A]), qui doivent rendre le meme terme.

La syntaxe prefixe n-aire donne en outre la commutativite de + et * sans regle
d'appoint : les operandes d'une somme plate sont ordonnes, les appels recursifs
en dernier.
"""
import re

# ------------------------------------------------------------------ lecture
TOKEN = re.compile(r"""
    (?P<ws>\s+)
  | (?P<lcomment>;[^\n]*)
  | (?P<bcomment>\#\|.*?\|\#)
  | (?P<datumcomment>\#;)
  | (?P<lang>\#lang[^\n]*)
  | (?P<open>[(\[{])
  | (?P<close>[)\]}])
  | (?P<quote>'|`|,@|,)
  | (?P<str>"(?:[^"\\]|\\.)*")
  | (?P<char>\#\\(?:[a-z]+|.))
  | (?P<bool>\#t(?:rue)?\b|\#f(?:alse)?\b)
  | (?P<atom>[^\s()\[\]{}"';`,]+)
""", re.X | re.S)


class ParseError(Exception):
    pass


def lire(src):
    """Rend la liste des formes de premier niveau, en listes Python."""
    toks = []
    for m in TOKEN.finditer(src):
        k = m.lastgroup
        if k in ("ws", "lcomment", "bcomment", "lang"):
            continue
        toks.append((k, m.group()))
    if "".join(m.group() for m in TOKEN.finditer(src)) != src:
        raise ParseError("caractere non reconnu")
    pos = 0

    def forme():
        nonlocal pos
        if pos >= len(toks):
            raise ParseError("fin de fichier")
        k, s = toks[pos]
        pos += 1
        if k == "datumcomment":
            forme()
            return forme()
        if k == "open":
            items = []
            while True:
                if pos >= len(toks):
                    raise ParseError("parenthese non fermee")
                if toks[pos][0] == "close":
                    pos += 1
                    return items
                if toks[pos][0] == "datumcomment":
                    pos += 1
                    forme()
                    continue
                items.append(forme())
        if k == "close":
            raise ParseError("parenthese en trop")
        if k == "quote":
            return ["quote", forme()]
        if k == "bool":
            return "#f" if s.startswith("#f") else "#t"
        return s

    out = []
    while pos < len(toks):
        if toks[pos][0] == "datumcomment":
            pos += 1
            forme()
            continue
        out.append(forme())
    return out


# ------------------------------------------------------------------ programme
ITERATIFS = {"for", "for/list", "for/sum", "for/and", "for/or", "for/fold",
             "for/product", "for*", "for*/list", "do", "while"}
BIBLIOTHEQUE = {"foldl", "foldr", "map", "filter", "andmap", "ormap", "apply",
                "for-each", "filter-map", "append-map", "count", "argmin", "argmax"}
OPS_COMMUTATIFS = {"+": "+", "*": "*"}
OPS_INFIXES = {"+": "+", "-": "-", "*": "*", "/": "/", "=": "=", "<": "<",
               ">": ">", "<=": "<=", ">=": ">=", "and": "&&", "or": "||",
               "append": "@", "cons": "::", "string-append": "^",
               "quotient": "div", "modulo": "mod", "remainder": "mod"}
VIDES = ("#f", "NOTHING", "[]", "empty", "null", "leaf")
PREDICATS_LISTE = {"empty?": "[]", "null?": "[]", "pair?": "cons", "cons?": "cons"}


def programme(formes):
    """Rend (structures, definitions). structures : nom -> champs ;
    definitions : nom -> (parametres, corps)."""
    structs, defs = {}, {}
    for f in formes:
        if not isinstance(f, list) or not f:
            continue
        tete = f[0]
        if tete in ("struct", "define-struct") and len(f) >= 3 and isinstance(f[2], list):
            nom = f[1] if isinstance(f[1], str) else f[1][0]
            structs[nom] = [c if isinstance(c, str) else c[0] for c in f[2]]
        elif tete == "define/contract" and len(f) >= 4 and isinstance(f[1], list):
            defs[f[1][0]] = (f[1][1:], f[-1])            # le contrat est ignore
        elif tete == "define" and len(f) >= 3:
            if isinstance(f[1], list):                    # (define (f x) corps)
                defs[f[1][0]] = (f[1][1:], f[-1])
            elif isinstance(f[2], list) and f[2] and f[2][0] in ("lambda", "λ"):
                defs[f[1]] = (f[2][1], f[2][-1])
            else:
                defs[f[1]] = ([], f[2])
    return structs, defs


def accesseurs(structs):
    """node-l -> (node, 2) ; node? -> node."""
    acc, pred = {}, {}
    for s, champs in structs.items():
        pred[s + "?"] = s
        for i, c in enumerate(champs):
            acc["%s-%s" % (s, c)] = (s, i + 1)
    return acc, pred


def contient(e, noms):
    if isinstance(e, str):
        return e in noms
    return any(contient(x, noms) for x in e)


# ------------------------------------------------------------------ rendu
class Rendu:
    def __init__(self, fonction, champs, acc):
        self.fonction = fonction
        self.champs = champs        # variable liee -> "C1"...
        self.acc = acc

    def rendre(self, e):
        if isinstance(e, str):
            if e == self.fonction:
                return "REC"
            if e == "#f":
                return "NOTHING"
            if e in ("empty", "null"):
                return "[]"
            return self.champs.get(e, e)
        if not e:
            return "()"
        if e[0] == "quote":
            q = e[1]
            if q == [] :
                return "[]"
            if isinstance(q, list):
                return "(LIST %s)" % " ".join(self.rendre(x) for x in q)
            return q
        tete = e[0]
        if isinstance(tete, list):
            return "(%s)" % " ".join(self.rendre(x) for x in e)
        if tete == self.fonction:
            return "REC"
        if tete in self.acc and len(e) == 2:            # (node-l t) -> C2
            return "C%d" % self.acc[tete][1]
        if tete in ("first", "car") and len(e) == 2:
            return "C1"
        if tete in ("rest", "cdr") and len(e) == 2:
            return "C2"
        if tete == "if" and len(e) == 4:
            return "COND (%s) (%s) (%s)" % tuple(self.rendre(x) for x in e[1:])
        if tete == "cond":
            clauses = []
            for c in e[1:]:
                clauses.append("(%s) (%s)" % (self.rendre(c[0]) if c[0] != "else" else "else",
                                              self.rendre(c[-1])))
            return "COND %s" % " ".join(clauses)
        if tete in ("lambda", "λ"):
            return "(LAM %s)" % self.rendre(e[-1])
        if tete in ("let", "let*", "letrec"):
            return self.rendre(e[-1])
        if tete == "not" and len(e) == 2:
            return "(not %s)" % self.rendre(e[1])
        if tete == "list":
            return "[]" if len(e) == 1 else "(LIST %s)" % " ".join(self.rendre(x) for x in e[1:])
        if tete in OPS_INFIXES and len(e) >= 3:
            op = OPS_INFIXES[tete]
            args = [self.rendre(x) for x in e[1:]]
            if tete in OPS_COMMUTATIFS:
                # somme ou produit plat : operandes non recursifs tries, puis
                # les appels recursifs ; sur, + et * etant commutatifs
                args = sorted((a for a in args if a != "REC"),
                              key=lambda a: (a.startswith("("), a)) + \
                       [a for a in args if a == "REC"]
            if tete == "cons":                           # associatif a droite
                r = args[-1]
                for a in reversed(args[:-1]):
                    r = "(%s :: %s)" % (a, r)
                return r
            r = args[0]
            for a in args[1:]:
                r = "(%s %s %s)" % (r, op, a)
            return r
        return "(%s)" % " ".join(self.rendre(x) for x in e)


# ------------------------------------------------------------------ cas
def champs_motif(motif, structs):
    """Motif racket/match -> (constructeur, table des champs)."""
    if motif == "#f":
        return "#f", {}
    if isinstance(motif, str):
        if motif in ("_", "else"):
            return "ELSE", {}
        if motif in ("empty", "null"):
            return "[]", {}
        return "SOME", {motif: "C1"}                      # variable : valeur presente
    if motif and motif[0] == "quote" and motif[1] == []:
        return "[]", {}
    if motif and motif[0] in ("cons", "list*") and len(motif) == 3:
        t = {}
        for i, v in enumerate(motif[1:]):
            if isinstance(v, str) and v != "_":
                t[v] = "C%d" % (i + 1)
        return "cons", t
    if motif and motif[0] in structs:
        t = {}
        for i, v in enumerate(motif[1:]):
            if isinstance(v, str) and v != "_":
                t[v] = "C%d" % (i + 1)
        return motif[0], t
    return "?", {}


def test_de(cond, pred, var_opt):
    """Rend le constructeur que la condition selectionne, ou None.
    (leaf? t) -> leaf ; (empty? l) -> [] ; x -> SOME ; (not x) -> #f."""
    if isinstance(cond, list) and len(cond) == 2 and isinstance(cond[0], str):
        if cond[0] in pred:
            return pred[cond[0]]
        if cond[0] in PREDICATS_LISTE:
            return PREDICATS_LISTE[cond[0]]
        if cond[0] in ("not", "false?") and var_opt and cond[1] == var_opt:
            return "#f"
    if var_opt and cond == var_opt:
        return "SOME"
    return None


def cas(corps, structs, pred, var_opt=None):
    """Reconnait une distinction de cas. Rend [(constructeur, champs, corps)]
    ou None. var_opt est la variable liee par un let dont on teste l'absence."""
    if not isinstance(corps, list) or not corps:
        return None
    tete = corps[0]
    # (let ([x (g l)]) ...) : variable candidate pour l'absence
    if tete in ("let", "let*") and len(corps) == 3 and isinstance(corps[1], list) \
            and len(corps[1]) == 1 and isinstance(corps[1][0], list):
        v = corps[1][0][0]
        return cas(corps[2], structs, pred, v)
    if tete == "match" and len(corps) >= 3:
        out = []
        for clause in corps[2:]:
            ctor, champs = champs_motif(clause[0], structs)
            out.append((ctor, champs, clause[-1]))
        return out
    if tete == "if" and len(corps) == 4:
        k = test_de(corps[1], pred, var_opt)
        if k is None:
            return None
        autre = {"#f": "SOME", "SOME": "#f"}.get(k, "ELSE")
        champs = {var_opt: "C1"} if var_opt else {}
        return [(k, champs if k == "SOME" else {}, corps[2]),
                (autre, champs if autre == "SOME" else {}, corps[3])]
    if tete == "cond":
        out = []
        for clause in corps[1:]:
            if clause[0] == "else":
                k = "ELSE"
                if var_opt and out and out[-1][0] in ("#f", "SOME"):
                    k = "SOME" if out[-1][0] == "#f" else "#f"
            else:
                k = test_de(clause[0], pred, var_opt)
                if k is None:
                    return None
            champs = {var_opt: "C1"} if (var_opt and k == "SOME") else {}
            out.append((k, champs, clause[-1]))
        return out
    if tete == "and" and len(corps) == 3 and var_opt and corps[1] == var_opt:
        return [("#f", {}, "#f"), ("SOME", {var_opt: "C1"}, corps[2])]
    return None


def _serrer(s):
    return re.sub(r"\s+", " ", s or "").strip()


def analyser(nom, source):
    """Rend {'forme', 'equations', 'base', 'pas'}, comme les autres analyseurs."""
    vide = {"equations": {}, "base": None, "pas": None}
    try:
        formes = lire(source)
    except ParseError:
        return dict(vide, forme="unanalysable")
    structs, defs = programme(formes)
    if nom not in defs:
        return dict(vide, forme="unanalysable")
    params, corps = defs[nom]
    acc, pred = accesseurs(structs)
    if contient(corps, ITERATIFS) or (isinstance(corps, list) and len(corps) > 2
                                      and corps[0] == "let" and isinstance(corps[1], str)):
        return dict(vide, forme="iterative")               # boucle ou let nomme
    if contient(corps, BIBLIOTHEQUE):
        return dict(vide, forme="no-recursion")
    branches = cas(corps, structs, pred)
    if branches is None:
        r = Rendu(nom, {}, acc).rendre(corps)
        forme = "no-pattern" if ("REC" in r and ("COND" in r or "&&" in r)) else "no-recursion"
        return {"forme": forme, "equations": {}, "base": None, "pas": _serrer(r)}
    equations = {}
    for ctor, champs, expr in branches:
        # une distinction imbriquee se rend comme un CASE, a la maniere d'OCaml
        sous = cas(expr, structs, pred)
        if sous is None and isinstance(expr, list) and expr and expr[0] in ("let", "let*"):
            sous = cas(expr, structs, pred)
        if sous:
            rendus = sorted(_serrer(Rendu(nom, dict(champs, **c), acc).rendre(e))
                            for _k, c, e in sous)
            equations[ctor] = "(CASE %s)" % " ".join(rendus)
        else:
            equations[ctor] = _serrer(Rendu(nom, champs, acc).rendre(expr))
    recursifs = [c for c, e in equations.items() if "REC" in e]
    vides = [c for c in equations if c in VIDES or equations[c] in ("NOTHING", "[]")]
    bases = [c for c in equations if c not in recursifs] if recursifs else vides
    pas = (equations[recursifs[0]] if recursifs
           else next((e for c, e in equations.items() if c not in bases), None))
    return {"forme": "constructors", "equations": equations,
            "base": equations[bases[0]] if bases else None, "pas": pas}


# ------------------------------------------------------------------ reemploi
PRIMITIVES_FONCTIONNELLES = {"+", "*", "-", "max", "min", "and", "or", "append",
                             "cons", "list", "even?", "odd?", "positive?", "add1"}


def _appels(e, nom):
    """La forme e contient-elle un appel a nom ?"""
    if isinstance(e, list) and e:
        if e[0] == nom:
            return True
        return any(_appels(x, nom) for x in e)
    return False


def reemploi(nom, source):
    """Une solution compte comme reemploi si la fonction demandee ne s'appelle
    pas elle-meme, et si elle passe une fonction en argument a une abstraction :
    une lambda, une primitive nommee (+, max...), ou une fonction definie dans la
    soumission. C'est la regle de l'instance OCaml, portee en Racket. Une
    enveloppe (define (f t) (aux t)) n'y satisfait pas ; une forme non
    analysable n'est jamais un reemploi."""
    try:
        structs, defs = programme(lire(source))
    except ParseError:
        return False
    if nom not in defs:
        return False
    _params, corps = defs[nom]
    if _appels(corps, nom):
        return False

    def fonctionnel(a):
        if isinstance(a, list) and a and a[0] in ("lambda", "λ"):
            return True
        return isinstance(a, str) and (a in defs or a in PRIMITIVES_FONCTIONNELLES)

    def cherche(e):
        if not isinstance(e, list) or not e:
            return False
        if isinstance(e[0], str) and e[0] not in ("lambda", "λ", "define", "let"):
            if any(fonctionnel(a) for a in e[1:]):
                return True
        return any(cherche(x) for x in e)
    return cherche(corps)
