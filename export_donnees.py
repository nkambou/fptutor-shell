"""Export des donnees d'experimentation vers des fichiers CSV prets a l'analyse.

    python3 export_donnees.py etat.json journal.jsonl affectation.csv sortie/

Produit sept fichiers dans le dossier de sortie. Aucun nom ni identifiant
nominatif n'y figure : seul le code d'anonymat de la table d'affectation est
repris. Le fichier affectation.csv est celui que l'enseignant garde hors du
jeu de donnees, sous cle, avec la correspondance code <-> apprenant.

Colonnes documentees dans codebook.md, produit par le meme appel.
"""

import csv, json, os, sys, datetime, statistics


# ------------------------------------------------------------ utilitaires

def lire_journal(chemin):
    if not os.path.exists(chemin):
        return []
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def lire_affectation(chemin):
    """code, ident, groupe_ordre, groupe_obligation, groupe_hors_forme, consentement"""
    if not os.path.exists(chemin):
        return {}
    with open(chemin, encoding="utf-8") as f:
        return {r["ident"]: r for r in csv.DictReader(f)}


def ecrire(dossier, nom, entetes, lignes):
    chemin = os.path.join(dossier, nom)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(entetes)
        w.writerows(lignes)
    print("  %-28s %5d lignes" % (nom, len(lignes)))


def secondes(a, b):
    try:
        return round((datetime.datetime.fromisoformat(b)
                      - datetime.datetime.fromisoformat(a)).total_seconds(), 1)
    except Exception:
        return ""


# ------------------------------------------------------------ tables

def table_participants(etat, aff):
    lignes = []
    for ident, ap in etat["apprenants"].items():
        a = aff.get(ident, {})
        etats = ap.get("etats", {})
        lignes.append([
            a.get("code", ident), a.get("cohorte", ap.get("cohorte", "")),
            a.get("consentement", ""), a.get("groupe_ordre", ""),
            a.get("groupe_obligation", ""), a.get("groupe_hors_forme", ""),
            ap.get("regime", ""),
            sum(1 for v in etats.values() if v == "acquired"),
            sum(1 for v in etats.values() if v == "generalised"),
            sum(1 for v in etats.values() if v == "instances"),
            sum(ap.get("reemplois", {}).values()),
            sum(ap.get("aides", {}).values()),
            sum(len(v) for v in ap.get("ecartes", {}).values()),
            sum(ap.get("resolutions", {}).values()) if isinstance(
                ap.get("resolutions", {}), dict) else "",
            len(ap.get("generalisations", {})),
            1 if ap.get("groupe") else 0,
        ])
    return (["code", "cohorte", "consentement", "groupe_ordre", "groupe_obligation",
             "groupe_hors_forme", "regime_choisi", "concepts_acquis",
             "concepts_generalises", "concepts_en_instances", "reemplois_total",
             "etayages_total", "solutions_ecartees", "problemes_resolus_autrement",
             "generalisations_ecrites", "a_travaille_en_groupe"], lignes)


def table_soumissions(journal, aff):
    lignes = []
    for e in journal:
        a = aff.get(e.get("apprenant", ""), {})
        lignes.append([
            a.get("code", e.get("apprenant", "")), e.get("horodatage", ""),
            e.get("concept", ""), e.get("chapitre", ""), e.get("exercice", ""),
            1 if e.get("verdict") == "reussite" else 0,
            e.get("categorie", ""), 1 if e.get("silencieuse") else 0,
            1 if e.get("hors_delai") else 0,
            (e.get("message_ghc") or "")[:200].replace("\n", " "),
        ])
    return (["code", "horodatage", "concept", "chapitre", "activite", "reussite",
             "categorie_erreur", "erreur_silencieuse", "hors_delai",
             "message_compilateur"], lignes)


def table_concepts(etat, aff):
    """Une ligne par apprenant et par concept : l'unite d'analyse principale."""
    lignes = []
    for ident, ap in etat["apprenants"].items():
        a = aff.get(ident, {})
        code = a.get("code", ident)
        concepts = set(ap.get("etats", {})) | set(ap.get("corpus", {}))
        for cid in sorted(concepts):
            corpus = ap.get("corpus", {}).get(cid, [])
            ecartes = ap.get("ecartes", {}).get(cid, [])
            aides = sum(v for k, v in ap.get("aides", {}).items()
                        if k.split("/")[0] == cid)
            echecs = sum(v for k, v in ap.get("echecs", {}).items()
                         if k.split("/")[0] == cid)
            verifs = [v for k, v in ap.get("verifications", {}).items()
                      if k.split("/")[0] == cid]
            lignes.append([
                code, cid, ap.get("etats", {}).get(cid, ""),
                len(corpus), len(ecartes),
                ap.get("reemplois", {}).get(cid, 0),
                aides, echecs,
                1 if cid in ap.get("generalisations", {}) else 0,
                len(verifs),
                sum(1 for v in verifs if v.get("statut") == "non expliquee"),
                ap.get("stabilite", {}).get(cid, ""),
            ])
    return (["code", "concept", "etat_final", "solutions_au_corpus",
             "solutions_ecartees", "reemplois", "etayages", "echecs_compilation",
             "generalisation_ecrite", "verifications_demandees",
             "verifications_non_expliquees", "dernier_compte_alignement"], lignes)


