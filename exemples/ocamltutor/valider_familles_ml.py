#!/usr/bin/env python3
"""Validation des familles OCaml avec le moteur de la coquille.

Reprend exactement la chaine de `normalisation2.aligner_corps`, mais en passant
par le fournisseur `language_ml` au lieu de l'analyseur Haskell : l'anti-unificateur
de `remontee.py` est celui du cadre, inchange. Fait aussi l'ablation de chaque
ancrage, comme `obligations.py`.

    python3 valider_familles_ml.py
"""
import os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = ICI                      # la coquille : le premier parent qui porte noyau.py
while not os.path.exists(os.path.join(RACINE, "noyau.py")) and RACINE != "/":
    RACINE = os.path.dirname(RACINE)
for d in (RACINE, ICI):
    if d not in sys.path:
        sys.path.insert(0, d)

import remontee as R
import normalisation2 as N2
import language_ml as L

FAMILLES = {
    # noms, type et ordre des champs du laboratoire 05 : Node (valeur, gauche, droit)
    "F-arbre": ("blocs", 2, [
        ("bintree_count_leaves", "let rec bintree_count_leaves a =\n  match a with\n  | Leaf -> 1\n  | Node (_, g, d) -> bintree_count_leaves g + bintree_count_leaves d"),
        ("bintree_count_internal_nodes", "let rec bintree_count_internal_nodes a =\n  match a with\n  | Leaf -> 0\n  | Node (_, g, d) -> 1 + bintree_count_internal_nodes g + bintree_count_internal_nodes d"),
        ("bintree_count_nodes", "let rec bintree_count_nodes a =\n  match a with\n  | Leaf -> 1\n  | Node (_, g, d) -> 1 + bintree_count_nodes g + bintree_count_nodes d"),
        ("bintree_height", "let rec bintree_height a =\n  match a with\n  | Leaf -> 0\n  | Node (_, g, d) -> 1 + max (bintree_height g) (bintree_height d)"),
        ("bintree_collect_values", "let rec bintree_collect_values a =\n  match a with\n  | Leaf -> []\n  | Node (x, g, d) -> bintree_collect_values g @ (x :: bintree_collect_values d)"),
    ]),
    "F-option": ("blocs", 1, [
        ("double_tete", "let double_tete l =\n  match premier l with\n  | None -> None\n  | Some x -> Some (2 * x)"),
        ("cent_sur_tete", "let cent_sur_tete l =\n  match premier l with\n  | None -> None\n  | Some x -> division 100 x"),
        ("pipeline", "let pipeline l =\n  match premiere l with\n  | None -> None\n  | Some s -> etape2 s"),
        ("longueur_premiere", "let longueur_premiere l =\n  match premiere l with\n  | None -> None\n  | Some s -> Some (String.length s)"),
    ]),
}


def aligner(corpus, granularite):
    """Meme calcul que N2.aligner_corps, avec l'analyse du fournisseur ml."""
    formes, bases = [], []
    for nom, src in corpus:
        a = L.analyse(nom, src)
        if a.get("pas") is None:
            continue
        formes.append(R.parse(R.tokens(a["pas"])))
        bases.append(a.get("base"))
    if len(formes) < 2:
        return 0, None
    R.Trou.n = 0
    subst = {}
    g = formes[0]
    for f in formes[1:]:
        g = R.antiunifier(g, f, subst)
    varie_base = len({b for b in bases if b is not None}) > 1
    fins = len(N2.compter_trous(g))
    blocs = (1 if varie_base else 0) + (1 if fins else 0)
    return (blocs if granularite == "blocs" else fins + (1 if varie_base else 0)), R.rendre(g)


def main():
    print("VALIDATION DES FAMILLES OCAML AVEC LE MOTEUR DE LA COQUILLE")
    print("=" * 70)
    for nom, (gran, attendu, corpus) in FAMILLES.items():
        pts, forme = aligner(corpus, gran)
        print("\n%s — %d ancrages, %s %d (attendu %d) : %s"
              % (nom, len(corpus), gran, pts, attendu,
                 "conforme" if pts == attendu else "NON CONFORME"))
        print("  forme generalisee : %s" % forme)
        print("  %-16s %-10s %-8s %s" % ("ancrage", "sans lui", "ecart", "verdict"))
        for i, (a_nom, _) in enumerate(corpus):
            reste = corpus[:i] + corpus[i + 1:]
            p, f = aligner(reste, gran)
            print("  %-16s %-10d %-+8d %s   %s"
                  % (a_nom, p, p - pts, "PORTEUR" if p != pts else "interchangeable", f))
        # l'ablation ne discrimine qu'a la granularite fine : les blocs saturent a 2
        pf, _ = aligner(corpus, "fins")
        print("  -- ablation a la granularite fine (complet : %d point(s)) --" % pf)
        for i, (a_nom, _) in enumerate(corpus):
            reste = corpus[:i] + corpus[i + 1:]
            p, f = aligner(reste, "fins")
            print("  %-16s %-10d %-+8d %s   %s"
                  % (a_nom, p, p - pf, "PORTEUR" if p != pf else "interchangeable", f))


if __name__ == "__main__":
    main()
