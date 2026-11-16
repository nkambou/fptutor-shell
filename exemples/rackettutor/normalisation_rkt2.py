"""Normalisation Racket, seconde version : moteur commun et vidage par Racket.

Experience de l'etude docs/ETUDE_NORMALISATEUR.md. Deux changements par rapport a
normalisation_rkt.py, et aucun autre :

  - l'arbre n'est plus lu par un lecteur de s-expressions ecrit en Python ;
    vidage.rkt demande a Racket de lire sa propre syntaxe et de rendre l'arbre
    en JSON ;
  - le rendu et la selection du cas de base viennent du moteur commun de la
    coquille, pilotes par la declaration ci-dessous.

Ce qui reste ici est ce qui ne se declare pas : reperer les structures et les
definitions, et reconnaitre ce qui tient lieu de distinction de cas en Racket.
"""
import json
import os
import subprocess
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = ICI
while not os.path.exists(os.path.join(RACINE, "moteur_termes.py")) and RACINE != "/":
    RACINE = os.path.dirname(RACINE)
sys.path.insert(0, RACINE)
from moteur_termes import Moteur, serrer

DECLARATION = {
    "OPERATEURS": {"+": "+", "-": "-", "*": "*", "/": "/", "=": "=", "<": "<",
                   ">": ">", "<=": "<=", ">=": ">=", "and": "&&", "or": "||",
                   "append": "@", "cons": "::", "string-append": "^",
                   "quotient": "div", "modulo": "mod", "remainder": "mod"},
    "COMMUTATIFS": ("+", "*"),
    "ASSOC_DROITE": ("cons",),
    "VIDES": ("#f", "[]", "empty", "null", "leaf"),
    "ATOMES": {"#f": "NOTHING", "empty": "[]", "null": "[]"},
    "CONDITION": ("if", "cond"),
    "LIAISON": ("let", "let*", "letrec"),
    "FONCTION": ("lambda", "λ"),
    "CITATION": ("quote",),
    "LISTE": ("list",),
}
M = Moteur(DECLARATION)

ITERATIFS = {"for", "for/list", "for/sum", "for/and", "for/or", "for/fold",
             "for/product", "for*", "for*/list", "do", "while"}
BIBLIOTHEQUE = {"foldl", "foldr", "map", "filter", "andmap", "ormap", "apply",
                "for-each", "filter-map", "append-map", "count", "argmin", "argmax"}
PREDICATS_LISTE = {"empty?": "[]", "null?": "[]", "pair?": "cons", "cons?": "cons"}


# ------------------------------------------------------------------ lecture
class ParseError(Exception):
    pass


_CACHE = {}


