#!/usr/bin/env python3
"""Essai a blanc de RacketTutor : une session complete, sans interface.
Repris de l'instance OCaml ; memes etapes, meme scenario.

    python3 exemples/rackettutor/essai_a_blanc.py

Rejoue ce qu'un apprenant fait, par le noyau du cadre : evaluation par Racket,
admission au corpus, alignement, decision de la politique, atelier, reemplois.
Ajoute deux sondes de la mesure de reemploi, qui sont la mesure principale
d'une etude : une enveloppe autour d'une recursion ecrite a la main, et une
definition que l'analyse ne sait pas lire.
"""
import os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = ICI                      # la coquille : le premier parent qui porte noyau.py
while not os.path.exists(os.path.join(RACINE, "noyau.py")) and RACINE != "/":
    RACINE = os.path.dirname(RACINE)
sys.path.insert(0, RACINE)
sys.path.insert(0, ICI)
os.environ.setdefault("TUTOR_DIR", ICI)
os.environ.setdefault("TUTOR_LANGUAGE", "language_rkt")

import noyau as N
from compiler_references import SOL, preambule

SCENARIO = [
    ("bintree-count-leaves", "reference"),
    ("bintree-count-internal-nodes", "reference"),
    ("bintree-sum", "bibliotheque"),        # correcte mais non comparable
    ("bintree-sum", "reference"),
    ("bintree-height", "reference"),
]
BIBLIO = {"bintree-sum": "(define (bintree-sum t) (foldl + 0 (bintree-collect-values t)))\n"}

FOLD = ("(define (fold-tree f z t)\n"
        "  (cond [(leaf? t) z]\n"
        "        [else (f (node-v t) (fold-tree f z (node-l t)) (fold-tree f z (node-r t)))]))\n")

# (nom, etiquette, code ajoute a l'amorce, reemploi attendu)
REEMPLOIS = [
    ("bintree-min", "recursion a la main", SOL["bintree-min"], False),
    ("bintree-all-positive", "schema employe",
     FOLD + "(define (bintree-all-positive t)\n"
            "  (fold-tree (lambda (x g d) (and (> x 0) g d)) #t t))\n", True),
    ("bintree-count-even", "schema employe",
     FOLD + "(define (bintree-count-even t)\n"
            "  (fold-tree (lambda (x g d) (+ (if (even? x) 1 0) g d)) 0 t))\n", True),
]

# erreurs typiques, pour lire ce que l'etayage dit a l'apprenant
ERREURS = [
    ("cas de base absent (cond)",
     "(define (bintree-sum t)\n  (cond [(node? t) (+ (node-v t) (bintree-sum (node-l t)) (bintree-sum (node-r t)))]))\n"),
    ("cas de base absent (accesseur)",
     "(define (bintree-sum t)\n  (+ (node-v t) (bintree-sum (node-l t)) (bintree-sum (node-r t))))\n"),
    ("types incompatibles",
     "(define (bintree-sum t)\n  (cond [(leaf? t) \"0\"]\n        [else (+ (node-v t) (bintree-sum (node-l t)) (bintree-sum (node-r t)))]))\n"),
    ("parenthese manquante",
     "(define (bintree-sum t)\n  (cond [(leaf? t) 0]\n        [else (+ (node-v t) (bintree-sum (node-l t)) (bintree-sum (node-r t)))])\n"),
]
SONDES = [
    ("bintree-count-even", "enveloppe d'une recursion a la main",
     "(define (compte t)\n  (cond [(leaf? t) 0]\n"
     "        [else (+ (if (even? (node-v t)) 1 0) (compte (node-l t)) (compte (node-r t)))]))\n"
     "(define (bintree-count-even t) (compte t))\n", False),
    ("bintree-count-even", "define/contract, recursion a la main",
     "(define/contract (bintree-count-even t)\n  (-> any/c integer?)\n"
     "  (cond [(leaf? t) 0]\n"
     "        [else (+ (if (even? (node-v t)) 1 0) (bintree-count-even (node-l t))"
     " (bintree-count-even (node-r t)))]))\n", False),
    ("bintree-count-even", "schema employe",
     FOLD + "(define (bintree-count-even t)\n"
            "  (fold-tree (lambda (x g d) (+ (if (even? x) 1 0) g d)) 0 t))\n", True),
]


