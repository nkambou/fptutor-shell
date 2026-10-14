#!/usr/bin/env python3
"""Generateur de donnees d'experience simulees, reglable.

    python3 simulateur.py sortie/
    python3 simulateur.py sortie/ --n 68 --effet 0.14 --chute 0.45

A quoi cela sert avant le terrain. Un devis se juge a ce qu'il peut detecter,
non a ce qu'on espere trouver. En engendrant des cohortes sous des hypotheses
explicites, on voit quel ecart le devis rend visible, ou les cellules sont trop
petites, et quelle modification du protocole change la reponse. Le cout est de
quelques secondes, contre une session perdue si la question se pose apres la
collecte.

Les donnees produites sont SYNTHETIQUES. Le dossier recoit un fichier
SIMULATION.md qui le signale, et la console comme le redacteur le repercutent.
Aucun chiffre qui en sort ne doit figurer dans un article comme un resultat.

Parametres, avec leur valeur par defaut :

    n            68     apprenants
    concepts     6      concepts sous manipulation
    effet        0.14   ecart de reemploi entre decouverte et exposition
    base         0.48   taux de reemploi de reference, en exposition
    sd           0.16   ecart-type entre apprenants
    chute        0.45   chute de portee correcte quand l'ancrage est retire
    p_correcte   0.85   portee correcte quand l'ancrage est servi
    obligation   2      concepts portant la manipulation de l'ancrage
    hors_forme   0.12   proportion de soumissions correctes non comparables
    attrition    0.07   proportion d'apprenants n'allant pas au terme
    graine       0      graine du generateur, pour reproduire un jeu
"""

import argparse, csv, json, math, os, random, sys

CONCEPTS = ["map", "filter", "fold", "compose", "tree", "chain"]
SEQUENCES = {
    "A": ["discovery", "exposed", "discovery", "exposed", "discovery", "exposed"],
    "B": ["exposed", "discovery", "exposed", "discovery", "exposed", "discovery"],
    "C": ["discovery", "discovery", "exposed", "exposed", "discovery", "exposed"],
    "D": ["exposed", "exposed", "discovery", "discovery", "exposed", "discovery"],
}
POLITIQUES = ["confront", "explain_and_continue"]
CATEGORIES = ["missing-base-case", "incompatible-types", "unknown-name",
              "syntax", "wrong-result", "int-double-mix"]

DEFAUTS = {"inscrits": 70, "refus": 2, "retraits": 0, "abandons": 0.07,
           "concepts": 6, "devis": "intra", "part_test": 0.50, "obligation": 2,
           "p_temoin": 0.48, "p_test": 0.62, "dispersion": "moyenne",
           "p_avec": 0.85, "p_sans": 0.40, "hors_forme": 0.12, "graine": 0,
           "gain_t0": 1.40, "gain_t1": 1.20, "jours_t1": 5, "jours_t2": 18}

DISPERSION = {"faible": 0.09, "moyenne": 0.16, "forte": 0.24}


def resume(p=None):
    """Rend les quantites derivees, celles qui disent si le devis tient."""
    o = dict(DEFAUTS)
    o.update({k: v for k, v in (p or {}).items() if v is not None})
    consentants = max(0, int(o["inscrits"]) - int(o["refus"]) - int(o["retraits"]))
    concepts = max(2, min(len(CONCEPTS), int(o["concepts"])))
    manipules = max(0, min(concepts, int(o["obligation"])))
    if o["devis"] == "intra":
        # chaque apprenant voit les deux ordres : le contraste est apparie
        analysables = consentants
        cellule = round(consentants * manipules / 4.0)
        comparaison = "intra-sujet, contrebalance"
    elif o["devis"] == "groupes":
        n_test = round(consentants * float(o["part_test"]))
        analysables = min(n_test, consentants - n_test)
        cellule = round(n_test * manipules / 2.0)
        comparaison = "entre groupes, %d contre %d" % (n_test, consentants - n_test)
    else:
        analysables = consentants
        cellule = 0
        comparaison = "groupe unique, aucune comparaison d'ordre"
    ecart = float(o["p_test"]) - float(o["p_temoin"])
    ecart_t2 = float(o["p_test"]) - float(o["p_temoin"])
    return {"ecart_t0": ecart_t2 * float(o["gain_t0"]),
            "ecart_t1": ecart_t2 * float(o["gain_t1"]),
            "ecart_t2": ecart_t2,
            "jours_t1": int(o["jours_t1"]), "jours_t2": int(o["jours_t2"]),
            "consentants": consentants, "analysables": analysables,
            "au_terme": round(consentants * (1 - float(o["abandons"]))),
            "ecart": ecart, "cellule_obligation": cellule,
            "comparaison": comparaison,
            "chute_portee": float(o["p_avec"]) - float(o["p_sans"]),
            "dispersion": DISPERSION.get(o["dispersion"], 0.16)}


