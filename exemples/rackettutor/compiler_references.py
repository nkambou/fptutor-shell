#!/usr/bin/env python3
"""Execute les solutions de reference de chaque ancrage avec le gabarit de test
du fournisseur et l'interprete Racket. Repris de l'instance OCaml.

    python3 compiler_references.py
"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import activities_rkt as A
import language_rkt as L

SOL = {
 "bintree-count-leaves": "(define (bintree-count-leaves t)\n  (cond [(leaf? t) 1]\n        [else (+ (bintree-count-leaves (node-l t)) (bintree-count-leaves (node-r t)))]))",
 "bintree-count-internal-nodes": "(define (bintree-count-internal-nodes t)\n  (cond [(leaf? t) 0]\n        [else (+ 1 (bintree-count-internal-nodes (node-l t)) (bintree-count-internal-nodes (node-r t)))]))",
 "bintree-sum": "(define (bintree-sum t)\n  (cond [(leaf? t) 0]\n        [else (+ (node-v t) (bintree-sum (node-l t)) (bintree-sum (node-r t)))]))",
 "bintree-height": "(define (bintree-height t)\n  (cond [(leaf? t) 0]\n        [else (+ 1 (max (bintree-height (node-l t)) (bintree-height (node-r t))))]))",
 "bintree-collect-values": "(define (bintree-collect-values t)\n  (cond [(leaf? t) '()]\n        [else (append (bintree-collect-values (node-l t))\n                      (cons (node-v t) (bintree-collect-values (node-r t))))]))",
 "double-tete": "(define (double-tete l)\n  (let ([x (premier l)])\n    (if x (* 2 x) #f)))",
 "cent-sur-tete": "(define (cent-sur-tete l)\n  (let ([x (premier l)])\n    (if x (division 100 x) #f)))",
 "pipeline": "(define (pipeline l)\n  (let ([s (premiere l)])\n    (if s\n        (let ([n (vers-entier s)])\n          (if n (division 100 n) #f))\n        #f)))",
 "longueur-premiere": "(define (longueur-premiere l)\n  (let ([s (premiere l)])\n    (if s (string-length s) #f)))",
 # reemplois : solutions ecrites a la main
 "bintree-count-even": "(define (bintree-count-even t)\n  (cond [(leaf? t) 0]\n        [else (+ (if (even? (node-v t)) 1 0) (bintree-count-even (node-l t)) (bintree-count-even (node-r t)))]))",
 "bintree-min": "(define (bintree-min t)\n  (define (m u v) (cond [(not u) v] [(not v) u] [else (min u v)]))\n  (cond [(leaf? t) #f]\n        [else (m (node-v t) (m (bintree-min (node-l t)) (bintree-min (node-r t))))]))",
 "bintree-all-positive": "(define (bintree-all-positive t)\n  (cond [(leaf? t) #t]\n        [else (and (> (node-v t) 0) (bintree-all-positive (node-l t)) (bintree-all-positive (node-r t)))]))",
 "ubtree-count-bin": "(define (ubtree-count-bin t)\n  (match t\n    [(ub-leaf) 0]\n    [(un s) (ubtree-count-bin s)]\n    [(bin l r) (+ 1 (ubtree-count-bin l) (ubtree-count-bin r))]))",
 "mille-sur-tete": "(define (mille-sur-tete l)\n  (let ([x (premier l)])\n    (if x (division 1000 x) #f)))",
 "lier": "(define (lier r f)\n  (if (erreur? r) r (f (ok-v r))))",
}


def activite(nom):
    for table in (A.ACTIVITES, A.REEMPLOIS):
        for acts in table.values():
            for a in acts:
                if a[0] == nom:
                    return a
    return None


def preambule(amorce, nom):
    """Amorce privee de la definition a completer."""
    i = amorce.find(";; %s :" % nom)
    return amorce[:i] if i >= 0 else amorce


def preambule_de(nom):
    a = activite(nom)
    return preambule(a[3], nom) if a else ""


def executer(code, expressions):
    src = L.test_template(code, expressions)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "soumission" + L.extension)
        open(p, "w").write(src)
        r = subprocess.run(L.command(p), capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout.splitlines(), r.stderr.strip()


def main():
    total = ok = 0
    for table in (A.ACTIVITES, A.REEMPLOIS):
        for famille, activites in table.items():
            for nom, _enonce, signature, amorce, tests in activites:
                total += 1
                sol = SOL.get(nom)
                if sol is None:
                    print("  %-30s AUCUNE SOLUTION DE REFERENCE" % nom)
                    continue
                code = preambule(amorce, nom) + sol + "\n"
                rc, sortie, err = executer(code, [t[0] for t in tests])
                attendus = [t[1] for t in tests]
                if rc != 0:
                    print("  %-30s ECHEC : %s" % (nom, err.split("\n")[0][:70]))
                    continue
                if sortie != attendus:
                    print("  %-30s SORTIE INATTENDUE %s, attendu %s" % (nom, sortie, attendus))
                    continue
                a = L.analyse(nom, code)
                print("  %-30s ok  %-13s base=%-8s pas=%s" % (nom, a["forme"], a["base"], a["pas"]))
                ok += 1
    print("\n%d ancrages sur %d passent leurs tests sous %s" % (ok, total, L.interprete()))
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