def lire(source):
    """Rend les formes de premier niveau, lues par Racket lui-meme.

    Le vidage coute un lancement de Racket, de l'ordre du tiers de seconde. Une
    soumission ne change plus une fois deposee, et l'alignement relit le meme
    corpus a chaque decision : le resultat est donc garde en memoire, et le cout
    n'est paye qu'une fois par soumission, a cote du temps de compilation.
    """
    if source in _CACHE:
        return _CACHE[source]
    racket = os.environ.get("RACKET_BIN") or "racket"
    with tempfile.NamedTemporaryFile("w", suffix=".rkt", delete=False) as f:
        f.write(source)
        chemin = f.name
    try:
        r = subprocess.run([racket, os.path.join(ICI, "vidage.rkt"), chemin],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            raise ParseError(r.stderr.strip()[:200])
        formes = json.loads(r.stdout)
        _CACHE[source] = formes
        return formes
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ParseError(str(e))
    finally:
        os.unlink(chemin)


# ------------------------------------------------------------------ programme
def programme(formes):
    structs, defs = {}, {}
    for f in formes:
        if not isinstance(f, list) or not f:
            continue
        tete = f[0]
        if tete in ("struct", "define-struct") and len(f) >= 3 and isinstance(f[2], list):
            nom = f[1] if isinstance(f[1], str) else f[1][0]
            structs[nom] = [c if isinstance(c, str) else c[0] for c in f[2]]
        elif tete == "define/contract" and len(f) >= 4 and isinstance(f[1], list):
            defs[f[1][0]] = (f[1][1:], f[-1])
        elif tete == "define" and len(f) >= 3:
            if isinstance(f[1], list):
                defs[f[1][0]] = (f[1][1:], f[-1])
            elif isinstance(f[2], list) and f[2] and f[2][0] in ("lambda", "λ"):
                defs[f[1]] = (f[2][1], f[2][-1])
            else:
                defs[f[1]] = ([], f[2])
    return structs, defs


def accesseurs(structs):
    acc, pred = {"first": "C1", "car": "C1", "rest": "C2", "cdr": "C2"}, {}
    for s, champs in structs.items():
        pred[s + "?"] = s
        for i, c in enumerate(champs):
            acc["%s-%s" % (s, c)] = "C%d" % (i + 1)
    return acc, pred


def contient(e, noms):
    if isinstance(e, str):
        return e in noms
    return any(contient(x, noms) for x in e)


# ------------------------------------------------------------------ cas
def champs_motif(motif, structs):
    if motif == "#f":
        return "#f", {}
    if isinstance(motif, str):
        if motif in ("_", "else"):
            return "ELSE", {}
        if motif in ("empty", "null"):
            return "[]", {}
        return "SOME", {motif: "C1"}
    if motif and motif[0] == "quote" and motif[1] == []:
        return "[]", {}
    if motif and motif[0] in ("cons", "list*") and len(motif) == 3:
        return "cons", {v: "C%d" % (i + 1) for i, v in enumerate(motif[1:])
                        if isinstance(v, str) and v != "_"}
    if motif and motif[0] in structs:
        return motif[0], {v: "C%d" % (i + 1) for i, v in enumerate(motif[1:])
                          if isinstance(v, str) and v != "_"}
    return "?", {}


def test_de(cond, pred, var_opt):
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
    if not isinstance(corps, list) or not corps:
        return None
    tete = corps[0]
    if tete in ("let", "let*") and len(corps) == 3 and isinstance(corps[1], list) \
            and len(corps[1]) == 1 and isinstance(corps[1][0], list):
        return cas(corps[2], structs, pred, corps[1][0][0])
    if tete == "match" and len(corps) >= 3:
        return [(lambda ctor_champs: (ctor_champs[0], ctor_champs[1], c[-1]))(
            champs_motif(c[0], structs)) for c in corps[2:]]
    if tete == "if" and len(corps) == 4:
        k = test_de(corps[1], pred, var_opt)
        if k is None:
            return None
        autre = {"#f": "SOME", "SOME": "#f"}.get(k, "ELSE")
        ch = {var_opt: "C1"} if var_opt else {}
        return [(k, ch if k == "SOME" else {}, corps[2]),
                (autre, ch if autre == "SOME" else {}, corps[3])]
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
            out.append((k, {var_opt: "C1"} if (var_opt and k == "SOME") else {},
                        clause[-1]))
        return out
    if tete == "and" and len(corps) == 3 and var_opt and corps[1] == var_opt:
        return [("#f", {}, "#f"), ("SOME", {var_opt: "C1"}, corps[2])]
    return None


# ------------------------------------------------------------------ analyse
def analyser(nom, source):
    vide = {"equations": {}, "base": None, "pas": None}
    try:
        formes = lire(source)
    except ParseError:
        return dict(vide, forme="unanalysable")
    structs, defs = programme(formes)
    if nom not in defs:
        return dict(vide, forme="unanalysable")
    _params, corps = defs[nom]
    acc, pred = accesseurs(structs)
    if contient(corps, ITERATIFS) or (isinstance(corps, list) and len(corps) > 2
                                      and corps[0] == "let" and isinstance(corps[1], str)):
        return dict(vide, forme="iterative")
    if contient(corps, BIBLIOTHEQUE):
        return dict(vide, forme="no-recursion")
    branches = cas(corps, structs, pred)
    if branches is None:
        r = M.rendre(corps, nom, {}, acc)
        forme = "no-pattern" if ("REC" in r and ("COND" in r or "&&" in r)) else "no-recursion"
        return {"forme": forme, "equations": {}, "base": None, "pas": r}
    equations = {}
    for ctor, champs, expr in branches:
        sous = cas(expr, structs, pred)
        if sous:
            equations[ctor] = "(CASE %s)" % " ".join(sorted(
                M.rendre(e, nom, dict(champs, **c), acc) for _k, c, e in sous))
        else:
            equations[ctor] = M.rendre(expr, nom, champs, acc)
    return M.selection(equations)
