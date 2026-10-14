"""Lignes de code : non vides, hors commentaires et hors docstrings."""
import ast, io, sys, tokenize, json

def lignes_code(src):
    doc = set()
    try:
        t = ast.parse(src)
        for n in ast.walk(t):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body \
               and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant) \
               and isinstance(n.body[0].value.value, str):
                doc.update(range(n.body[0].lineno, n.body[0].end_lineno + 1))
    except SyntaxError:
        pass
    n = 0
    for i, l in enumerate(src.splitlines(), 1):
        s = l.strip()
        if s and not s.startswith("#") and i not in doc:
            n += 1
    return n

def sections(path, reperes):
    """Compte par section, une section commencant a chaque repere (texte d'une ligne)."""
    src = open(path).read().splitlines()
    bornes = []
    for nom, rep in reperes:
        i = next(k for k, l in enumerate(src) if rep in l)
        bornes.append((i, nom))
    bornes.sort(); bornes.append((len(src), None))
    out = {}
    for (a, nom), (b, _) in zip(bornes, bornes[1:]):
        out[nom] = lignes_code("\n".join(src[a:b]))
    return out

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("%5d  %s" % (lignes_code(open(p).read()), p))
