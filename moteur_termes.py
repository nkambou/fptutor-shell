"""Moteur commun des termes : rendu dans le vocabulaire commun et selection du
cas de base et du pas.

Ce que les fournisseurs refaisaient chacun de leur cote. L'etude
docs/ETUDE_NORMALISATEUR.md montre que ces deux operations sont identiques d'une
instance a l'autre, a la table des operateurs pres. Elles sont donc ici, pilotees
par une declaration.

Le moteur travaille sur un arbre sous forme de listes et de chaines, celui que
rend le lecteur du langage : ["+", ["node-v", "t"], ["f", ["node-l", "t"]]].
Ce qui reste au fournisseur est ce qui ne se declare pas : obtenir cet arbre,
reperer la definition visee, et reconnaitre ce qui tient lieu de distinction de
cas dans son langage.

Declaration attendue, toutes les cles etant facultatives :

    OPERATEURS   nom prefixe -> symbole infixe du vocabulaire commun
    COMMUTATIFS  operateurs dont les operandes sont ordonnes
    ASSOC_DROITE operateurs rendus en cascade a droite, comme cons
    VIDES        constructeurs ou valeurs qui designent le cas vide
    ATOMES       atome du langage -> atome du vocabulaire commun
    CONDITION    formes qui tiennent lieu de conditionnelle
    LIAISON      formes dont seul le corps compte
    FONCTION     formes qui construisent une fonction anonyme
    CITATION     forme de citation, et nom de la construction de liste
"""
import re

DEFAUT = {
    "OPERATEURS": {}, "COMMUTATIFS": (), "ASSOC_DROITE": (),
    "VIDES": (), "ATOMES": {},
    "CONDITION": ("if", "cond"), "LIAISON": ("let", "let*", "letrec"),
    "FONCTION": ("lambda",), "CITATION": ("quote",), "LISTE": ("list",),
}


def serrer(s):
    return re.sub(r"\s+", " ", s or "").strip()


class Moteur:
    def __init__(self, declaration=None):
        self.d = dict(DEFAUT, **(declaration or {}))

    # ------------------------------------------------------------- rendu
    def rendre(self, e, fonction, champs=None, accesseurs=None):
        """Rend le terme canonique d'une expression.

        fonction   : le nom dont l'appel devient REC
        champs     : variable liee -> etiquette ("x" -> "C1")
        accesseurs : nom d'accesseur -> etiquette ("node-l" -> "C2")
        """
        champs = champs or {}
        accesseurs = accesseurs or {}
        d = self.d

        def rendre(e):
            if isinstance(e, str):
                if e == fonction:
                    return "REC"
                if e in d["ATOMES"]:
                    return d["ATOMES"][e]
                return champs.get(e, e)
            if not e:
                return "()"
            tete = e[0]
            if isinstance(tete, list):
                return "(%s)" % " ".join(rendre(x) for x in e)
            if tete in d["CITATION"]:
                q = e[1]
                if q == []:
                    return "[]"
                if isinstance(q, list):
                    return "(LIST %s)" % " ".join(rendre(x) for x in q)
                return q
            if tete == fonction:
                return "REC"
            if tete in accesseurs and len(e) == 2:
                return accesseurs[tete]
            if tete in d["CONDITION"] and tete == "if" and len(e) == 4:
                return "COND (%s) (%s) (%s)" % tuple(rendre(x) for x in e[1:])
            if tete in d["CONDITION"]:
                clauses = ["(%s) (%s)" % (rendre(c[0]) if c[0] != "else" else "else",
                                          rendre(c[-1])) for c in e[1:]]
                return "COND %s" % " ".join(clauses)
            if tete in d["FONCTION"]:
                return "(LAM %s)" % rendre(e[-1])
            if tete in d["LIAISON"]:
                return rendre(e[-1])
            if tete in d["LISTE"]:
                return "[]" if len(e) == 1 else "(LIST %s)" % " ".join(
                    rendre(x) for x in e[1:])
            if tete in d["OPERATEURS"] and len(e) >= 3:
                return self._infixe(tete, [rendre(x) for x in e[1:]])
            return "(%s)" % " ".join(rendre(x) for x in e)

        return serrer(rendre(e))

    def _infixe(self, tete, args):
        op = self.d["OPERATEURS"][tete]
        if tete in self.d["COMMUTATIFS"]:
            # somme ou produit plat : operandes non recursifs tries, puis les REC
            args = sorted((a for a in args if a != "REC"),
                          key=lambda a: (a.startswith("("), a)) + \
                   [a for a in args if a == "REC"]
        if tete in self.d["ASSOC_DROITE"]:
            r = args[-1]
            for a in reversed(args[:-1]):
                r = "(%s %s %s)" % (a, op, r)
            return r
        r = args[0]
        for a in args[1:]:
            r = "(%s %s %s)" % (r, op, a)
        return r

    # --------------------------------------------------- base et pas
    def selection(self, equations):
        """Des equations par constructeur vers {forme, equations, base, pas}.

        Meme regle dans toutes les instances : les equations ou REC apparait sont
        les cas recursifs, les bases sont les autres, le pas est la premiere
        equation recursive. Sans recursion, les bases sont les cas vides declares.
        """
        vides = tuple(self.d["VIDES"]) + ("NOTHING", "[]")
        recursifs = [c for c, e in equations.items() if "REC" in e]
        cas_vides = [c for c in equations if c in vides or equations[c] in vides]
        bases = [c for c in equations if c not in recursifs] if recursifs else cas_vides
        pas = (equations[recursifs[0]] if recursifs
               else next((e for c, e in equations.items() if c not in bases), None))
        return {"forme": "constructors", "equations": equations,
                "base": equations[bases[0]] if bases else None, "pas": pas}
