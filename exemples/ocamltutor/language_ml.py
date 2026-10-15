"""Fournisseur de langage OCaml pour FPTutor-Shell.

Implemente l'interface attendue par le noyau : identification, commande
d'execution, gabarit du module de test, analyse vers le vocabulaire commun, et
classement des messages du compilateur. Rien du shell n'est modifie.
"""

import glob
import os
import shutil
import sys

import normalisation_ml as NML

name = "ml"
extension = ".ml"

# Nom affiche par les interfaces et langue par defaut du tuteur : deux elements
# que le cadre lisait auparavant dans ses propres pages, en dur.
titre = "OCamlTutor"
langue_defaut = "fr"
compilateur = "OCaml"      # nom affiche dans la page d'inscription


def interprete():
    """Chemin de l'interprete OCaml, cherche dans cet ordre :

        1. la variable d'environnement OCAML_BIN, si elle est definie ;
        2. le PATH courant ;
        3. les commutateurs opam du dossier personnel, le plus recent d'abord.

    Le troisieme cas existe parce qu'une installation par opam n'est dans le
    PATH qu'apres « eval $(opam env) » : un script lance depuis un
    environnement ou cette commande n'a pas ete evaluee ne trouve rien.
    """
    v = os.environ.get("OCAML_BIN")
    if v and os.path.exists(v):
        return v
    trouve = shutil.which("ocaml")
    if trouve:
        return trouve
    motifs = [os.path.expanduser("~/.opam/*/bin/ocaml"),
              "/usr/local/bin/ocaml", "/opt/homebrew/bin/ocaml"]
    candidats = []
    for m in motifs:
        candidats.extend(sorted(glob.glob(m), reverse=True))
    for c in candidats:
        if os.access(c, os.X_OK):
            return c
    return None


ABSENT = ("Interprete OCaml introuvable : le serveur tourne, mais aucune "
          "soumission ne peut etre compilee. Lancez-le avec OCAML_BIN, ou "
          "eval $(opam env) si OCaml vient d'opam.")


def command(chemin):
    # OCaml 4.14.2, la version LTS retenue par le cours. Le mode script de
    # l'interprete suffit : aucune compilation separee n'est necessaire.
    # -w +8 rend explicite l'avertissement de filtrage non exhaustif, qui est
    # ce que la categorie missing-base-case projette.
    #
    # Sans interprete, le serveur ne doit pas tomber : la commande rendue
    # echoue proprement avec un message lisible, que la categorisation range
    # dans « unclassified » et que l'apprenant voit comme une erreur du cadre,
    # non comme une erreur de son code.
    ocaml = interprete()
    if ocaml is None:
        return [sys.executable, "-c",
                "import sys; sys.stderr.write(%r); sys.exit(1)" % (ABSENT + "\n")]
    return [ocaml, "-w", "+8", chemin]


GABARIT = """%s

let () =
%s
"""


def test_template(code, expressions):
    # chaque expression de test rend une chaine : le cadre compare une ligne par
    # expression, et OCaml n'a pas d'affichage generique
    lignes = "\n".join("  print_endline (%s);" % e for e in expressions)
    return GABARIT % (code.rstrip(), lignes)


def analyse(function_name, code):
    return NML.analyser(function_name, code)


def categorise(message, compile_mais_faux=False):
    if compile_mais_faux:
        return "wrong-result"
    m = message or ""
    if "not exhaustive" in m or "not matched" in m:
        return "missing-base-case"
    if "This expression has type" in m and "int" in m and "float" in m:
        return "int-float-mix"
    if "This expression has type" in m or "is applied to too many" in m \
            or "has no method" in m:
        return "incompatible-types"
    if "Unbound value" in m or "Unbound constructor" in m or "Unbound type" in m:
        return "unknown-name"
    if "Syntax error" in m or "Parse error" in m:
        return "syntax"
    return "unclassified"


# formes rendues par analyser qui sont admissibles a l'alignement
ALIGNABLE_FORMS = ("constructors",)


# Solutions de reference par famille, pour la validation dans la console.
def _references():
    try:
        from compiler_references import SOL
    except Exception:
        return {}
    familles = {
        "F-arbre": ["bintree_count_leaves", "bintree_count_internal_nodes", "bintree_sum",
                    "bintree_height", "bintree_collect_values"],
        "F-option": ["double_tete", "cent_sur_tete", "pipeline", "longueur_premiere"],
    }
    return {f: [(n, SOL[n]) for n in noms if n in SOL] for f, noms in familles.items()}


REFERENCES = _references()