def table_generalisations(etat, aff):
    lignes = []
    for ident, ap in etat["apprenants"].items():
        code = aff.get(ident, {}).get("code", ident)
        for cid, texte in ap.get("generalisations", {}).items():
            t = texte if isinstance(texte, str) else texte.get("texte", "")
            lignes.append([code, cid, len(t.split()), t.replace("\n", " \\n ")])
    return (["code", "concept", "mots", "texte_generalisation"], lignes)


def table_solutions(etat, aff):
    """Corpus et solutions ecartees, avec la forme canonique calculee par le
    moteur : c'est la trace qui permet de reverifier un alignement apres coup."""
    lignes = []
    for ident, ap in etat["apprenants"].items():
        code = aff.get(ident, {}).get("code", ident)
        for cid, corpus in ap.get("corpus", {}).items():
            for x in corpus:
                lignes.append([code, cid, x.get("nom", ""), "admise",
                               x.get("base", ""), x.get("canon", ""),
                               x.get("code", "").replace("\n", " \\n ")])
        for cid, ecartes in ap.get("ecartes", {}).items():
            for x in ecartes:
                nom, motif = (x + ["", ""])[:2] if isinstance(x, list) else (x, "")
                code_src = x[2] if isinstance(x, list) and len(x) > 2 else ""
                lignes.append([code, cid, nom, "ecartee: " + str(motif), "", "",
                               str(code_src).replace("\n", " \\n ")])
    return (["code", "concept", "activite", "statut", "cas_de_base",
             "forme_canonique", "code_soumis"], lignes)


def table_etayages(etat, aff):
    lignes = []
    for ident, ap in etat["apprenants"].items():
        code = aff.get(ident, {}).get("code", ident)
        for cle, n in ap.get("aides", {}).items():
            cid, _, act = cle.partition("/")
            lignes.append([code, cid, act, n,
                           ap.get("derniere_erreur", {}).get(cle, "")])
    return (["code", "concept", "activite", "niveaux_pris",
             "derniere_categorie_erreur"], lignes)


def table_verifications(etat, aff):
    lignes = []
    for ident, ap in etat["apprenants"].items():
        code = aff.get(ident, {}).get("code", ident)
        for cle, v in ap.get("verifications", {}).items():
            cid, _, act = cle.partition("/")
            lignes.append([code, cid, act, v.get("statut", ""),
                           v.get("justes", ""), len(v.get("questions", [])),
                           "; ".join(v.get("signaux", []))])
    return (["code", "concept", "activite", "statut", "reponses_justes",
             "questions_posees", "indices_de_declenchement"], lignes)


CODEBOOK = """# Codebook des donnees d'experimentation

Un enregistrement anonymise par ligne. La colonne `code` est le code
d'anonymat ; la correspondance avec les apprenants reste dans
`affectation.csv`, conserve hors du jeu de donnees.

## participants.csv
Une ligne par apprenant. Variables d'affectation experimentale
(`groupe_ordre`, `groupe_obligation`, `groupe_hors_forme`) et totaux de
session. Sert aux analyses entre groupes et aux statistiques descriptives.

## soumissions.csv
Une ligne par soumission compilee, dans l'ordre chronologique. Sert a la
courbe d'erreurs par chapitre, au releve des erreurs silencieuses, au calcul
des delais entre soumissions et a toute analyse de processus.

## concepts.csv
Une ligne par apprenant et par concept : c'est l'unite d'analyse principale
des modeles a effets mixtes, l'apprenant et le concept servant d'effets
aleatoires.

## generalisations.csv
Le texte de chaque generalisation produite. Sert au codage qualitatif de la
correction et de la portee de l'abstraction obtenue.

## solutions.csv
Chaque solution admise ou ecartee, avec sa forme canonique. Permet de
reverifier apres coup tout alignement, et de recalculer un compte de points
de variation si la definition en change.

## etayages.csv
Niveaux d'etayage pris par concept et par activite, avec la categorie de la
derniere erreur. Sert a l'analyse de la demande d'aide.

## verifications.csv
Chaque demande d'explication, son statut et les indices qui l'ont declenchee.
Sert a estimer le taux de declenchement et le taux d'explications non
concordantes.
"""


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        return
    etat = json.load(open(sys.argv[1], encoding="utf-8"))
    journal = lire_journal(sys.argv[2])
    aff = lire_affectation(sys.argv[3])
    dossier = sys.argv[4]
    os.makedirs(dossier, exist_ok=True)

    print("Export vers %s" % dossier)
    for nom, fabrique, args in (
            ("participants.csv", table_participants, (etat, aff)),
            ("soumissions.csv", table_soumissions, (journal, aff)),
            ("concepts.csv", table_concepts, (etat, aff)),
            ("generalisations.csv", table_generalisations, (etat, aff)),
            ("solutions.csv", table_solutions, (etat, aff)),
            ("etayages.csv", table_etayages, (etat, aff)),
            ("verifications.csv", table_verifications, (etat, aff))):
        entetes, lignes = fabrique(*args)
        ecrire(dossier, nom, entetes, lignes)

    with open(os.path.join(dossier, "codebook.md"), "w", encoding="utf-8") as f:
        f.write(CODEBOOK)
    print("  %-28s" % "codebook.md")

    n = len(etat["apprenants"])
    acquis = [sum(1 for v in ap.get("etats", {}).values() if v == "acquired")
              for ap in etat["apprenants"].values()]
    print("\n%d apprenants, %d soumissions, %.1f concepts acquis en moyenne"
          % (n, len(journal), statistics.mean(acquis) if acquis else 0))


if __name__ == "__main__":
    main()