def _clamp(x, a=0.02, b=0.98):
    return max(a, min(b, x))


def engendrer(p=None):
    """Rend les tables d'un jeu simule, sans rien ecrire sur le disque."""
    o = dict(DEFAUTS)
    o.update({k: v for k, v in (p or {}).items() if v is not None})
    rnd = random.Random(o["graine"] or None)
    der = resume(o)
    # les parametres du modele se deduisent de la description de l'experience
    o["n"] = der["consentants"]
    o["base"] = float(o["p_temoin"])
    o["effet"] = der["ecart"]
    o["sd"] = der["dispersion"]
    o["p_correcte"] = float(o["p_avec"])
    o["chute"] = der["chute_portee"]
    o["attrition"] = float(o["abandons"])
    concepts = CONCEPTS[:max(2, min(len(CONCEPTS), int(o["concepts"])))]
    manipules = concepts[:max(0, min(len(concepts), int(o["obligation"])))]
    politique = {c: POLITIQUES[i % 2] for i, c in enumerate(concepts)}

    participants, conception, concepts_t, gen, soumissions = [], [], [], [], []
    reemplois_lignes = []
    pretest, posttest, questionnaire, affectation = [], [], [], []
    t = 0

    for i in range(int(o["n"])):
        code = "P%03d" % (i + 1)
        seq = "ABCD"[i % 4]
        if o["devis"] == "groupes":
            en_test = i < round(int(o["n"]) * float(o["part_test"]))
            regimes = {c: ("discovery" if en_test else "exposed") for c in CONCEPTS}
        elif o["devis"] == "unique":
            regimes = {c: "discovery" for c in CONCEPTS}
        else:
            regimes = dict(zip(CONCEPTS, SEQUENCES[seq]))
        aptitude = rnd.gauss(0, o["sd"])
        abandon = rnd.random() < o["attrition"]
        dernier = rnd.choice([3, 4, 5]) if abandon else len(concepts)

        oblig = {}
        for c in manipules:
            oblig[c] = ("retiree" if (regimes[c] == "discovery" and (i // 2) % 2 == 0)
                        else ("complete" if regimes[c] == "discovery" else "sans objet"))

        pre = sum(1 for _ in range(10)
                  if rnd.random() < _clamp(0.55 + 2.0 * aptitude))
        pretest.append([code] + [1 if rnd.random() < _clamp(0.55 + 2.0 * aptitude)
                                 else 0 for _ in range(10)] + [pre])

        acquis = generalises = instances = reemplois_tot = etayages_tot = 0
        ecartees_tot = resolutions = gen_ecrites = 0
        schemas = []

        for k, cid in enumerate(concepts):
            if k >= dernier:
                break
            decouverte = regimes[cid] == "discovery"
            retire = oblig.get(cid) == "retiree"

            n_inst = (rnd.choice([3, 3, 4, 4, 5]) if decouverte
                      else rnd.choice([2, 3, 3]))
            corpus = ecartees = etayages = echecs = 0
            for j in range(n_inst):
                essais = 1 + (1 if rnd.random() < _clamp(0.35 - 1.5 * aptitude, 0, 1) else 0)
                for e in range(essais):
                    t += rnd.randint(90, 900)
                    reussi = e == essais - 1
                    soumissions.append([
                        code,
                        "2026-01-%02dT%02d:%02d:00" % (12 + (t // 86400) % 50,
                                                       (t // 3600) % 24, (t // 60) % 60),
                        cid, 4 + k // 2, "%s%d" % (cid, j + 1),
                        1 if reussi else 0,
                        ("wrong-result" if reussi and rnd.random() < 0.06
                         else rnd.choice(CATEGORIES)),
                        1 if (reussi and rnd.random() < 0.055) else 0,
                        1 if rnd.random() < 0.04 else 0,
                        "" if reussi else "Pattern match(es) are non-exhaustive",
                        "instance"])
                    if not reussi:
                        echecs += 1
                        if rnd.random() < (0.55 if decouverte else 0.45):
                            etayages += 1
                if rnd.random() < o["hors_forme"]:
                    ecartees += 1
                else:
                    corpus += 1

            portee = "non applicable"
            if decouverte:
                pc = (o["p_correcte"] - o["chute"]) if retire else o["p_correcte"]
                portee = "correcte" if rnd.random() < _clamp(pc, 0, 1) else "trop etroite"
                gen_ecrites += 1
                texte = ("f g [] = []\\nf g (x:xs) = g x : f g xs"
                         if portee == "correcte"
                         else "f [] = []\\nf (x:xs) = x : f xs")
                # deux juges, accord imparfait comme dans la vraie vie
                j1 = portee if rnd.random() < 0.92 else (
                    "trop etroite" if portee == "correcte" else "correcte")
                j2 = j1 if rnd.random() < 0.90 else (
                    "trop etroite" if j1 == "correcte" else "correcte")
                gen.append([code, cid, len(texte.split()), texte, portee, j1, j2,
                            j1 if j1 == j2 else "a arbitrer"])

            # trois moments, trois delais, trois ecarts deduits du profil
            base_t = float(o["base"]) + aptitude
            moments = [
                ("t0", 0, der["ecart_t0"]),
                ("t1", max(1, int(rnd.gauss(der["jours_t1"], 1.5))), der["ecart_t1"]),
                ("t2", max(7, int(rnd.gauss(der["jours_t2"], 4))), der["ecart_t2"])]
            par_moment = {}
            for nom_m, jours, ecart_m in moments:
                taux_m = _clamp(base_t + (ecart_m if decouverte else 0))
                r_m = sum(1 for _ in range(2) if rnd.random() < taux_m)
                par_moment[nom_m] = (r_m, jours)
                reemplois_lignes.append([code, cid, nom_m, jours, r_m, 2,
                                         regimes[cid]])
            # la mesure agregee reste celle de T2, la principale
            taux = _clamp(base_t + (der["ecart_t2"] if decouverte else 0))
            reemplois = par_moment["t2"][0]
            hf = ""
            if cid in manipules:
                p_hf = taux + (0.05 if portee == "correcte" else -0.28)
                hf = 1 if rnd.random() < _clamp(p_hf, 0, 1) else 0

            etat = ("acquired" if reemplois == 2 else
                    "generalised" if portee != "non applicable" else "instances")
            acquis += etat == "acquired"
            generalises += etat == "generalised"
            instances += etat == "instances"
            reemplois_tot += reemplois
            etayages_tot += etayages
            ecartees_tot += ecartees
            resolutions += ecartees

            # horodatages de l'atelier et de la generalisation, en jours de cours
            jour_atelier = 7 * (2 + k) + rnd.randint(0, 2)
            concepts_t.append([code, cid, etat, corpus, ecartees, reemplois,
                               etayages, echecs,
                               1 if portee != "non applicable" else 0, 0, 0,
                               1 if decouverte else 0,
                               "2026-01-%02d" % (5 + min(24, jour_atelier)),
                               "2026-01-%02d" % (5 + min(24, jour_atelier)),
                               par_moment["t2"][1]])
            conception.append([code, cid, regimes[cid], politique[cid],
                               oblig.get(cid, "sans objet"), portee, hf])
            schemas.append(1 if rnd.random() < _clamp(taux - 0.05) else 0)

        participants.append([code, "SIM", "oui", seq,
                             oblig.get(manipules[0], "sans objet") if manipules else "",
                             politique[concepts[0]], "free",
                             acquis, generalises, instances, reemplois_tot,
                             etayages_tot, ecartees_tot, resolutions,
                             gen_ecrites, 0])
        affectation.append([code, "SIM", seq,
                            oblig.get(manipules[0], "sans objet") if manipules else "",
                            politique[concepts[0]], "oui",
                            "" if not abandon else str(4 + rnd.randint(0, 3))])
        n = len(schemas)
        ecrit = [1 if rnd.random() < _clamp(0.6 + aptitude) else 0
                 for _ in range(len(concepts))]
        sch = schemas + [0] * (len(concepts) - n)
        reco = [1 if rnd.random() < _clamp(0.55 + aptitude) else 0 for _ in range(6)]
        posttest.append([code] + ecrit + sch + reco
                        + [rnd.choice([0, 1, 2]), rnd.choice([0, 1, 2])]
                        + [1 if rnd.random() < _clamp(0.45 + aptitude) else 0
                           for _ in range(2)])
        questionnaire.append([code, rnd.randint(2, 5), rnd.randint(2, 5),
                              rnd.randint(1, 5), rnd.randint(3, 5),
                              rnd.choices(["trop tot", "au bon moment", "trop tard"],
                                          weights=[26, 55, 19])[0], ""])

    return {"o": o, "concepts": concepts, "manipules": manipules,
            "reemplois": reemplois_lignes,
            "participants": participants, "conception": conception,
            "concepts_t": concepts_t, "generalisations": gen,
            "soumissions": soumissions, "pretest": pretest,
            "posttest": posttest, "questionnaire": questionnaire,
            "affectation": affectation}


def ecrire(d, dossier):
    os.makedirs(dossier, exist_ok=True)
    o, concepts = d["o"], d["concepts"]

    def sortir(nom, entetes, lignes):
        with open(os.path.join(dossier, nom), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(entetes)
            w.writerows(lignes)

    sortir("participants.csv",
           ["code", "cohorte", "consentement", "groupe_ordre", "groupe_obligation",
            "groupe_hors_forme", "regime_choisi", "concepts_acquis",
            "concepts_generalises", "concepts_en_instances", "reemplois_total",
            "etayages_total", "solutions_ecartees", "problemes_resolus_autrement",
            "generalisations_ecrites", "a_travaille_en_groupe"], d["participants"])
    sortir("concepts.csv",
           ["code", "concept", "etat_final", "solutions_au_corpus",
            "solutions_ecartees", "reemplois", "etayages", "echecs_compilation",
            "generalisation_ecrite", "verifications_demandees",
            "verifications_non_expliquees", "dernier_compte_alignement",
            "horodatage_atelier", "horodatage_generalisation",
            "delai_reemploi_t2_jours"],
           d["concepts_t"])
    sortir("reemplois.csv",
           ["code", "concept", "moment", "delai_jours", "reussis", "items",
            "regime"], d["reemplois"])
    sortir("conception.csv",
           ["code", "concept", "regime", "politique_hors_forme",
            "groupe_obligation", "portee_generalisation", "reemploi_hors_famille"],
           d["conception"])
    sortir("generalisations.csv",
           ["code", "concept", "mots", "texte_generalisation", "portee_moteur",
            "portee_juge_1", "portee_juge_2", "portee_retenue"], d["generalisations"])
    sortir("soumissions.csv",
           ["code", "horodatage", "concept", "chapitre", "activite", "reussite",
            "categorie_erreur", "erreur_silencieuse", "hors_delai",
            "message_compilateur", "role_temporel"], d["soumissions"])
    sortir("pretest.csv",
           ["code"] + ["item_%d" % i for i in range(1, 11)] + ["total"], d["pretest"])
    sortir("posttest.csv",
           ["code"] + ["ecriture_%s" % c for c in concepts]
           + ["schema_%s" % c for c in concepts]
           + ["reco_%d" % i for i in range(1, 7)]
           + ["explication_1", "explication_2", "transfert_1", "transfert_2"],
           d["posttest"])
    sortir("questionnaire.csv",
           ["code", "jauge_comprise", "jauge_utile", "etayage_utile",
            "rythme_choisi", "moment_atelier_percu", "commentaire"],
           d["questionnaire"])
    sortir("affectation_anonymisee.csv",
           ["code", "cohorte", "groupe_ordre", "groupe_obligation",
            "groupe_hors_forme", "consentement", "abandon_semaine"], d["affectation"])

    with open(os.path.join(dossier, "SIMULATION.md"), "w", encoding="utf-8") as f:
        f.write("# Donnees SIMULEES\n\n"
                "Ce dossier ne contient aucune donnee reelle. Il a ete engendre "
                "pour eprouver la chaine d'analyse et juger ce que le devis peut "
                "detecter.\n\n## Parametres employes\n\n"
                + "\n".join("    %-12s %s" % (k, v) for k, v in sorted(o.items()))
                + "\n\nconcepts : %s\nconcepts avec manipulation de l'ancrage : %s\n"
                % (", ".join(concepts), ", ".join(d["manipules"]) or "aucun")
                + "\nAucun chiffre issu de ce dossier ne doit figurer dans un "
                  "article comme un resultat.\n")
    return dossier


def puissance(p=None, repetitions=200):
    """Taux de detection a 5 %, sur des cohortes engendrees puis analysees.

    Rend, pour l'effet de reemploi et pour la chute de portee, la proportion de
    replications ou le test conclut. C'est la reponse a « ce devis peut-il voir
    ce que j'espere trouver ».
    """
    import analyses
    o = dict(DEFAUTS)
    o.update({k: v for k, v in (p or {}).items() if v is not None})
    der = resume(o)
    conclut_q1 = conclut_q2 = 0
    ecarts, chutes = [], []
    for r in range(int(repetitions)):
        o["graine"] = 1000 + r
        d = engendrer(o)
        lignes = []
        idx = {(x[0], x[1]): x for x in d["concepts_t"]}
        gen = {(g[0], g[1]): g[7] for g in d["generalisations"]}
        for c in d["conception"]:
            k = (c[0], c[1])
            t = idx.get(k)
            if not t:
                continue
            lignes.append({"code": c[0], "regime": c[2], "obligation": c[4],
                           "portee": gen.get(k) or c[5], "reemplois": t[5]})
        par = {}
        for l in lignes:
            e = par.setdefault(l["code"], {"d": [], "e": []})
            e["d" if l["regime"] == "discovery" else "e"].append(l["reemplois"] / 2.0)
        paires = [(analyses.moyenne(x["d"]), analyses.moyenne(x["e"]))
                  for x in par.values() if x["d"] and x["e"]]
        t1 = analyses.t_apparie([a for a, _ in paires], [b for _, b in paires])
        if math.isfinite(t1["p"]) and t1["p"] < 0.05:
            conclut_q1 += 1
        ecarts.append(t1["diff"])
        f = [l for l in lignes if l["obligation"] in ("complete", "retiree")
             and l["regime"] == "discovery"
             and l["portee"] in ("correcte", "trop etroite")]
        a = sum(1 for l in f if l["obligation"] == "complete" and l["portee"] == "correcte")
        b = sum(1 for l in f if l["obligation"] == "complete" and l["portee"] != "correcte")
        c2 = sum(1 for l in f if l["obligation"] == "retiree" and l["portee"] == "correcte")
        e2 = sum(1 for l in f if l["obligation"] == "retiree" and l["portee"] != "correcte")
        fi = analyses.fisher(a, b, c2, e2)
        if math.isfinite(fi["p"]) and fi["p"] < 0.05:
            conclut_q2 += 1
        if a + b and c2 + e2:
            chutes.append(a / (a + b) - c2 / (c2 + e2))
    n = max(1, int(repetitions))
    return {"repetitions": n, "parametres": o,
            "resume": der,
            "q1": {"puissance": conclut_q1 / n,
                   "ecart_median": sorted(ecarts)[len(ecarts) // 2] if ecarts else None,
                   "cible": der["ecart"]},
            "q2": {"puissance": conclut_q2 / n,
                   "chute_mediane": sorted(chutes)[len(chutes) // 2] if chutes else None,
                   "cible": der["chute_portee"]}}


def main():
    a = argparse.ArgumentParser(description="Engendre un jeu de donnees simule.")
    a.add_argument("dossier")
    for k, v in DEFAUTS.items():
        a.add_argument("--" + k, type=type(v), default=None)
    a.add_argument("--puissance", type=int, default=0,
                   help="au lieu d'ecrire, estime la puissance sur N replications")
    o = a.parse_args()
    p = {k: getattr(o, k) for k in DEFAUTS}
    if o.puissance:
        print(json.dumps(puissance(p, o.puissance), indent=1, ensure_ascii=False))
        return
    d = engendrer(p)
    ecrire(d, o.dossier)
    print("Donnees SIMULEES ecrites dans %s" % o.dossier)
    print("  %d apprenants, %d soumissions, %d couples apprenant-concept"
          % (len(d["participants"]), len(d["soumissions"]), len(d["conception"])))


if __name__ == "__main__":
    main()
