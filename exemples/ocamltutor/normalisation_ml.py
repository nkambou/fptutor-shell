"""Normalisation OCaml vers le vocabulaire commun de FPTutor-Shell.

Meme role que normalisation2 pour Haskell : l'analyse syntaxique est faite ici,
et language_ml.py s'y adosse. Le vocabulaire rendu est celui du cadre :
C1..Cn pour les champs du motif, REC pour l'appel recursif, COND pour une
decision, LIST pour une construction de liste, NOTHING pour l'absence.

Sous-ensemble couvert : let [rec] avec parametres et annotations, match ... with,
function, gardes when, conditionnelles, let ... in, application, operateurs
infixes et prefixes, constructeurs, listes, n-uplets, variables de type.
"""
import re

TOKEN = re.compile(r"""
    (?P<ws>\s+)
  | (?P<comment>\(\*.*?\*\))
  | (?P<arrow>->)
  | (?P<cons>::)
  | (?P<concat>\^|@)
  | (?P<num>\d+\.\d+|\d+)
  | (?P<str>"(?:[^"\\]|\\.)*")
  | (?P<char>'(?:\\.|[^'\\])')
  | (?P<tyvar>'[A-Za-z_][A-Za-z0-9_]*)
  | (?P<id>[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)*)
  | (?P<op><=|>=|<>|=|<|>|\+|-|\*|/|\|\||&&)
  | (?P<punct>[()\[\];,|:])
""", re.X | re.S)

KEYWORDS = {"let", "rec", "in", "match", "with", "function", "fun", "if", "then",
            "else", "true", "false", "and", "mod", "when", "type", "of"}


class ParseError(Exception):
    def __init__(self, token):
        super().__init__("construction non couverte : %r" % (token,))
        self.token = token


def lex(src: str):
    out, i = [], 0
    while i < len(src):
        m = TOKEN.match(src, i)
        if not m:
            raise ParseError(src[i:i + 12])
        i = m.end()
        kind = m.lastgroup
        if kind in ("ws", "comment"):
            continue
        out.append((kind, m.group()))
    out.append(("eof", ""))
    return out