def activite(nom, pool="instances"):
    table = N.ACTIVITES if pool == "instances" else N.REEMPLOIS
    for fam, acts in table.items():
        for a in acts:
            if a[0] == nom:
                return fam, a
    raise SystemExit("activite inconnue : %s" % nom)


def main():
    ref = N.referentiel()
    ap = N.nouvel_apprenant("essai", "INF6120-A26")
    cid = "arbre-pli"
    print("ESSAI A BLANC — concept %s, interprete %s" % (cid, " ".join(N.LANGUE.command("x.rkt"))))
    print("=" * 74)
    action = None
    for nom, variante in SCENARIO:
        famille, act = activite(nom)
        base = preambule(act[3], nom)
        code = base + (SOL[nom] if variante == "reference"
                       else SOL["bintree-collect-values"] + "\n" + BIBLIO[nom]) + "\n"
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

    print("\n  ATELIER D'ABSTRACTION")
    aff = N.alignement_affichable(ap["corpus"][cid])
    for l in aff["lignes"]:
        print("    %-30s base=%-6s pas=%s" % (l["nom"], l["base"], l["pas"]))
    print("    ce qui varie : %d bloc(s), forme %s" % (aff["blocs"], aff["forme"]))
    for niveau in (1, 2, 3):
        print("    etayage %d : %s" % (niveau, N.aide("F-arbre", None, niveau, "abstraction")))
    ap["etats"][cid] = "generalised"

    print("\n  REEMPLOIS")
    for nom, etiq, sol, attendu in REEMPLOIS:
        famille, act = activite(nom, "reemplois")
        code = preambule(act[3], nom) + sol
        verdict = N.evaluer(code, act[4])
        employe = N.schema_employe(nom, code)
        print("    %-22s %-24s tests=%s reemploi=%s" % (nom, etiq, verdict["reussite"], employe))
        if verdict["reussite"] and employe:
            ap["reemplois"][cid] = ap["reemplois"].get(cid, 0) + 1
        action, motif = N.decider(ref, ap, cid)
        print("      DECISION : %-12s %s" % (action, motif))

    print("\n  SONDES DE LA MESURE DE REEMPLOI")
    ecarts = 0
    for nom, etiq, sol, attendu in SONDES:
        famille, act = activite(nom, "reemplois")
        code = preambule(act[3], nom) + sol
        verdict = N.evaluer(code, act[4])
        employe = N.schema_employe(nom, code)
        ok = employe == attendu
        ecarts += not ok
        print("    %-38s tests=%s forme=%-13s reemploi=%-5s %s"
              % (etiq, verdict["reussite"], N.LANGUE.analyse(nom, code)["forme"], employe,
                 "ok" if ok else "FAUX %s" % ("POSITIF" if employe else "NEGATIF")))
    print("\n  ETAYAGE SUR ERREUR (famille F-arbre, bintree-sum)")
    famille, act = activite("bintree-sum")
    for etiq, sol in ERREURS:
        code = preambule(act[3], "bintree-sum") + sol
        verdict = N.evaluer(code, act[4])
        cat = N.categoriser(verdict)
        print("    %s -> %s" % (etiq, cat))
        for niveau in (1, 2, 3):
            print("      %d. %s" % (niveau, N.aide("F-arbre", cat, niveau)))
    print("\n  etat final : %s, reemplois %d, ecarts de mesure %d"
          % (ap["etats"][cid], ap["reemplois"].get(cid, 0), ecarts))
    return 1 if ecarts else 0


if __name__ == "__main__":
    sys.exit(main())
