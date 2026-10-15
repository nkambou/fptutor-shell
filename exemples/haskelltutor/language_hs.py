"""Fournisseur de langage Haskell pour FPTutor-Shell.

Quatrieme instanciation, et la seule qui revienne au langage dont la coquille
est issue. L'analyse n'est donc pas a ecrire : normalisation.py, herite de
HaskellTutor, lit deja une definition Haskell sur une liste et en rend la forme
canonique. Ce fournisseur l'enveloppe et traduit son vocabulaire vers celui que
l'interface des fournisseurs attend.

Deux traductions seulement :

    structurel-droit, structurel-garde  ->  constructors
    accumulateur, non-structurel        ->  formes non alignables
    ELEM                                ->  C1

REST et REC sont deja ceux du vocabulaire commun.
"""
import os
import re
import shutil
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)
import normalisation as NH

# ------------------------------------------------------------ identification
name = "hs"
extension = ".hs"
titre = "HaskellTutor"
langue_defaut = "fr"
compilateur = "GHC"


# ------------------------------------------------------------ execution
def interprete():
    v = os.environ.get("GHC_BIN")
    if v and os.path.exists(v):
        return v
    return shutil.which("runghc") or shutil.which("runhaskell")


ABSENT = ("Interprete Haskell introuvable : le serveur tourne, mais aucune "
          "soumission ne peut etre compilee. Installez GHC, ou lancez le "
          "serveur avec GHC_BIN.")


def command(chemin):
    ghc = interprete()
    if ghc is None:
        return [sys.executable, "-c",
                "import sys; sys.stderr.write(%r); sys.exit(1)" % (ABSENT + "\n")]
    return [ghc, chemin]


def test_template(code, expressions):
    lignes = "\n".join("  print (%s)" % e for e in expressions)
    return "%s\n\nmain :: IO ()\nmain = do\n%s\n" % (code.rstrip(), lignes)


# ------------------------------------------------------------ analyse
ALIGNABLE_FORMS = ("constructors",)

_FORMES = {"structurel-droit": "constructors", "structurel-garde": "constructors",
           "accumulateur": "no-recursion", "non-structurel": "no-pattern"}


_LIAISON = re.compile(r"^\s*(\w[\w']*)\s*=\s*(.+?)\s*$")


def _inliner_where(source):
    """Remplace une liaison locale simple par sa valeur, avant l'analyse.

    L'analyseur herite ecarte la clause where sans substituer ce qu'elle lie :
    « somme (x:xs) = x + reste where reste = somme xs » rend « C1 + reste » au
    lieu de « C1 + REC », et la solution compte alors comme une variation du
    schema. La substitution est faite ici, dans le fournisseur, pour ne pas
    toucher a normalisation.py, dont les ablations de l'article dependent.

    Seules les liaisons d'une ligne, sans parametre, sont substituees ; une
    fonction locale a parametres reste traitee comme avant.
    """
    bloc = re.split(r"\bwhere\b", source)
    if len(bloc) < 2:
        return source
    corps, reste, liaisons = bloc[0], bloc[1], {}
    for l in reste.splitlines():
        m = _LIAISON.match(l)
        if m and " " not in m.group(1):
            liaisons[m.group(1)] = m.group(2)
    if not liaisons:
        return source
    for nom, valeur in liaisons.items():
        corps = re.sub(r"\b%s\b" % re.escape(nom), "(%s)" % valeur, corps)
    return corps


def analyse(function_name, code):
    """Enveloppe normalisation.analyser : meme analyse, vocabulaire du cadre."""
    r = NH.analyser(function_name, _inliner_where(code))
    if r.get("forme") == "non-structurel" and code != _inliner_where(code):
        r = NH.analyser(function_name, code)
    forme = _FORMES.get(r.get("forme"), "unanalysable")
    base = r.get("base")
    pas = (r.get("canon") or "").replace("ELEM", "C1") or None
    if pas:
        # une liaison locale substituee laisse des parentheses autour d'un seul
        # terme : (REC) et REC doivent rendre le meme texte
        pas = re.sub(r"\((REC|C1|REST|[\w']+)\)", r"\1", pas).strip()
    if forme != "constructors":
        return {"forme": forme, "equations": {}, "base": None,
                "pas": pas, "motif": r.get("note", "")}
    return {"forme": forme, "base": base, "pas": pas,
            "equations": {"[]": base, "(x:xs)": pas}}


# ------------------------------------------------------------ categorisation
def categorise(message, compile_mais_faux=False):
    """Les categories du cadre ont ete tirees de GHC : la projection est directe."""
    if compile_mais_faux:
        return "wrong-result"
    m = message or ""
    if "Non-exhaustive patterns" in m or "non-exhaustive" in m.lower():
        return "missing-base-case"
    if "Variable not in scope" in m or "Data constructor not in scope" in m:
        return "unknown-name"
    if "parse error" in m or "lexical error" in m or "Parse error" in m:
        return "syntax"
    if "Couldn't match" in m or "No instance for" in m or "Ambiguous type" in m:
        return "incompatible-types"
    return "unclassified"


# ------------------------------------------------------------ references
def _references():
    try:
        from compiler_references import SOL
    except Exception:
        return {}
    familles = {"F-liste": ["somme", "longueur", "produit", "tous_positifs", "aplatir"]}
    return {f: [(n, SOL[n]) for n in noms if n in SOL] for f, noms in familles.items()}


REFERENCES = _references()