# --------------------------------------------------------------- syntaxe
class P:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self, k=0):
        return self.t[min(self.i + k, len(self.t) - 1)]

    def val(self, k=0):
        return self.peek(k)[1]

    def eat(self, v=None):
        k, s = self.peek()
        if v is not None and s != v:
            raise ParseError(s or "fin de fichier")
        self.i += 1
        return s

    # définitions ------------------------------------------------------
    def parse_program(self):
        """Renvoie la liste des définitions de haut niveau."""
        defs = []
        while self.peek()[0] != "eof":
            if self.val() == "type":          # declaration de type : ignoree
                self.i += 1
                while self.peek()[0] != "eof" and self.val() != "let":
                    self.i += 1
                continue
            if self.val() == "open":          # ouverture de module : ignoree
                self.i += 1
                while self.peek()[0] != "eof" and self.val() != "let":
                    self.i += 1
                continue
            defs.append(self.parse_let(top=True))
        return defs

    def parse_let(self, top=False):
        self.eat("let")
        rec = False
        if self.val() == "rec":
            self.eat("rec"); rec = True
        name = self.eat()
        params = []
        while self.val() not in ("=", ":"):
            params.append(self.parse_param())
        if self.val() == ":":           # annotation du type de retour
            self.eat(":"); self.skip_type()
        self.eat("=")
        body = self.parse_expr()
        if not top and self.val() == "in":
            self.eat("in")
            rest = self.parse_expr()
            return ("letin", name, params, rec, body, rest)
        if self.val() == ";":
            self.eat(";")
            if self.val() == ";":
                self.eat(";")
        return ("def", name, params, rec, body)

    def parse_param(self):
        if self.val() == "(":
            self.eat("(")
            n = self.eat()
            if self.val() == ":":
                self.eat(":"); self.skip_type()
            self.eat(")")
            return n
        return self.eat()

    def skip_type(self):
        depth = 0
        while True:
            k, s = self.peek()
            if depth == 0 and (s in ("=", "in") or k == "eof"):
                return
            if s == "(":
                depth += 1
            elif s == ")":
                if depth == 0:
                    return
                depth -= 1
            self.i += 1

    # expressions ------------------------------------------------------
    def parse_expr(self):
        if self.val() == "match":
            return self.parse_match()
        if self.val() == "function":
            self.eat("function")
            return ("match", ("var", "__arg__"), self.parse_branches())
        if self.val() == "if":
            self.eat("if"); c = self.parse_expr()
            self.eat("then"); a = self.parse_expr()
            b = None
            if self.val() == "else":
                self.eat("else"); b = self.parse_expr()
            return ("if", c, a, b)
        if self.val() == "let":
            return self.parse_let()
        if self.val() == "fun":
            self.eat("fun")
            ps = []
            while self.val() != "->":
                ps.append(self.parse_param())
            self.eat("->")
            return ("fun", ps, self.parse_expr())
        return self.parse_binary(0)

    def parse_match(self):
        self.eat("match")
        scr = self.parse_binary(0)
        if self.val() == ",":                # scrutine en n-uplet sans parentheses
            parts = [scr]
            while self.val() == ",":
                self.eat(",")
                parts.append(self.parse_binary(0))
            scr = ("tuple", parts)
        self.eat("with")
        return ("match", scr, self.parse_branches())

    def parse_branches(self):
        branches = []
        if self.val() == "|":
            self.eat("|")
        while True:
            pat = self.parse_pattern()
            if self.val() == ",":            # motif en n-uplet sans parentheses
                parts = [pat]
                while self.val() == ",":
                    self.eat(",")
                    parts.append(self.parse_pattern())
                pat = ("ptuple", parts)
            guard = None
            if self.val() == "when":
                self.eat("when"); guard = self.parse_binary(0)
            self.eat("->")
            body = self.parse_expr()
            branches.append((pat, guard, body))
            if self.val() == "|":
                self.eat("|"); continue
            return branches

    def parse_pattern(self):
        parts = [self.parse_pattern_atom()]
        while self.val() == "::":
            self.eat("::"); parts.append(self.parse_pattern_atom())
        if len(parts) == 1:
            return parts[0]
        pat = parts[-1]
        for p in reversed(parts[:-1]):
            pat = ("pctor", "::", [p, pat])
        return pat

    def parse_pattern_atom(self):
        k, s = self.peek()
        if s == "(":
            self.eat("(")
            inner = [self.parse_pattern()]
            while self.val() == ",":
                self.eat(","); inner.append(self.parse_pattern())
            self.eat(")")
            return inner[0] if len(inner) == 1 else ("ptuple", inner)
        if s == "[":
            self.eat("[")
            if self.val() == "]":
                self.eat("]"); return ("pctor", "[]", [])
            items = [self.parse_pattern()]
            while self.val() == ";":
                self.eat(";"); items.append(self.parse_pattern())
            self.eat("]")
            return ("plist", items)
        if s == "_":
            self.eat(); return ("pwild",)
        if k == "num" or k == "str" or k == "char" or s in ("true", "false"):
            self.eat(); return ("pconst", s)
        if k == "id" and s[0].isupper():
            self.eat()
            if self.val() == "(" or (self.peek()[0] == "id" and self.val() != "->"):
                args = []
                if self.val() == "(":
                    self.eat("(")
                    args.append(self.parse_pattern())
                    while self.val() == ",":
                        self.eat(","); args.append(self.parse_pattern())
                    self.eat(")")
                else:
                    args.append(self.parse_pattern_atom())
                return ("pctor", s, args)
            return ("pctor", s, [])
        if k == "id":
            self.eat(); return ("pvar", s)
        raise ParseError(s)

    LEVELS = [("||",), ("&&",), ("=", "<>", "<", ">", "<=", ">="),
              ("::", "@", "^"), ("+", "-"), ("*", "/", "mod")]

    def parse_binary(self, level):
        if level >= len(self.LEVELS):
            return self.parse_app()
        left = self.parse_binary(level + 1)
        while self.val() in self.LEVELS[level]:
            op = self.eat()
            right = self.parse_binary(level + 1)
            left = ("op", op, [left, right])
        return left

    def parse_app(self):
        head = self.parse_atom()
        args = []
        while True:
            k, s = self.peek()
            if k == "id" and s in KEYWORDS and s not in ("true", "false"):
                break
            if s in ("(", "[") or k in ("num", "str", "char") or \
               s in ("true", "false") or (k == "id" and s not in KEYWORDS):
                args.append(self.parse_atom())
            else:
                break
        return head if not args else ("app", head, args)

    def parse_atom(self):
        k, s = self.peek()
        if s == "(":
            self.eat("(")
            if self.val() == ")":
                self.eat(")"); return ("const", "()")
            if self.peek()[0] == "op" and self.val(1) == ")":   # (+) préfixe
                op = self.eat(); self.eat(")")
                return ("var", "__op_%s__" % op)
            inner = [self.parse_expr()]
            while self.val() == ",":
                self.eat(","); inner.append(self.parse_expr())
            self.eat(")")
            return inner[0] if len(inner) == 1 else ("tuple", inner)
        if s == "[":
            self.eat("[")
            if self.val() == "]":
                self.eat("]"); return ("ctor", "[]", [])
            items = [self.parse_expr()]
            while self.val() == ";":
                self.eat(";"); items.append(self.parse_expr())
            self.eat("]")
            return ("list", items)
        if k in ("num", "str", "char") or s in ("true", "false"):
            self.eat(); return ("const", s)
        if k == "id":
            self.eat()
            if s[0].isupper() and s not in ("None",):
                return ("ctor", s, [])
            return ("var", s)
        raise ParseError(s)



# ------------------------------------------------- rendu en vocabulaire commun

INFIX = {"+", "-", "*", "/", "mod", "^", "@", "::", "=", "<>", "<", ">", "<=",
         ">=", "&&", "||"}
