"""Analyses de l'etude, sans dependance hors bibliotheque standard.

    python3 analyses.py hstutor/donnees

Rend un dictionnaire de resultats, que la console affiche et que prose.py
transforme en texte. Les tests sont implementes ici plutot qu'importes : le
tuteur ne doit rien exiger d'installe, et un enseignant qui lance la console
sur son poste n'a pas a se soucier de scipy.

Ce qui est calcule :

    Q1  reemploi spontane, contraste intra-sujet, t apparie et d de Cohen
    Q2  portee de la generalisation selon l'ancrage obligatoire, Fisher exact
    Q3  politique hors forme, comparaison de Welch, exploratoire
    Q4  etayage et reprises selon le regime
    processus  taux de reussite, erreurs silencieuses, categories
"""

import csv, json, math, os, sys


# ------------------------------------------------------------ statistiques

def _lgamma(x):
    return math.lgamma(x)


def _betacf(a, b, x):
    M, eps, fp = 200, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    if abs(d) < fp:
        d = fp
    d = 1 / d
    h = d
    for m in range(1, M + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        if abs(d) < fp:
            d = fp
        c = 1 + aa / c
        if abs(c) < fp:
            c = fp
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        if abs(d) < fp:
            d = fp
        c = 1 + aa / c
        if abs(c) < fp:
            c = fp
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < eps:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(_lgamma(a + b) - _lgamma(a) - _lgamma(b)
                  + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def p_de_t(t, df):
    """p bilaterale d'un t de Student."""
    if df <= 0 or not math.isfinite(t):
        return float("nan")
    return _ibeta(df / 2, 0.5, df / (df + t * t))


def moyenne(v):
    return sum(v) / len(v) if v else float("nan")


def ecart_type(v):
    if len(v) < 2:
        return float("nan")
    m = moyenne(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def t_apparie(a, b):
    d = [x - y for x, y in zip(a, b)]
    n, m, s = len(d), moyenne(d), ecart_type(d)
    if not n or not s:
        return {"n": n, "diff": m, "dz": float("nan"), "t": float("nan"),
                "p": float("nan")}
    t = m / (s / math.sqrt(n))
    return {"n": n, "diff": m, "dz": m / s, "t": t, "p": p_de_t(t, n - 1)}


def t_welch(a, b):
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return {"n1": n1, "n2": n2, "m1": moyenne(a), "m2": moyenne(b),
                "t": float("nan"), "p": float("nan")}
    v1, v2 = ecart_type(a) ** 2, ecart_type(b) ** 2
    se = math.sqrt(v1 / n1 + v2 / n2)
    t = (moyenne(a) - moyenne(b)) / se if se else float("nan")
    df = ((v1 / n1 + v2 / n2) ** 2 /
          ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)))
    return {"n1": n1, "n2": n2, "m1": moyenne(a), "m2": moyenne(b),
            "t": t, "df": df, "p": p_de_t(t, df)}


def fisher(a, b, c, d):
    """Test exact bilateral sur une table 2x2."""
    def lf(n):
        return _lgamma(n + 1)

    def pr(a, b, c, d):
        return math.exp(lf(a + b) + lf(c + d) + lf(a + c) + lf(b + d)
                        - lf(a) - lf(b) - lf(c) - lf(d) - lf(a + b + c + d))
    n, r1, c1 = a + b + c + d, a + b, a + c
    if min(n, r1, c1) < 0:
        return {"p": float("nan"), "or": float("nan")}
    obs, total = pr(a, b, c, d), 0.0
    for i in range(max(0, c1 - (n - r1)), min(r1, c1) + 1):
        q = pr(i, r1 - i, c1 - i, n - r1 - c1 + i)
        if q <= obs * 1.0000001:
            total += q
    rc = (a * d) / (b * c) if b and c else float("inf")
    return {"p": min(1.0, total), "or": rc}


# ------------------------------------------------------------ lecture

def _lire(dossier, nom):
    p = os.path.join(dossier, nom)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def joindre(dossier):
    concepts = _lire(dossier, "concepts.csv")
    conception = _lire(dossier, "conception.csv")
    pretest = {r["code"]: _num(r.get("total")) for r in _lire(dossier, "pretest.csv")}
    gen = {}
    for r in _lire(dossier, "generalisations.csv"):
        gen[(r["code"], r["concept"])] = (r.get("portee_retenue")
                                          or r.get("portee_moteur") or "")
    idx = {(r["code"], r["concept"]): r for r in concepts}
    lignes = []
    for r in conception:
        cle = (r["code"], r["concept"])
        c = idx.get(cle, {})
        lignes.append({
            "code": r["code"], "concept": r["concept"], "regime": r.get("regime", ""),
            "politique": r.get("politique_hors_forme", ""),
            "obligation": r.get("groupe_obligation", ""),
            "portee": gen.get(cle) or r.get("portee_generalisation", ""),
            "portee_moteur": r.get("portee_generalisation", ""),
            "hors_famille": _num(r.get("reemploi_hors_famille")),
            "reemplois": _num(c.get("reemplois")),
            "etayages": _num(c.get("etayages")),
            "ecartees": _num(c.get("solutions_ecartees")),
            "corpus": _num(c.get("solutions_au_corpus")),
            "pretest": pretest.get(r["code"], float("nan"))})
    return [l for l in lignes if l["regime"]]


# ------------------------------------------------------------ analyses

def analyser(dossier):
    d = joindre(dossier)
    if not d:
        return {"refus": "Aucune donnee jointe. Verifiez que concepts.csv et "
                         "conception.csv sont presents dans %s." % dossier}
    apprenants = sorted({l["code"] for l in d})
    concepts = sorted({l["concept"] for l in d})
    r = {"dossier": dossier, "apprenants": len(apprenants),
         "couples": len(d), "concepts": concepts,
         "simule": os.path.exists(os.path.join(dossier, "SIMULATION.md"))}

    # equilibre du plan
    r["equilibre"] = [{"concept": c,
                       "discovery": sum(1 for l in d if l["concept"] == c
                                        and l["regime"] == "discovery"),
                       "exposed": sum(1 for l in d if l["concept"] == c
                                      and l["regime"] == "exposed")}
                      for c in concepts]
    incomplets = sum(1 for a in apprenants
                     if sum(1 for l in d if l["code"] == a) < len(concepts))
    r["incomplets"] = incomplets

    # Q1
    valides = [l for l in d if math.isfinite(l["reemplois"])]
    par = {}
    for l in valides:
        o = par.setdefault(l["code"], {"d": [], "e": []})
        o["d" if l["regime"] == "discovery" else "e"].append(l["reemplois"] / 2.0)
    paires = [(moyenne(o["d"]), moyenne(o["e"])) for o in par.values()
              if o["d"] and o["e"]]
    r["q1"] = {
        "discovery": moyenne([l["reemplois"] / 2.0 for l in valides
                              if l["regime"] == "discovery"]),
        "exposed": moyenne([l["reemplois"] / 2.0 for l in valides
                            if l["regime"] == "exposed"]),
        "paires": len(paires),
        "inverses": sum(1 for a, b in paires if b > a),
        "par_concept": [{"concept": c,
                         "discovery": moyenne([l["reemplois"] / 2.0 for l in valides
                                               if l["concept"] == c
                                               and l["regime"] == "discovery"]),
                         "exposed": moyenne([l["reemplois"] / 2.0 for l in valides
                                             if l["concept"] == c
                                             and l["regime"] == "exposed"])}
                        for c in concepts]}
    r["q1"].update(t_apparie([a for a, _ in paires], [b for _, b in paires]))

    # les trois moments de mesure, si le jeu les porte
    re = _lire(dossier, "reemplois.csv")
    if re:
        moments = {}
        for m in ("t0", "t1", "t2"):
            sous = [x for x in re if x.get("moment") == m]
            if not sous:
                continue
            par_a = {}
            for x in sous:
                items = _num(x.get("items")) or 2
                o = par_a.setdefault(x["code"], {"d": [], "e": []})
                cle = "d" if x.get("regime") == "discovery" else "e"
                o[cle].append(_num(x.get("reussis")) / items)
            pr = [(moyenne(o["d"]), moyenne(o["e"])) for o in par_a.values()
                  if o["d"] and o["e"]]
            t = t_apparie([a for a, _ in pr], [b for _, b in pr])
            delais = [_num(x.get("delai_jours")) for x in sous]
            delais = [x for x in delais if math.isfinite(x)]
            moments[m] = {"discovery": moyenne([_num(x["reussis"]) / (_num(x["items"]) or 2)
                                                for x in sous
                                                if x.get("regime") == "discovery"]),
                          "exposed": moyenne([_num(x["reussis"]) / (_num(x["items"]) or 2)
                                              for x in sous
                                              if x.get("regime") == "exposed"]),
                          "delai_moyen": moyenne(delais), "n": len(pr),
                          "diff": t["diff"], "p": t["p"], "dz": t["dz"]}
        r["moments"] = moments

    # post-test, reemploi hors tuteur
    post = _lire(dossier, "posttest.csv")
    if post:
        cols = [c for c in post[0] if c.startswith("schema_")]
        v = [_num(x[c]) for x in post for c in cols if x[c] != ""]
        v = [x for x in v if math.isfinite(x)]
        r["q1"]["hors_tuteur"] = moyenne(v)
        r["q1"]["hors_tuteur_n"] = len(v)

    # Q2
    f = [l for l in d if l["obligation"] in ("complete", "retiree")
         and l["regime"] == "discovery"
         and l["portee"] in ("correcte", "trop etroite")]
    a = sum(1 for l in f if l["obligation"] == "complete" and l["portee"] == "correcte")
    b = sum(1 for l in f if l["obligation"] == "complete" and l["portee"] != "correcte")
    c = sum(1 for l in f if l["obligation"] == "retiree" and l["portee"] == "correcte")
    e = sum(1 for l in f if l["obligation"] == "retiree" and l["portee"] != "correcte")
    q2 = {"n_complete": a + b, "n_retiree": c + e,
          "p_complete": a / (a + b) if a + b else float("nan"),
          "p_retiree": c / (c + e) if c + e else float("nan")}
    q2.update(fisher(a, b, c, e))
    hf = [l for l in f if math.isfinite(l["hors_famille"])]
    if hf:
        q2["hf_complete"] = moyenne([l["hors_famille"] for l in hf
                                     if l["obligation"] == "complete"])
        q2["hf_retiree"] = moyenne([l["hors_famille"] for l in hf
                                    if l["obligation"] == "retiree"])
        q2["hf_correcte"] = moyenne([l["hors_famille"] for l in hf
                                     if l["portee"] == "correcte"])
        q2["hf_etroite"] = moyenne([l["hors_famille"] for l in hf
                                    if l["portee"] == "trop etroite"])
    # concordance des deux mesures de la portee
    deux = [l for l in d if l["portee"] and l["portee_moteur"]
            and l["portee"] != "non applicable"]
    if deux:
        q2["concordance"] = moyenne([1.0 if l["portee"] == l["portee_moteur"] else 0.0
                                     for l in deux])
        q2["concordance_n"] = len(deux)
    r["q2"] = q2

    # Q3
    ho = [l for l in d if l["ecartees"] > 0 and math.isfinite(l["reemplois"])]
    g1 = [l["reemplois"] for l in ho if l["politique"] == "confront"]
    g2 = [l["reemplois"] for l in ho if l["politique"] == "explain_and_continue"]
    r["q3"] = {"n": len(ho), "n_confront": len(g1), "n_continue": len(g2)}
    if len(g1) > 1 and len(g2) > 1:
        r["q3"].update(t_welch(g1, g2))

    # Q4
    ed = [l["etayages"] for l in d if l["regime"] == "discovery"
          and math.isfinite(l["etayages"])]
    ee = [l["etayages"] for l in d if l["regime"] == "exposed"
          and math.isfinite(l["etayages"])]
    r["q4"] = {"etayage": t_welch(ed, ee)}
    quest = _lire(dossier, "questionnaire.csv")
    if quest:
        r["q4"]["moment"] = {v: sum(1 for x in quest
                                    if x.get("moment_atelier_percu") == v)
                             for v in ("trop tot", "au bon moment", "trop tard")}
        for col in ("jauge_comprise", "jauge_utile", "etayage_utile"):
            v = [_num(x.get(col)) for x in quest]
            v = [x for x in v if math.isfinite(x)]
            if v:
                r["q4"][col] = moyenne(v)

    # processus
    s = _lire(dossier, "soumissions.csv")
    if s:
        ok = [x for x in s if _num(x.get("reussite")) == 1]
        cat = {}
        for x in s:
            if _num(x.get("reussite")) == 0:
                k = x.get("categorie_erreur", "?")
                cat[k] = cat.get(k, 0) + 1
        r["processus"] = {
            "soumissions": len(s), "reussite": len(ok) / len(s),
            "silencieuses": (moyenne([_num(x.get("erreur_silencieuse")) for x in ok])
                             if ok else float("nan")),
            "categories": sorted(cat.items(), key=lambda kv: -kv[1])[:8]}
    return r


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    print(json.dumps(analyser(sys.argv[1]), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
