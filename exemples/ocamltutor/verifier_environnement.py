#!/usr/bin/env python3
"""Verifie que l'environnement permet de faire tourner l'instance OCaml.

    python3 verifier_environnement.py

Quatre controles : l'interprete est trouve, il compile et execute un module
minimal, le fournisseur rend une forme canonique, et le referentiel se charge.
"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def dire(ok, texte, detail=""):
    print("  [%s] %s%s" % ("ok " if ok else "NON", texte,
                           "" if not detail else "  -> %s" % detail))
    return ok

def main():
    print("VERIFICATION DE L'ENVIRONNEMENT")
    tout = True
    try:
        import language_ml as L
        chemin = L.interprete()
        tout &= dire(True, "interprete OCaml trouve", chemin)
    except SystemExit as e:
        print(str(e))
        print("  PATH vu par Python :", os.environ.get("PATH", "")[:200])
        return 1

    v = subprocess.run([chemin, "-version"], capture_output=True, text=True)
    tout &= dire(v.returncode == 0, "version", v.stdout.strip() or v.stderr.strip())

    src = L.test_template("let f x = x + 1", ["string_of_int (f 41)"])
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "essai" + L.extension)
        open(p, "w").write(src)
        r = subprocess.run(L.command(p), capture_output=True, text=True, cwd=d)
    tout &= dire(r.returncode == 0 and r.stdout.strip() == "42",
                 "compilation et execution d'un module minimal",
                 r.stdout.strip() or r.stderr.strip()[:80])

    a = L.analyse("somme", "let rec somme a =\n  match a with\n"
                           "  | Leaf -> 0\n  | Node (x, g, d) -> x + somme g + somme d")
    tout &= dire(a["forme"] == "constructors" and a["pas"] is not None,
                 "le fournisseur rend une forme canonique",
                 "%s / %s" % (a["forme"], a["pas"]))

    import json
    ici = os.path.dirname(os.path.abspath(__file__))
    ref = os.path.join(ici, "referentiel.json")
    try:
        r = json.load(open(ref, encoding="utf-8"))
        fam = list(r.get("familles", {}))
        tout &= dire(bool(fam), "referentiel charge", "familles : %s" % ", ".join(fam))
    except Exception as e:
        tout &= dire(False, "referentiel charge", str(e))

    print("\n%s" % ("Environnement pret." if tout else
                    "Environnement incomplet : voir les lignes NON ci-dessus."))
    return 0 if tout else 1

if __name__ == "__main__":
    sys.exit(main())
