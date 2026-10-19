#!/usr/bin/env python3
"""Essai a blanc d'OCamlTutor : une session complete, sans interface.

Rejoue ce qu'un apprenant fait pendant l'activite, en passant par le noyau du
cadre : evaluation par le compilateur OCaml, admission au corpus, alignement,
decision de la politique avec ses trois conjonctions, atelier d'abstraction,
items de reemploi. Aucune interface n'est necessaire pour verifier que la boucle
tourne.

    TUTOR_DIR=mltutor TUTOR_LANGUAGE=language_ml python3 essai_a_blanc.py
"""
import os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = ICI                      # la coquille : le premier parent qui porte noyau.py
while not os.path.exists(os.path.join(RACINE, "noyau.py")) and RACINE != "/":
    RACINE = os.path.dirname(RACINE)
sys.path.insert(0, RACINE)
os.environ.setdefault("TUTOR_DIR", ICI)
os.environ.setdefault("TUTOR_LANGUAGE", "language_ml")

import noyau as N
from compiler_references import SOL, preambule

# ce que l'apprenant soumet, dans l'ordre, pour le concept arbre-pli(fold_tree)
SCENARIO = [
    ("bintree_count_leaves", "reference"),
    ("bintree_count_internal_nodes", "bibliotheque"),   # correcte mais non comparable
    ("bintree_count_internal_nodes", "reference"),
    ("bintree_height", "reference"),
    ("bintree_count_nodes", "reference"),
]
# solutions sans recursion sur l'arbre : une par valeur collectee, soit un par
# noeud interne ; un arbre ayant n noeuds internes porte n + 1 feuilles, donc
# 2n + 1 noeuds
BIBLIO = {"bintree_count_internal_nodes":
          "let bintree_count_internal_nodes a =\n"
          "  List.fold_left (fun n _ -> n + 1) 0 (bintree_collect_values a)\n",
          "bintree_count_nodes":
          "let bintree_count_nodes a =\n"
          "  List.fold_left (fun n _ -> n + 2) 1 (bintree_collect_values a)\n"}


def activite(nom, pool="instances"):
    table = N.ACTIVITES if pool == "instances" else N.REEMPLOIS
    for fam, acts in table.items():
        for a in acts:
            if a[0] == nom:
                return fam, a
    raise SystemExit("activite inconnue : %s" % nom)


def soumettre(ref, ap, cid, famille, act, code):
    verdict = N.evaluer(code, act[4])
    adm = N.admettre(act[0], code, famille, verdict)
    print("    compile=%s tests=%s | admise=%s %s"
          % (verdict["compile"], verdict["reussite"], adm["admis"],
             "" if adm["admis"] else "(%s)" % adm["motif"]))
    if adm["admis"]:
        ap["corpus"].setdefault(cid, []).append({"nom": act[0], "code": code})
    elif verdict["reussite"]:
        ap["ecartes"].setdefault(cid, []).append({"nom": act[0], "motif": adm["motif"]})
    return verdict, adm


def main():
    ref = N.referentiel()
    ap = N.nouvel_apprenant("essai", "INF6120-A26")
    cid = "arbre-pli"
    print("ESSAI A BLANC — concept %s, compilateur %s" % (cid, " ".join(N.LANGUE.command("x.ml"))))
    print("=" * 74)

    for nom, variante in SCENARIO:
        famille, act = activite(nom)
        # SOL dans compiler_references qui contient les implémentations récursives des fonctions
        if variante == "reference":
            code = preambule(act[3], nom) + "\n" + SOL[nom] + "\n"
        else:
            code = (preambule(act[3], nom) + "\n"
                    + SOL["bintree_collect_values"] + "\n\n" + BIBLIO[nom])
        print("\n  %s (%s)" % (nom, variante))
        soumettre(ref, ap, cid, famille, act, code)
        corpus = [(x["nom"], x["code"]) for x in ap["corpus"].get(cid, [])]
        if corpus:
            nb, forme, blocs = N.etat_alignement(corpus)
            print("    corpus=%d alignement fins=%d blocs=%d forme=%s"
                  % (len(corpus), nb, blocs, forme))
        action, motif = N.decider(ref, ap, cid)
        print("    DECISION : %-12s %s" % (action, motif))
        if action == "abstraction":
            break

    if action != "abstraction":
        print("\n  la porte n'a pas ouvert ; le garde-fou aurait pris le relais")
        return 1

    print("\n  ATELIER D'ABSTRACTION")
    aff = N.alignement_affichable(ap["corpus"][cid])
    for l in aff["lignes"]:
        print("    %-30s base=%-8s pas=%s" % (l["nom"], l["base"], l["pas"]))
    print("    ce qui varie : %d bloc(s), forme %s" % (aff["blocs"], aff["forme"]))
    for niveau in (1, 2, 3):
        print("    etayage %d : %s" % (niveau, N.aide("F-arbre", None, niveau, "abstraction")))

    ap["etats"][cid] = "generalised"
    ap["generalisations"][cid] = ("let rec fold_tree f z a = match a with "
                                 "Leaf -> z | Node (x, g, d) -> f x (fold_tree f z g) (fold_tree f z d)")
    print("    generalisation ecrite par l'apprenant : acceptee")

    print("\n  REEMPLOIS")
    for nom, avec_schema in (("bintree_min", False), ("bintree_all_positive", True)):
        famille, act = activite(nom, "reemplois")
        if avec_schema:
            code = (preambule(act[3], nom) + "\n"
                    + ap["generalisations"][cid] + "\n\n"
                    + "let %s a = fold_tree (fun x g d -> x > 0 && g && d) true a\n" % nom)
        else:
            code = preambule(act[3], nom) + "\n" + SOL[nom] + "\n"
        verdict = N.evaluer(code, act[4])
        employe = N.schema_employe(nom, code)
        print("    %-24s tests=%s schema employe=%s" % (nom, verdict["reussite"], employe))
        if verdict["reussite"] and employe:
            ap["reemplois"][cid] = ap["reemplois"].get(cid, 0) + 1
        action, motif = N.decider(ref, ap, cid)
        print("      DECISION : %-12s %s" % (action, motif))
    print("\n  etat final du concept : %s, reemplois %d"
          % (ap["etats"][cid], ap["reemplois"].get(cid, 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
