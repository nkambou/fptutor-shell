#!/usr/bin/env python3
"""Essai a blanc de HaskellTutor : une session complete, sans interface.

    python3 exemples/haskelltutor/essai_a_blanc.py

Rejoue ce qu'un apprenant fait, par le noyau du cadre : evaluation par runghc,
admission au corpus, alignement, decision de la politique, atelier, reemplois.
"""
import os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = ICI
while not os.path.exists(os.path.join(RACINE, "noyau.py")) and RACINE != "/":
    RACINE = os.path.dirname(RACINE)
sys.path.insert(0, RACINE)
sys.path.insert(0, ICI)
os.environ.setdefault("TUTOR_DIR", ICI)
os.environ.setdefault("TUTOR_LANGUAGE", "language_hs")

import noyau as N
from compiler_references import SOL

SCENARIO = [("somme", "reference"), ("longueur", "reference"),
            ("produit", "bibliotheque"), ("produit", "reference"),
            ("tous_positifs", "reference")]
BIBLIO = {"produit": "produit :: [Int] -> Int\nproduit xs = foldr (*) 1 xs"}
REEMPLOIS = [("compte_pairs", "schema employe", SOL["compte_pairs"], True),
             ("maximum_liste", "schema employe", SOL["maximum_liste"], True)]


def activite(nom, pool="instances"):
    table = N.ACTIVITES if pool == "instances" else N.REEMPLOIS
    for fam, acts in table.items():
        for a in acts:
            if a[0] == nom:
                return fam, a
    raise SystemExit("activite inconnue : %s" % nom)


def main():
    ref = N.referentiel()
    ap = N.nouvel_apprenant("essai", "ESSAI")
    cid = "liste-pli"
    print("ESSAI A BLANC — concept %s, interprete %s"
          % (cid, " ".join(N.LANGUE.command("x.hs"))))
    print("=" * 74)
    action = None
    for nom, variante in SCENARIO:
        famille, act = activite(nom)
        code = SOL[nom] if variante == "reference" else BIBLIO[nom]
        verdict = N.evaluer(code, act[4])
        adm = N.admettre(act[0], code, famille, verdict)
        print("\n  %s (%s)\n    compile=%s tests=%s | admise=%s %s"
              % (nom, variante, verdict["compile"], verdict["reussite"], adm["admis"],
                 "" if adm["admis"] else "(%s)" % adm["motif"]))
        if adm["admis"]:
            ap["corpus"].setdefault(cid, []).append({"nom": act[0], "code": code})
        elif verdict["reussite"]:
            ap["ecartes"].setdefault(cid, []).append({"nom": act[0], "motif": adm["motif"]})
        corpus = [(x["nom"], x["code"]) for x in ap["corpus"].get(cid, [])]
        if corpus:
            nb, forme, blocs = N.etat_alignement(corpus)
            print("    corpus=%d alignement=%d forme=%s" % (len(corpus), nb, forme))
        action, motif = N.decider(ref, ap, cid)
        print("    DECISION : %-12s %s" % (action, motif))
        if action == "abstraction":
            break
    if action != "abstraction":
        print("\n  la porte n'a pas ouvert")
        return 1

    print("\n  ATELIER D ABSTRACTION")
    aff = N.alignement_affichable(ap["corpus"][cid])
    for l in aff["lignes"]:
        print("    %-18s base=%-6s pas=%s" % (l["nom"], l["base"], l["pas"]))
    print("    ce qui varie : %d bloc(s), forme %s" % (aff["blocs"], aff["forme"]))
    print("    charpente    : %s" % N.squelette(aff["forme"]))
    ap["etats"][cid] = "generalised"

    print("\n  REEMPLOIS")
    for nom, etiq, sol, attendu in REEMPLOIS:
        famille, act = activite(nom, "reemplois")
        verdict = N.evaluer(sol, act[4])
        employe = N.schema_employe(nom, sol)
        print("    %-16s %-16s tests=%s reemploi=%s" % (nom, etiq, verdict["reussite"], employe))
        if verdict["reussite"] and employe:
            ap["reemplois"][cid] = ap["reemplois"].get(cid, 0) + 1
        action, motif = N.decider(ref, ap, cid)
        print("      DECISION : %-12s %s" % (action, motif))
    print("\n  etat final : %s, reemplois %d"
          % (ap["etats"][cid], ap["reemplois"].get(cid, 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
