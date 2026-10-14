#!/usr/bin/env python3
"""Banc des exercices de suivi : des reponses justes et fausses, soumises au
tuteur en mode apercu, qui ne touche pas aux resultats des etudiants.

    python3 ocamltutor/banc_suivi.py          depuis FPTutor, tuteur lance

A faire tourner avec le VRAI compilateur OCaml : avec le substitut, toute
reponse completee est acceptee et le banc n'a aucun sens.
Chaque reponse fausse doit etre refusee ; chaque reponse juste acceptee, et
comptee comme reemploi seulement si elle passe par un pli.
"""
import json, os, sys, urllib.request
B = os.environ.get("TUTEUR_URL", "http://localhost:8081")
T = os.environ.get("TUTEUR", "ocamltutor")
def post(c,d):
    r=urllib.request.Request(B+c,data=json.dumps(d).encode(),headers={"Content-Type":"application/json"},method="POST")
    return json.load(urllib.request.urlopen(r))
sys.path.insert(0,T); import activities_ml as A
AMORCE={a[0]:a[3] for a in A.REEMPLOIS["F-arbre"]}
def entete(item): return AMORCE[item].rsplit("let rec",1)[0]

PLI = """let rec plier f z a = match a with
  | Leaf -> z
  | Node (x, g, d) -> f x (plier f z g) (plier f z d)
"""
CAS = {
"bintree_count_even": [
 ("compte tous les noeuds", "let rec bintree_count_even a = match a with Leaf -> 0 | Node (_,g,d) -> 1 + bintree_count_even g + bintree_count_even d", False, None),
 ("racine seulement", "let bintree_count_even a = match a with Node (x,_,_) when x mod 2 = 0 -> 1 | _ -> 0", False, None),
 ("impairs", "let rec bintree_count_even a = match a with Leaf -> 0 | Node (x,g,d) -> (if x mod 2 <> 0 then 1 else 0) + bintree_count_even g + bintree_count_even d", False, None),
 ("gauche seulement", "let rec bintree_count_even a = match a with Leaf -> 0 | Node (x,g,_) -> (if x mod 2 = 0 then 1 else 0) + bintree_count_even g", False, None),
 ("recursion a la main, juste", "let rec bintree_count_even a = match a with Leaf -> 0 | Node (x,g,d) -> (if x mod 2 = 0 then 1 else 0) + bintree_count_even g + bintree_count_even d", True, False),
 ("pli redefini", PLI + "let bintree_count_even a = plier (fun x g d -> (if x mod 2 = 0 then 1 else 0) + g + d) 0 a", True, True),
],
"bintree_all_positive": [
 ("toujours vrai", "let bintree_all_positive a = true", False, None),
 ("racine seulement", "let bintree_all_positive a = match a with Leaf -> true | Node (x,_,_) -> x > 0", False, None),
 ("gauche seulement", "let rec bintree_all_positive a = match a with Leaf -> true | Node (x,g,_) -> x > 0 && bintree_all_positive g", False, None),
 ("positif au sens large", "let rec bintree_all_positive a = match a with Leaf -> true | Node (x,g,d) -> x >= 0 && bintree_all_positive g && bintree_all_positive d", False, None),
 ("recursion a la main, juste", "let rec bintree_all_positive a = match a with Leaf -> true | Node (x,g,d) -> x > 0 && bintree_all_positive g && bintree_all_positive d", True, False),
 ("pli redefini", PLI + "let bintree_all_positive a = plier (fun x g d -> x > 0 && g && d) true a", True, True),
],
"ubtree_count_bin": [
 ("sommet seulement", "let ubtree_count_bin a = match a with Bin _ -> 1 | _ -> 0", False, None),
 ("sans traverser Un", "let rec ubtree_count_bin a = match a with UbLeaf -> 0 | Un _ -> 0 | Bin (g,d) -> 1 + ubtree_count_bin g + ubtree_count_bin d", False, None),
 ("recursion a la main, juste", "let rec ubtree_count_bin a = match a with UbLeaf -> 0 | Un t -> ubtree_count_bin t | Bin (g,d) -> 1 + ubtree_count_bin g + ubtree_count_bin d", True, False),
 ("pli propre au nouveau type", """let rec plier_ub f1 f2 z a = match a with
  | UbLeaf -> z
  | Un t -> f1 (plier_ub f1 f2 z t)
  | Bin (g, d) -> f2 (plier_ub f1 f2 z g) (plier_ub f1 f2 z d)
let ubtree_count_bin a = plier_ub (fun n -> n) (fun g d -> 1 + g + d) 0 a""", True, True),
],
}
post("/api/ext/admin/apercu/entrer", {"nom":"banc"})
defaut = 0
for item, cas in CAS.items():
    print("\n==", item)
    for lib, code, attendu_correct, attendu_pli in cas:
        r = post("/api/ext/admin/apercu/soumettre", {"nom":"banc","item":item,"code":entete(item)+code+"\n"})
        etat = json.load(open(os.path.join(T,"suivi_etat.json")))["apercus"]["banc"]["resultats"].get(item, {})
        juste = r["correct"] == attendu_correct
        ligne = "  %-34s correct=%-5s %s" % (lib, r["correct"], "" if juste else "<-- ATTENDU %s" % attendu_correct)
        if r["correct"]:
            ligne += " | reemploi=%s (%s)" % (etat.get("reemploi"), etat.get("forme"))
            if attendu_pli is not None and bool(etat.get("pli_arbre")) != attendu_pli:
                ligne += " <-- pli attendu %s" % attendu_pli; juste = False
        if not juste: defaut += 1
        print(ligne)
        # on retire le resultat pour que l'item reste ouvert
        e = json.load(open(os.path.join(T,"suivi_etat.json"))); e["apercus"]["banc"]["resultats"].pop(item, None)
        json.dump(e, open(os.path.join(T,"suivi_etat.json"),"w"))
st = json.load(urllib.request.urlopen(B + "/api/ext/statut"))
if st.get("compilateur_simule"):
    print("\nATTENTION : compilateur simule, ce banc n'a pas de sens dans ce mode.")
print("\n%d ecart(s)" % defaut)
