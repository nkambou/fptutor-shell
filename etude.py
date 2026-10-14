"""Gestion d'une etude en classe : consentement, anonymat, export automatique.

Le principe est qu'aucune donnee de recherche ne sort du systeme sans deux
conditions reunies : la collecte est activee pour l'etude, et l'apprenant
concerne a donne son consentement. Un apprenant sans consentement enregistre
est exclu de l'export, ce qui est le comportement par defaut.

L'etude est decrite dans etude.json, distinct du referentiel :

    {
      "active": false,
      "nom": "INF6120-H26",
      "cadence": 25,
      "inclure_code": true,
      "dossier": "donnees",
      "consentements": {"<ident>": {"code": "P001", "consentement": "oui",
                                     "date": "2026-01-13", "retrait": ""}},
      "prochain_code": 2,
      "soumissions_depuis_export": 0
    }

Le fichier etude.json contient la correspondance entre l'identifiant interne
et le code d'anonymat. Il ne fait jamais partie de l'export : c'est la table
que l'enseignant garde sous cle.
"""

import json, os, csv, datetime

FICHIER = os.environ.get("ETUDE", "etude.json")

DEFAUT = {"active": False, "nom": "", "cadence": 25, "inclure_code": True,
          "dossier": "donnees", "consentements": {}, "prochain_code": 1,
          "soumissions_depuis_export": 0, "dernier_export": ""}


def lire():
    if not os.path.exists(FICHIER):
        return dict(DEFAUT)
    with open(FICHIER, encoding="utf-8") as f:
        e = json.load(f)
    for k, v in DEFAUT.items():
        e.setdefault(k, v)
    return e


def ecrire(e):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)


def code_de(e, ident):
    """Rend le code d'anonymat d'un apprenant, ou None s'il n'a pas consenti."""
    c = e["consentements"].get(ident)
    if not c or c.get("consentement") != "oui" or c.get("retrait"):
        return None
    return c.get("code")


def inscrire(e, ident, consentement="", date=""):
    """Enregistre un apprenant dans l'etude et lui attribue un code stable."""
    c = e["consentements"].setdefault(ident, {})
    if not c.get("code"):
        c["code"] = "P%03d" % e["prochain_code"]
        e["prochain_code"] += 1
    if consentement:
        c["consentement"] = consentement
        c["date"] = date or datetime.date.today().isoformat()
    c.setdefault("consentement", "")
    c.setdefault("retrait", "")
    return c["code"]


def retirer(e, ident):
    """Retrait du consentement : l'apprenant sort de tout export ulterieur."""
    c = e["consentements"].get(ident)
    if c:
        c["retrait"] = datetime.date.today().isoformat()


def apprenants_inclus(e, etat):
    return {i: code_de(e, i) for i in etat.get("apprenants", {})
            if code_de(e, i)}


def compter_soumission(e):
    """Appele a chaque soumission. Rend True lorsque la cadence est atteinte."""
    if not e.get("active"):
        return False
    e["soumissions_depuis_export"] = e.get("soumissions_depuis_export", 0) + 1
    return e["soumissions_depuis_export"] >= max(1, int(e.get("cadence", 25)))


def exporter(e, etat, journal_chemin):
    """Ecrit les fichiers d'analyse, restreints aux apprenants consentants.

    Rend un compte rendu : nombre d'apprenants inclus, exclus, fichiers ecrits.
    """
    import export_donnees as X
    inclus = apprenants_inclus(e, etat)
    exclus = [i for i in etat.get("apprenants", {}) if i not in inclus]
    if not inclus:
        return {"inclus": 0, "exclus": len(exclus), "fichiers": [],
                "message": "aucun apprenant consentant : rien n'a ete ecrit"}

    # un etat restreint, pour ne jamais transmettre les autres
    restreint = {"apprenants": {i: ap for i, ap in etat["apprenants"].items()
                                if i in inclus}}
    aff = {i: {"code": c, "cohorte": e.get("nom", ""), "consentement": "oui",
               "groupe_ordre": "", "groupe_obligation": "", "groupe_hors_forme": ""}
           for i, c in inclus.items()}

    lignes_journal = []
    if os.path.exists(journal_chemin):
        with open(journal_chemin, encoding="utf-8") as f:
            for l in f:
                if not l.strip():
                    continue
                ev = json.loads(l)
                if ev.get("apprenant") in inclus:
                    lignes_journal.append(ev)

    dossier = e.get("dossier", "donnees")
    os.makedirs(dossier, exist_ok=True)
    fichiers = []
    tables = (("participants.csv", X.table_participants, (restreint, aff)),
              ("soumissions.csv", X.table_soumissions, (lignes_journal, aff)),
              ("concepts.csv", X.table_concepts, (restreint, aff)),
              ("generalisations.csv", X.table_generalisations, (restreint, aff)),
              ("solutions.csv", X.table_solutions, (restreint, aff)),
              ("etayages.csv", X.table_etayages, (restreint, aff)),
              ("verifications.csv", X.table_verifications, (restreint, aff)))
    for nom, fabrique, args in tables:
        entetes, lignes = fabrique(*args)
        if nom == "solutions.csv" and not e.get("inclure_code", True):
            k = entetes.index("code_soumis")
            entetes = entetes[:k]
            lignes = [l[:k] for l in lignes]
        with open(os.path.join(dossier, nom), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(entetes)
            w.writerows(lignes)
        fichiers.append(nom)

    with open(os.path.join(dossier, "codebook.md"), "w", encoding="utf-8") as f:
        f.write(X.CODEBOOK)
    fichiers.append("codebook.md")

    e["soumissions_depuis_export"] = 0
    e["dernier_export"] = datetime.datetime.now().isoformat(timespec="seconds")
    return {"inclus": len(inclus), "exclus": len(exclus), "fichiers": fichiers,
            "dossier": dossier, "message": "export ecrit"}


def vue(e, etat):
    """Etat de l'etude pour la console enseignante."""
    lignes = []
    for i, ap in etat.get("apprenants", {}).items():
        c = e["consentements"].get(i, {})
        lignes.append({"ident": i, "nom": ap.get("nom", ""),
                       "code": c.get("code", ""),
                       "consentement": c.get("consentement", ""),
                       "retrait": c.get("retrait", ""),
                       "inclus": bool(code_de(e, i))})
    inclus = sum(1 for l in lignes if l["inclus"])
    return {"active": e.get("active", False), "nom": e.get("nom", ""),
            "cadence": e.get("cadence", 25),
            "inclure_code": e.get("inclure_code", True),
            "dossier": e.get("dossier", "donnees"),
            "dernier_export": e.get("dernier_export", ""),
            "depuis_export": e.get("soumissions_depuis_export", 0),
            "apprenants": sorted(lignes, key=lambda x: x["code"] or "zzz"),
            "inclus": inclus, "exclus": len(lignes) - inclus}
