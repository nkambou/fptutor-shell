#!/usr/bin/env python3
"""Execute les solutions de reference de l'instance Haskell avec le gabarit du
fournisseur et runghc.

    python3 exemples/haskelltutor/compiler_references.py
"""
import os, subprocess, sys, tempfile
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import activities_hs as A
import language_hs as L

SOL = {
 "somme": "somme :: [Int] -> Int\nsomme [] = 0\nsomme (x:xs) = x + somme xs",
 "longueur": "longueur :: [Int] -> Int\nlongueur [] = 0\nlongueur (x:xs) = 1 + longueur xs",
 "produit": "produit :: [Int] -> Int\nproduit [] = 1\nproduit (x:xs) = x * produit xs",
 "tous_positifs": "tous_positifs :: [Int] -> Bool\ntous_positifs [] = True\ntous_positifs (x:xs) = x > 0 && tous_positifs xs",
 "aplatir": "aplatir :: [[Int]] -> [Int]\naplatir [] = []\naplatir (x:xs) = x ++ aplatir xs",
 "compte_pairs": "compte_pairs :: [Int] -> Int\ncompte_pairs = foldr (\\x n -> if even x then 1 + n else n) 0",
 "maximum_liste": "maximum_liste :: [Int] -> Int\nmaximum_liste = foldr1 max",
}


def executer(code, expressions):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "Soumission" + L.extension)
        open(p, "w").write(L.test_template(code, expressions))
        r = subprocess.run(L.command(p), capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout.splitlines(), r.stderr.strip()


def main():
    total = ok = 0
    for table in (A.ACTIVITES, A.REEMPLOIS):
        for famille, activites in table.items():
            for nom, _enonce, _sig, _amorce, tests in activites:
                total += 1
                sol = SOL.get(nom)
                if sol is None:
                    print("  %-18s AUCUNE SOLUTION DE REFERENCE" % nom); continue
                rc, sortie, err = executer(sol, [t[0] for t in tests])
                attendus = [t[1] for t in tests]
                if rc != 0:
                    print("  %-18s ECHEC : %s" % (nom, err.split("\n")[0][:70])); continue
                if sortie != attendus:
                    print("  %-18s SORTIE %s, attendu %s" % (nom, sortie, attendus)); continue
                a = L.analyse(nom, sol)
                print("  %-18s ok  %-14s base=%-5s pas=%s"
                      % (nom, a["forme"], a["base"], a["pas"]))
                ok += 1
    print("\n%d ancrages sur %d passent leurs tests sous %s" % (ok, total, L.interprete()))
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