VIDES = ("NIL", "Nothing", "None", "Feuille", "[]", "F")


class Rendu:
    """Traduit une expression OCaml en terme du vocabulaire commun."""

    def __init__(self, fonction, champs):
        self.fonction = fonction
        self.champs = champs          # nom de variable -> "C1", "C2", ...

    def rendre(self, e):
        t = e[0]
        if t == "var":
            v = e[1]
            if v == self.fonction:
                return "REC"
            if v == "None":
                return "NOTHING"
            return self.champs.get(v, v)
        if t == "const":
            return "NOTHING" if e[1] == "None" else e[1]
        if t == "ctor":
            if e[1] in ("None",):
                return "NOTHING"
            if not e[2]:
                return "[]" if e[1] in ("[]", "NIL") else e[1]
            return "(%s %s)" % (e[1], " ".join(self.rendre(a) for a in e[2]))
        if t == "list":
            return "[]" if not e[1] else "(LIST %s)" % " ".join(
                self.rendre(a) for a in e[1])
        if t == "tuple":
            return "(TUPLE %s)" % " ".join(self.rendre(a) for a in e[1])
        if t == "op":
            g, d = self.rendre(e[2][0]), self.rendre(e[2][1])
            # commutativite limitee a + et *, comme les fournisseurs Haskell et
            # Python : appliquee a la concatenation elle creerait de fausses egalites
            if e[1] in ("+", "*") and g.strip() == "REC" and d.strip() != "REC":
                g, d = d, g
            return "(%s %s %s)" % (g, e[1], d)
        if t == "app":
            f = self.rendre(e[1])
            if f == "REC":
                return "REC"
            args = " ".join(self.rendre(a) for a in e[2])
            return "(%s %s)" % (f, args) if args else f
        if t == "if":
            b = self.rendre(e[3]) if e[3] else "()"
            return "COND (%s) (%s) (%s)" % (self.rendre(e[1]), self.rendre(e[2]), b)
        if t == "fun":
            return "(LAM %s)" % self.rendre(e[2])
        if t == "letin":
            return self.rendre(e[5])
        if t == "match":
            branches = sorted(self.rendre(b[2]) for b in e[2])
            return "(CASE %s)" % " ".join(branches)
        return "?"


def champs_de(pat):
    """Associe les variables liees par un motif aux etiquettes C1..Cn."""
    noms, ctor = [], None

    def walk(p):
        nonlocal ctor
        k = p[0]
        if k == "pvar":
            noms.append(p[1])
        elif k == "pwild":
            noms.append(None)
        elif k == "pctor":
            if ctor is None:
                ctor = p[1]
            for a in p[2]:
                walk(a)
        elif k in ("ptuple", "plist"):
            for a in p[1]:
                walk(a)
    walk(pat)
    if ctor is None and pat[0] == "pvar":
        ctor = None
    table = {}
    for i, n in enumerate(noms):
        if n is not None:
            table[n] = "C%d" % (i + 1)
    return ctor or ("[]" if pat == ("pctor", "[]", []) else None), table


def _serrer(s):
    return re.sub(r"\s+", " ", s or "").strip()


def analyser(nom, source):
    """Rend {'forme', 'equations', 'base', 'pas'}, comme l'analyseur Haskell."""
    try:
        defs = P(lex(source)).parse_program()
    except ParseError:
        return {"forme": "unanalysable", "equations": {}, "base": None, "pas": None}
    cible = next((d for d in defs if d[0] == "def" and d[1] == nom), None)
    if cible is None:
        cible = next((d for d in reversed(defs) if d[0] == "def"), None)
    if cible is None:
        return {"forme": "unanalysable", "equations": {}, "base": None, "pas": None}
    _, fname, params, rec, body = cible
    if re.search(r"\bfor\b|\bwhile\b", source):
        return {"forme": "iterative", "equations": {}, "base": None, "pas": None}
    if re.search(r"\bList\.(map|filter|fold_left|fold_right|for_all|exists|concat)\b"
                 r"|\bOption\.(bind|map|value)\b", source):
        return {"forme": "no-recursion", "equations": {}, "base": None, "pas": None}
    if body[0] != "match":
        r = Rendu(fname, {}).rendre(body)
        forme = "no-pattern" if "COND" in r or "REC" in r else "no-recursion"
        return {"forme": forme, "equations": {}, "base": None, "pas": _serrer(r)}
    equations = {}
    for pat, garde, corps in body[2]:
        ctor, champs = champs_de(pat)
        rendu = _serrer(Rendu(fname, champs).rendre(corps))
        equations[ctor or "ARG"] = rendu
    recursifs = [c for c, e in equations.items() if "REC" in e]
    vides = [c for c in equations if c in VIDES or not equations[c].count("C")]
    bases = [c for c in equations if c not in recursifs] if recursifs else vides
    pas = (equations[recursifs[0]] if recursifs
           else next((e for c, e in equations.items() if c not in bases), None))
    return {"forme": "constructors", "equations": equations,
            "base": equations[bases[0]] if bases else None, "pas": pas}
