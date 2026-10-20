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


ABSENT = ("Interprète OCaml introuvable : le serveur tourne, mais aucune "
          "soumission ne peut être compilée. Lancez-le avec OCAML_BIN, ou "
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


def reemploi(function_name, code):
    """Facultatif : consulte par noyau.schema_employe s'il existe. Meme regle que
    l'extension de suivi : pas de recursion propre, et une fonction passee a une
    abstraction."""
    return NML.reemploi(function_name, code)[0]


def categorise(message, compile_mais_faux=False):
    if compile_mais_faux:
        return "wrong-result"
    m = message or ""
    # Une erreur (« Error: ») empeche le code de s'executer ; un avertissement
    # (Warning 8, filtrage non exhaustif) ne l'empeche pas. Quand OCaml signale
    # les deux, on classe d'apres l'erreur, qui est ce qui bloque l'etudiant.
    if "Error:" in m:
        m = m[m.index("Error:"):]
    if "not exhaustive" in m or "not matched" in m:
        return "missing-base-case"
    if "This expression has type" in m and "int" in m and "float" in m:
        return "int-float-mix"
    # 'The constructor Node expects 3 argument(s), but is applied here to 2' :
    # un champ de Node oublie ou en trop, sans quoi le message restait non classe
    if "This expression has type" in m or "is applied to too many" in m \
            or "has no method" in m or ("expects" in m and "argument" in m):
        return "incompatible-types"
    if "Unbound value" in m or "Unbound constructor" in m or "Unbound type" in m:
        return "unknown-name"
    if "Syntax error" in m or "Parse error" in m:
        return "syntax"
    return "unclassified"


# ------------------------------------------------------------ etayage
# Textes attaches aux categories, remplacant ceux du cadre, ecrits pour Haskell
# (GHCi, equations, listes). Ils s'appuient sur les messages releves sur OCaml
# 4.14.2 avec le gabarit de test (voir JOURNAL_STAGE.md, « Releve des messages »).
#
# Version 2 (2026-10-20) : une idee par niveau, vingt mots au plus, et un niveau 1
# qui donne deja une piste (demande du superviseur). La version 1 expliquait le
# message d'OCaml sans aider a avancer, en 20 a 42 mots.
#   lecture  : ce qui se passe, affiche tout de suite (ce n'est pas un indice) ;
#   niveau 1 : la piste la plus probable ;
#   niveau 2 : ou regarder, dans le message d'OCaml ou dans l'enonce ;
#   niveau 3 : la charpente, jamais le corps.
# Aucun niveau ne donne la valeur du cas Leaf ni ne nomme le schema vise.
AIDES_ERREUR = {
 "missing-base-case": [
   "Votre match oublie une des deux formes d'arbre : Leaf ou Node. Laquelle n'a pas "
   "de cas ?",
   "Le message la nomme : regardez la ligne qui suit 'Here is an example of a case "
   "that is not matched'.",
   "Il faut un cas par forme : | Leaf -> ... | Node (x, g, d) -> ... Que doit rendre "
   "la fonction sur t0 = Leaf ?"],
 "incompatible-types": [
   "Comparez ce que rend chaque cas de votre match avec la signature de la fonction : "
   "un cas produit-il autre chose que le type attendu ?",
   "Dans le message, 'has type' est ce que vous avez écrit, 'was expected' ce qu'il "
   "fallait. La partie fautive est soulignée (^).",
   "Node a trois champs : Node (valeur, gauche, droit). Chaque appel récursif prend "
   "un seul sous-arbre."],
 "int-float-mix": [
   "Un nombre à virgule (1.0) ou un opérateur à point (+.) s'est glissé dans un "
   "calcul d'entiers.",
   "En OCaml, + - * / servent pour les int, et +. -. *. /. pour les float : on ne "
   "les mélange pas.",
   "Ces exercices n'utilisent que des int : écrivez 1 et non 1.0, et + et non +. "
   "(avec un point)."],
 "unknown-name": [
   "OCaml ne connaît pas un nom. Le plus souvent : le mot rec oublié, ou une faute "
   "de frappe.",
   "Lisez la ligne 'Hint:' du message : OCaml y propose souvent la correction.",
   "Une fonction qui s'appelle elle-même s'écrit let rec nom a = ... Les "
   "constructeurs prennent une majuscule : Leaf, Node."],
 "syntax": [
   "OCaml n'arrive pas à lire votre code. Par exemple, with oublié après "
   "match a, ou une parenthèse non fermée.",
   "Le message d'erreur de OCaml recopie la ligne où le compilateur s'est arrêté (le ^ la souligne). La faute "
   "est souvent indiquée juste avant : retrouvez cette ligne dans votre code et relisez celle "
   "du dessus (with, -> ou parenthèse fermante oublié ?).",
   "Forme attendue : let rec nom a = match a with | Leaf -> ... | Node (x, g, d) -> ..."],
 "wrong-result": [
   "Dans le tableau des résultats, regardez la ligne t0 : t0 est une simple feuille. "
   "Si elle est fausse, c'est votre cas Leaf qui ne retourne pas la bonne valeur.",
   "Si la ligne t0 est juste mais pas les autres, c'est votre cas Node qui combine mal "
   "les résultats de g et de d. Relisez l'énoncé; que doit-on en faire ?",
   # La premiere ligne fausse, et non t1 : selon l'erreur, t1 peut etre juste (par
   # exemple 1 + g + d pour la hauteur) et l'ecart n'apparaitre que sur t2.
   "Prenez la première ligne fausse du tableau et calculez à la main sur cet arbre : "
   "d'abord chaque feuille (votre cas Leaf), puis chaque nœud en remontant (votre cas "
   "Node). Où vous écartez-vous de la valeur attendue ?"],
 "unclassified": [
   "Si le tuteur indique un délai dépassé, votre fonction s'appelle sans fin : "
   "vérifiez vos appels récursifs.",
   "Sinon, lisez la ligne qui commence par 'Error:' : elle dit ce qu'OCaml reproche.",
   "Chaque appel récursif doit porter sur g ou d, jamais sur l'arbre entier."],
}

LECTURES = {
 "missing-base-case": "OCaml signale qu'un cas n'est pas traité dans votre match.",
 "incompatible-types": "Une valeur n'a pas le type attendu à cet endroit du code.",
 "int-float-mix": "Un entier et un nombre à virgule se rencontrent dans la même opération.",
 "unknown-name": "Un nom employé dans votre code n'est défini nulle part.",
 "syntax": "Le code ne peut pas être lu : le problème est dans l'écriture, avant le sens.",
 "wrong-result": "Votre code compile, mais ses résultats ne sont pas ceux attendus.",
 "unclassified": "OCaml a refusé votre définition, ou son exécution n'a pas abouti.",
}

# Textes du noyau precises pour les arbres (le noyau dit « cas de base » et « cas
# recursif ») : consigne de forme, raison d'une solution hors forme, et premiere
# question de verification avec des choix qui sont de l'OCaml (true, et non True).
CONSIGNE_FORME = ("en distinguant explicitement le cas de la feuille (Leaf) et le cas "
                  "du nœud (Node)")
VERIF_BASE = "Que rend votre fonction sur une feuille (Leaf) ?"
DISTRACTEURS_BASE = ("0", "1", "[]", "true", "None")
RAISONS = {
 "no-pattern": "elle ne distingue pas les cas : on n'y voit ni ce que vaut le résultat "
               "sur une feuille (Leaf), ni ce que vous faites d'un nœud (Node) et de "
               "ses deux sous-arbres",
}

# Indices propres a un exercice (noyau.aide) : ils remplacent l'indice general
# seulement pour cet exercice, cette categorie et ce niveau (None garde l'indice
# general). height est le seul exercice de la famille qui demande une fonction que
# l'etudiant n'ecrit pas lui-meme, max, peut-etre inconnue en debut de cours vu qu'ils viennent
# de le voir je pense. un
# indice general ne peut pas la nommer sans egarer sur les autres exercices.
# Le niveau 3 nomme max et montre son usage sur des nombres, sans ecrire le cas Node.
# Pour le resultat faux, chaque exercice a son propre niveau 3 : il eclaire sur des
# exemples du tableau (t0, t1, t2) ce que la fonction doit rendre, et nomme l'outil
# d'OCaml dont l'exercice a besoin (max, @, mod, &&), sans ecrire les cas Leaf et
# Node. Les niveaux 1 et 2 restent generaux. Aucun ne nomme le schema vise.
AIDES_EXERCICE = {
 "bintree_count_leaves": {
  "wrong-result": [None, None,
   "Sur t0 = Leaf, il y a exactement une feuille. Sur t1 = Node (3, Leaf, Leaf), il y "
   "en a deux, une dans chaque sous-arbre. Le nœud lui-même n'est pas une feuille."]},
 "bintree_count_internal_nodes": {
  "wrong-result": [None, None,
   "Sur t0 = Leaf, il n'y a aucun nœud interne. Sur t1 = Node (3, Leaf, Leaf), il y en "
   "a un seul : le nœud lui-même. Votre cas Node le compte-t-il, en plus de ceux de ses "
   "deux sous-arbres ?"]},
 "bintree_count_nodes": {
  "wrong-result": [None, None,
   "Ici, les feuilles comptent aussi comme des nœuds : t0 = Leaf a 1 nœud, et "
   "t1 = Node (3, Leaf, Leaf) en a 3, le nœud et ses deux feuilles."]},
 "bintree_height": {
  "wrong-result": [
   None,
   None,
   "La hauteur d'un nœud dépend du plus haut de ses deux sous-arbres. Pour garder le "
   "plus grand de deux entiers, OCaml fournit la fonction max : max (3) (5) vaut 5."],
 },
 "bintree_collect_values": {
  "wrong-result": [None, None,
   "Une feuille ne porte aucune valeur : sa liste est vide. Un nœud apporte sa valeur "
   "et les listes de ses deux sous-arbres. Pour mettre deux listes bout à bout, OCaml "
   "fournit @ : [1] @ [2; 3] vaut [1; 2; 3]."]},
 # exercices apres l'atelier : rien n'indique comment les resoudre (mesure du
 # reemploi spontane), seulement ce que la fonction doit rendre
 "bintree_count_even": {
  "wrong-result": [None, None,
   "Sur t2 = Node (2, Node (1, Leaf, Leaf), Node (4, Leaf, Leaf)), les nœuds qui portent "
   "un entier pair sont 2 et 4 : le résultat est 2. En OCaml, x est pair quand "
   "x mod 2 = 0."]},
 "bintree_all_positive": {
  "wrong-result": [None, None,
   "Une feuille ne porte aucun entier : rien ne la contredit. Pour un nœud, son entier "
   "et ses deux sous-arbres doivent convenir à la fois. En OCaml, && exige que deux "
   "conditions soient vraies."]},
 "bintree_count_internal_nodes_fold": {
  "wrong-result": [None, None,
   "Deux choix sont à faire : la valeur pour une feuille, et la façon de combiner la "
   "valeur d'un nœud avec les résultats de ses deux sous-arbres. Sur t1 = Node (3, "
   "Leaf, Leaf), le résultat attendu est 1."]},
 "bintree_collect_internal_nodes_fold": {
  "wrong-result": [None, None,
   "Deux choix sont à faire : la liste pour une feuille, et la façon de combiner la "
   "valeur d'un nœud avec les listes de ses deux sous-arbres. Pour mettre deux listes "
   "bout à bout, OCaml fournit @."]},
}


# formes rendues par analyser qui sont admissibles a l'alignement
ALIGNABLE_FORMS = ("constructors",)


# Solutions de reference par famille, pour la validation dans la console.
def _references():
    try:
        from compiler_references import SOL
    except Exception:
        return {}
    familles = {
        "F-arbre": ["bintree_count_leaves", "bintree_count_internal_nodes", "bintree_count_nodes",
                    "bintree_height", "bintree_collect_values"],
        "F-option": ["double_tete", "cent_sur_tete", "pipeline", "longueur_premiere"],
    }
    return {f: [(n, SOL[n]) for n in noms if n in SOL] for f, noms in familles.items()}


REFERENCES = _references()
