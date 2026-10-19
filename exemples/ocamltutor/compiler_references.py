#!/usr/bin/env python3
"""Compile et execute les solutions de reference de chaque ancrage, avec le
gabarit de test du fournisseur et le compilateur du cours.

    python3 compiler_references.py
"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import activities_ml as A
import language_ml as L

SOL = {
 "bintree_count_leaves": "let rec bintree_count_leaves a =\n  match a with\n  | Leaf -> 1\n  | Node (_, g, d) -> bintree_count_leaves g + bintree_count_leaves d",
 "bintree_count_internal_nodes": "let rec bintree_count_internal_nodes a =\n  match a with\n  | Leaf -> 0\n  | Node (_, g, d) -> 1 + bintree_count_internal_nodes g + bintree_count_internal_nodes d",
 # à modif pour les tests
 "bintree_count_nodes": "let rec bintree_count_nodes a =\n  match a with\n  | Leaf -> 1\n  | Node (_, g, d) -> 1 + bintree_count_nodes g + bintree_count_nodes d",
 "bintree_height": "let rec bintree_height a =\n  match a with\n  | Leaf -> 0\n  | Node (_, g, d) -> 1 + max (bintree_height g) (bintree_height d)",
 "bintree_collect_values": "let rec bintree_collect_values a =\n  match a with\n  | Leaf -> []\n  | Node (x, g, d) -> bintree_collect_values g @ (x :: bintree_collect_values d)",
 "double_tete": "let double_tete l =\n  match premier l with\n  | None -> None\n  | Some x -> Some (2 * x)",
 "cent_sur_tete": "let cent_sur_tete l =\n  match premier l with\n  | None -> None\n  | Some x -> division 100 x",
 "pipeline": "let pipeline l =\n  match premiere l with\n  | None -> None\n  | Some s ->\n    match vers_entier s with\n    | None -> None\n    | Some n -> division 100 n",
 "longueur_premiere": "let longueur_premiere l =\n  match premiere l with\n  | None -> None\n  | Some s -> Some (String.length s)",
 # reemplois : version employant le schema, puis version a la main
 "bintree_count_even": "let rec bintree_count_even a =\n  match a with\n  | Leaf -> 0\n  | Node (x, g, d) -> (if x mod 2 = 0 then 1 else 0) + bintree_count_even g + bintree_count_even d",
 "bintree_min": "let rec bintree_min a =\n  match a with\n  | Leaf -> None\n  | Node (x, g, d) ->\n    let m u v = match u, v with\n      | None, r -> r | r, None -> r\n      | Some p, Some q -> Some (min p q) in\n    m (Some x) (m (bintree_min g) (bintree_min d))",
 "bintree_all_positive": "let rec bintree_all_positive a =\n  match a with\n  | Leaf -> true\n  | Node (x, g, d) -> x > 0 && bintree_all_positive g && bintree_all_positive d",
 "ubtree_count_bin": "let rec ubtree_count_bin a =\n  match a with\n  | UbLeaf -> 0\n  | Un t -> ubtree_count_bin t\n  | Bin (g, d) -> 1 + ubtree_count_bin g + ubtree_count_bin d",
 "mille_sur_tete": "let mille_sur_tete l =\n  match premier l with\n  | None -> None\n  | Some x -> division 1000 x",
 "lier": "let lier r f =\n  match r with\n  | Erreur m -> Erreur m\n  | Ok x -> f x",
}


def preambule(amorce, nom):
    """Amorce privee de sa ligne a completer : declarations de type et prelude."""
    lignes = [l for l in amorce.split("\n")
              if not l.strip().startswith("let rec %s " % nom)
              and not l.strip().startswith("let %s " % nom)
              and not l.strip().startswith("let %s(" % nom)]
    return "\n".join(lignes)


def executer(code, expressions):
    src = L.test_template(code, expressions)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "soumission" + L.extension)
        open(p, "w").write(src)
        r = subprocess.run(L.command(p), capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout.splitlines(), r.stderr.strip()


def main():
    total = ok = 0
    for pool, table in (("instance", A.ACTIVITES), ("reemploi", A.REEMPLOIS)):
        for famille, activites in table.items():
            for nom, _enonce, signature, amorce, tests in activites:
                total += 1
                sol = SOL.get(nom)
                if sol is None:
                    print("  %-30s AUCUNE SOLUTION DE REFERENCE" % nom)
                    continue
                code = preambule(amorce, nom) + "\n" + sol + "\n"
                rc, sortie, err = executer(code, [t[0] for t in tests])
                attendus = [t[1] for t in tests]
                if rc != 0:
                    print("  %-30s ECHEC DE COMPILATION : %s" % (nom, err.split("\n")[-1][:70]))
                    continue
                if sortie != attendus:
                    print("  %-30s SORTIE INATTENDUE %s, attendu %s" % (nom, sortie, attendus))
                    continue
                cat = L.categorise(err) if err else "-"
                a = L.analyse(nom, code)
                print("  %-30s ok  %-13s base=%-8s pas=%s"
                      % (nom, a["forme"], a["base"], a["pas"]))
                ok += 1
    print("\n%d ancrages sur %d compilent et passent leurs tests" % (ok, total))
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
