#!/usr/bin/env python3
"""Essai de bout en bout par HTTP, contre un serveur lance :

    TUTOR_DIR=exemples/rackettutor TUTOR_LANGUAGE=language_rkt PORT=8093 python3 serveur.py
    python3 exemples/rackettutor/sonde_http.py http://localhost:8093

Rejoue ce que fait la page etudiante : apres chaque soumission reussie, elle
relit l'etat. C'est cette relecture qui neutralisait la condition de stabilite
(observation O12). La sonde verifie que l'atelier s'ouvre a la meme solution
avec ou sans relecture.
"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compiler_references import SOL, preambule
import activities_rkt as A

B = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8093"


def post(p, d):
    r = urllib.request.Request(B + p, data=json.dumps(d).encode(), method="POST")
    return json.load(urllib.request.urlopen(r, timeout=60))


def get(p):
    return json.load(urllib.request.urlopen(B + p, timeout=60))


amorces = {a[0]: a[3] for a in A.ACTIVITES["F-arbre"]}
ordre = ["bintree-count-leaves", "bintree-count-internal-nodes", "bintree-sum",
         "bintree-height", "bintree-collect-values"]
ouverture = {}
for relire in (False, True):
    ident = post("/api/inscription", {"nom": "sonde%d" % relire, "cohorte": "ESSAI"})["ident"]
    for i, nom in enumerate(ordre, 1):
        r = post("/api/soumettre", {"ident": ident, "activite": nom,
                                    "code": preambule(amorces[nom], nom) + SOL[nom] + "\n"})
        d = r["etat"]["decision"]
        if relire:
            for _ in range(3):
                d = get("/api/etat?ident=" + ident)["decision"]
        print("  relecture=%-5s solution %d %-30s -> %s" % (relire, i, nom, d))
        if d == "abstraction":
            ouverture[relire] = i
            break
print("\natelier ouvert a la solution %s sans relecture, %s avec relecture : %s"
      % (ouverture.get(False), ouverture.get(True),
         "identique" if ouverture.get(False) == ouverture.get(True) else "ECART"))
sys.exit(0 if ouverture.get(False) == ouverture.get(True) else 1)
