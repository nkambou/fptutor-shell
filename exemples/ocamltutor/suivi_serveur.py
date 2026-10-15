#!/usr/bin/env python3
"""Seance de suivi d'OCamlTutor : vingt minutes, trois items, un questionnaire.

    TUTOR_DIR=ocamltutor TUTOR_LANGUAGE=language_ml SUIVI_JETON=... \\
        python3 suivi_serveur.py          puis http://localhost:8083/
                                               http://localhost:8083/admin

Ce serveur est une couche d'etude, a cote de la coquille et non dedans : il
reutilise le fournisseur OCaml et le noyau pour l'execution et la detection du
reemploi, et ne modifie ni l'un ni l'autre.

Trois principes.

**Ferme par defaut.** Les etudiants n'y accedent qu'a l'ouverture du suivi, soit
automatiquement a la date et l'heure programmees, soit manuellement par un
administrateur, enseignant ou chercheur, muni du jeton. Hors de la fenetre, la
page dit que le suivi n'est pas ouvert, et rien d'autre.

**Rien ne rappelle le schema.** L'amorce ne porte que le type et les valeurs
d'essai. Ni fold_tree, ni la generalisation ecrite au laboratoire, ni le corpus
des solutions, ni l'indicateur de points de variation. Les enonces ne renvoient
pas au laboratoire. L'aide porte sur l'erreur commise, jamais sur le pli.

**La mesure est fixee d'avance.** Un item compte comme reemploi lorsque la
solution est correcte et que la fonction demandee ne contient aucun appel
recursif explicite. Une forme non analysable compte comme non-reemploi et est
signalee, faute de quoi un defaut de couverture du normalisateur deviendrait un
faux positif sur la mesure principale.
"""
import json, os, sys, time, urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = ICI                      # la coquille : le premier parent qui porte noyau.py
while not os.path.exists(os.path.join(RACINE, "noyau.py")) and RACINE != "/":
    RACINE = os.path.dirname(RACINE)
for d in (RACINE, ICI):
    if d not in sys.path:
        sys.path.insert(0, d)
os.environ.setdefault("TUTOR_DIR", ICI)
os.environ.setdefault("TUTOR_LANGUAGE", "language_ml")

import noyau as N
import activities_ml as A

PORT = int(os.environ.get("PORT", "8083"))
JETON = os.environ.get("SUIVI_JETON", "")
CONFIG = os.path.join(ICI, "suivi_config.json")
ETAT = os.path.join(ICI, "suivi_etat.json")
JOURNAL = os.path.join(ICI, "suivi_journal.jsonl")

# ------------------------------------------------------------- items du suivi
# Enonces neutres : aucun renvoi au laboratoire, aucune suggestion de strategie.
ENONCES = {
    "bintree_count_even": "Un arbre binaire sur les entiers : combien de ses nœuds "
                          "internes portent un entier pair ? "
                          "Toute solution correcte est acceptée.",
    "bintree_min": "Un arbre binaire sur les entiers : donnez le plus petit entier "
                   "porté par un nœud interne, ou None si l'arbre est une feuille. "
                   "Toute solution correcte est acceptée.",
    "bintree_all_positive": "Le même type d'arbre : tous les entiers portés par ses "
                            "nœuds internes sont-ils strictement positifs ? "
                            "Toute solution correcte est acceptée.",
    "ubtree_count_bin": "On considère un arbre dont chaque nœud a un ou deux "
                        "sous-arbres. Combien a-t-il de nœuds à deux sous-arbres ? "
                        "Toute solution correcte est acceptée.",
}
# Gradation voulue : meme forme que le laboratoire, puis type du resultat change,
# puis type de l'arbre change. bintree_min reste disponible mais n'est plus servi :
# la manipulation d'une option y ajoutait une difficulte etrangere au schema.
ORDRE = ["bintree_count_even", "bintree_all_positive", "ubtree_count_bin"]


def items():
    table = {}
    for acts in A.REEMPLOIS.values():
        for (nom, _enonce, sig, amorce, tests) in acts:
            if nom in ENONCES:
                table[nom] = dict(id=nom, enonce=ENONCES[nom], signature=sig,
                                  amorce=amorce, tests=tests)
    return [table[n] for n in ORDRE if n in table]


# Question d'exposition : son libelle depend de l'option retenue pour l'enonce du
# laboratoire 05, decrite dans docs/OPTIONS_EXPOSITION.md. Option A, la derniere
# section reste dans l'enonce et nomme fold_tree ; option B, elle est reportee au
# laboratoire suivant et rien ne la nomme. La valeur se donne au lancement :
#   SUIVI_OPTION_EXPOSITION=B
OPTION_EXPOSITION = (os.environ.get("SUIVI_OPTION_EXPOSITION") or "A").upper()[:1]
if OPTION_EXPOSITION not in ("A", "B"):
    OPTION_EXPOSITION = "A"

QUESTIONS_EXPOSITION = {
    "A": {"libelle": "Avant de faire ces exercices, aviez-vous lu la dernière section "
                     "de l'énoncé du laboratoire 05, celle qui demande fold_tree ?",
          "choix": [["oui", "oui"], ["non", "non"], ["ne_sait_pas", "je ne sais plus"]]},
    "B": {"libelle": "Avant de faire ces exercices, aviez-vous déjà rencontré une "
                     "fonction qui prend en paramètres une valeur de départ et une "
                     "opération, et qui parcourt l'arbre à votre place ?",
          "choix": [["oui_cours", "oui, dans ce cours"], ["oui_ailleurs", "oui, ailleurs"],
                    ["non", "non"], ["ne_sait_pas", "je ne sais plus"]]},
}

RESSOURCES = [["doc_ocaml", "la documentation d'OCaml"],
              ["notes_labo", "les notes ou l'énoncé du laboratoire"],
              ["condisciple", "un ou une condisciple"],
              ["assistant", "un assistant conversationnel"],
              ["web", "une recherche sur le web"],
              ["aucune", "aucune"]]

# L'aide porte sur l'erreur, jamais sur le schema.
AIDE = {
    "syntax": ["Le compilateur s'arrête sur la forme du code : relisez la ligne "
               "qu'il indique.",
               "Vérifiez les parenthèses et la flèche de chaque cas du filtrage."],
    "unknown-name": ["Un nom n'est pas connu du compilateur : le message le désigne.",
                     "Vérifiez l'orthographe et que chaque fonction employée est "
                     "définie avant son usage."],
    "incompatible-types": ["Deux types ne concordent pas : le message indique "
                           "lesquels.",
                           "Regardez ce que rend chaque cas : tous doivent rendre "
                           "le même type."],
    "missing-base-case": ["Un cas du type n'est pas traité.",
                          "Énumérez les constructeurs du type et vérifiez que "
                          "chacun a son cas."],
    "wrong-result": ["Le code s'exécute mais le résultat diffère : essayez-le sur "
                     "le plus petit arbre possible.",
                     "Vérifiez la valeur rendue pour une feuille, puis pour un seul "
                     "nœud."],
    "defaut": ["Relisez l'énoncé et la signature demandée.",
               "Essayez votre fonction sur les valeurs d'essai fournies."],
}

# --------------------------------------------------------------- persistance
def lire(chemin, defaut):
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    return defaut


def ecrire(chemin, d):
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


APERCU_EN_COURS = [False]


def journaliser(evenement, **champs):
    if APERCU_EN_COURS[0]:
        return
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(ts=datetime.now().isoformat(timespec="seconds"),
                                evenement=evenement, **champs),
                           ensure_ascii=False) + "\n")


def config():
    return lire(CONFIG, {"ouvert_manuellement": False, "debut": None, "fin": None,
                         "duree_min": 20, "cohorte": "INF6120-A26"})


def ouvert():
    """Ouvert si l'administrateur l'a ouvert, ou si l'on est dans la fenetre
    programmee. Ferme par defaut."""
    c = config()
    if c.get("ferme_force"):
        return False, "fermé par l'administrateur"
    if c.get("ouvert_manuellement"):
        return True, "ouvert par l'administrateur"
    maintenant = datetime.now()
    try:
        deb = datetime.fromisoformat(c["debut"]) if c.get("debut") else None
        fin = datetime.fromisoformat(c["fin"]) if c.get("fin") else None
    except ValueError:
        return False, "fenêtre mal définie"
    if deb and maintenant >= deb and (not fin or maintenant <= fin):
        return True, "fenêtre programmée"
    if deb and maintenant < deb:
        return False, "ouverture prévue le %s" % deb.strftime("%d/%m à %H:%M")
    return False, "le suivi n'est pas ouvert"


def inscrits_seance_principale():
    """Pseudonymes inscrits au tuteur lors de la seance du laboratoire 05.

    Le suivi n'admet qu'eux : c'est le pseudonyme qui relie les deux seances, et
    une trace de suivi sans seance principale ne mesure pas une reutilisation.
    La comparaison ignore la casse et les espaces en bordure."""
    try:
        e = N.charger_etat()
    except Exception:
        return set()
    return {(ap.get("nom") or "").strip().casefold()
            for ap in (e.get("apprenants") or {}).values() if ap.get("nom")}


def _defs(code):
    """Definitions de premier niveau : nom -> (parametres, rec, corps)."""
    import normalisation_ml as NML
    try:
        return {d[1]: (d[2], d[3], d[4]) for d in NML.P(NML.lex(code)).parse_program()
                if d[0] == "def"}
    except Exception:
        return None


def _parcourir(t):
    if isinstance(t, tuple):
        yield t
        for x in t[1:]:
            yield from _parcourir(x)
    elif isinstance(t, list):
        for x in t:
            yield from _parcourir(x)


def _appelle(corps, nom):
    return any(n[0] == "var" and len(n) > 1 and n[1] == nom for n in _parcourir(corps))


def _filtre_un_arbre(corps):
    """Le corps filtre-t-il sur les constructeurs d'un type d'arbre ?"""
    motifs = repr(corps)
    return any(c in motifs for c in ("'Leaf'", "'Node'", "'UbLeaf'", "'Un'", "'Bin'"))


def reemploi(nom, code):
    """Rend (reemploi, forme, pli_arbre).

    Une solution compte comme reemploi si elle est correcte, si la fonction
    demandee ne s'appelle pas elle-meme, et si elle passe une fonction en argument
    a une abstraction : une lambda, un operateur prefixe, ou une fonction nommee.
    Sans cette derniere condition, une enveloppe autour d'une recursion ecrite a
    la main, du type « let f a = aux a », serait prise a tort pour un reemploi.

    pli_arbre precise si l'abstraction employee est un pli defini sur l'arbre
    lui-meme, qui est le schema vise, plutot qu'une fonction de bibliotheque.
    Une forme non analysable n'est jamais un reemploi."""
    defs = _defs(code)
    if not defs or nom not in defs:
        return False, "non analysable", False
    params, _rec, corps = defs[nom]
    if _appelle(corps, nom):
        return False, "recursion explicite", False
    for n in _parcourir(corps):
        if n[0] != "app":
            continue
        tete, args = n[1], n[2]
        fonctionnels = [a for a in args if isinstance(a, tuple) and (
            a[0] == "fun" or
            (a[0] == "var" and (str(a[1]).startswith("__op_") or a[1] in defs)))]
        if not fonctionnels:
            continue
        pli = False
        if tete[0] == "var" and tete[1] in defs:
            _p, rec, c = defs[tete[1]]
            pli = bool(rec) and _appelle(c, tete[1]) and _filtre_un_arbre(c)
        return True, ("pli sur l'arbre" if pli else "abstraction d'ordre superieur"), pli
    return False, "sans abstraction ni recursion propre", False


# -------------------------------------------------------------------- api
def api(chemin, p, corps):
    etat = lire(ETAT, {"apprenants": {}})
    its = items()
    # Apercu : l'enseignant voit exactement ce que verra l'etudiant, meme suivi
    # ferme. Les routes d'apercu sont sous /api/admin/, donc protegees comme
    # l'administration ; ce qui y est fait est range a part et n'entre jamais
    # dans les resultats.
    apercu = chemin.startswith("/api/admin/apercu/")
    if apercu:
        chemin = "/api/" + chemin[len("/api/admin/apercu/"):]
    cle_etat = "apercus" if apercu else "apprenants"
    APERCU_EN_COURS[0] = apercu
    etat.setdefault(cle_etat, {})

    if chemin == "/api/statut":
        o, motif = ouvert()
        c = config()
        return {"ouvert": o, "motif": motif, "duree_min": c.get("duree_min", 20),
                "option_exposition": OPTION_EXPOSITION,
                "question_exposition": QUESTIONS_EXPOSITION[OPTION_EXPOSITION],
                "ressources": RESSOURCES,
                "compilateur_simule": "faux_compilateur" in (os.environ.get("OCAML_BIN") or "")}

    # ------------------------------------------------------ administration
    if not apercu and chemin.startswith("/api/admin/"):
        # Aucun jeton par defaut : les routes d'administration sont protegees au
        # proxy, avec la meme authentification que la console enseignante, qui
        # est d'ou on les pilote. SUIVI_JETON reste disponible pour un
        # deploiement sans cette protection.
        if JETON and (corps or {}).get("jeton", p.get("jeton", [""])[0]) != JETON:
            return {"erreur": "jeton requis"}
        c = config()
        if chemin == "/api/admin/ouvrir":
            c.update(ouvert_manuellement=True, ferme_force=False)
            ecrire(CONFIG, c); journaliser("ouverture", par=corps.get("par", "admin"))
            return {"ok": True, "config": c}
        if chemin == "/api/admin/fermer":
            c.update(ouvert_manuellement=False, ferme_force=True)
            ecrire(CONFIG, c); journaliser("fermeture", par=corps.get("par", "admin"))
            return {"ok": True, "config": c}
        if chemin == "/api/admin/programmer":
            c.update(debut=corps.get("debut"), fin=corps.get("fin"),
                     ouvert_manuellement=False, ferme_force=False)
            ecrire(CONFIG, c)
            journaliser("programmation", debut=c["debut"], fin=c["fin"],
                        par=corps.get("par", "admin"))
            return {"ok": True, "config": c}
        if chemin == "/api/admin/etat":
            lignes = []
            for nom, ap in etat["apprenants"].items():
                lignes.append(dict(nom=nom, items=len(ap["resultats"]),
                                   reemplois=sum(1 for r in ap["resultats"].values()
                                                 if r.get("reemploi")),
                                   questionnaire=bool(ap.get("questionnaire")),
                                   debut=ap.get("debut")))
            o, motif = ouvert()
            return {"config": c, "ouvert": o, "motif": motif, "apprenants": lignes}
        return {"erreur": "route inconnue"}

    # ------------------------------------------------------------- apprenant
    o, motif = ouvert()
    if not o and not apercu:
        return {"ferme": True, "motif": motif}

    if chemin == "/api/entrer":
        nom = (corps.get("nom") or "").strip()
        if not apercu and nom and nom.casefold() not in inscrits_seance_principale():
            journaliser("entree_refusee", pseudonyme_saisi=nom)
            return {"erreur": "Ce pseudonyme n'a pas été utilisé lors de la séance "
                              "du laboratoire. Vérifiez l'orthographe : seul le "
                              "pseudonyme choisi à cette séance donne accès au suivi."}
        import re as _re
        if not nom:
            return {"erreur": "pseudonyme requis"}
        if "@" in nom or _re.search(r"[A-Za-z]{4}\s*\d{8}", nom) or _re.search(r"\d{6,}", nom):
            return {"erreur": "Ce pseudonyme ressemble à une adresse ou à un code "
                              "permanent : entrez le pseudonyme choisi à la séance "
                              "précédente."}
        ap = etat[cle_etat].setdefault(nom, {
            "debut": time.time(), "resultats": {}, "tentatives": {}, "aides": {},
            "debuts_item": {}, "questionnaire": None,
            "consentement": corps.get("consentement", True)})
        ecrire(ETAT, etat)
        if not apercu:
            journaliser("entree", apprenant=nom)
        return {"ok": True}

    ap = etat[cle_etat].get(corps.get("nom") if corps else p.get("nom", [""])[0])
    if not ap:
        return {"erreur": "inconnu : entrez d'abord votre pseudonyme"}
    nom = corps.get("nom") if corps else p.get("nom", [""])[0]

    if chemin == "/api/courant":
        faits = set(ap["resultats"])
        for it in its:
            if it["id"] not in faits:
                ap["debuts_item"].setdefault(it["id"], time.time())
                ecrire(ETAT, etat)
                return {"item": {k: it[k] for k in ("id", "enonce", "signature", "amorce")},
                        "rang": len(faits) + 1, "total": len(its),
                        "ecoule_min": int((time.time() - ap["debut"]) / 60)}
        return {"fini": True, "questionnaire_fait": bool(ap.get("questionnaire")),
                "recursion_main": [i for i, r in ap["resultats"].items()
                                   if r.get("correct") and not r.get("reemploi")]}

    if chemin == "/api/soumettre":
        it = next((x for x in its if x["id"] == corps.get("item")), None)
        if it is None:
            return {"erreur": "exercice inconnu"}
        code = corps["code"]
        ap["tentatives"][it["id"]] = ap["tentatives"].get(it["id"], 0) + 1
        v = N.evaluer(code, it["tests"])
        cat = N.LANGUE.categorise(v.get("message", ""), v.get("compile") and not v.get("reussite"))
        rep = {"correct": bool(v.get("reussite")), "categorie": cat,
               "message": (v.get("message") or "")[:600]}
        if v.get("reussite"):
            emp, forme, pli = reemploi(it["id"], code)
            ap["resultats"][it["id"]] = dict(
                correct=True, reemploi=emp, forme=forme, pli_arbre=pli,
                tentatives=ap["tentatives"][it["id"]],
                aides=ap["aides"].get(it["id"], 0),
                duree_s=int(time.time() - ap["debuts_item"].get(it["id"], time.time())))
        journaliser("soumission", apprenant=nom, item=it["id"],
                    correct=rep["correct"], categorie=cat,
                    reemploi=ap["resultats"].get(it["id"], {}).get("reemploi"),
                    forme=ap["resultats"].get(it["id"], {}).get("forme"),
                    tentative=ap["tentatives"][it["id"]], code=code)
        ap.setdefault("derniere_categorie", {})[it["id"]] = cat
        ecrire(ETAT, etat)
        return rep

    if chemin == "/api/passer":
        # Le temps est compte : un item non resolu peut etre laisse, il est alors
        # enregistre comme non resolu, ce qui est une donnee et non une perte.
        it = corps["item"]
        ap["resultats"][it] = dict(correct=False, reemploi=False, forme="non resolu",
                                   tentatives=ap["tentatives"].get(it, 0),
                                   aides=ap["aides"].get(it, 0),
                                   duree_s=int(time.time() - ap["debuts_item"].get(it, time.time())))
        journaliser("item_laisse", apprenant=nom, item=it)
        ecrire(ETAT, etat)
        return {"ok": True}

    if chemin == "/api/aide":
        it = corps["item"]
        n = ap["aides"].get(it, 0)
        if n >= 2:
            return {"texte": "Aucune autre indication n'est prévue pour cet exercice.",
                    "niveau": n}
        cat = ap.get("derniere_categorie", {}).get(it) or "defaut"
        texte = AIDE.get(cat, AIDE["defaut"])[n]
        ap["aides"][it] = n + 1
        journaliser("aide", apprenant=nom, item=it, niveau=n + 1, categorie=cat)
        ecrire(ETAT, etat)
        return {"texte": texte, "niveau": n + 1}

    if chemin == "/api/questionnaire":
        ap["questionnaire"] = dict(corps.get("reponses") or {},
                                   ts=datetime.now().isoformat(timespec="seconds"))
        journaliser("questionnaire", apprenant=nom, reponses=corps.get("reponses"))
        ecrire(ETAT, etat)
        return {"ok": True}

    return {"erreur": "route inconnue"}


ORIGINE = os.environ.get("SUIVI_ORIGINE", "")   # ex. http://localhost:8081 en local


class Handler(BaseHTTPRequestHandler):
    def _entetes_origine(self):
        # Utile seulement en local, quand la console enseignante et le suivi sont
        # servis sur deux ports. Derriere le proxy, les deux partagent l'origine.
        if ORIGINE:
            self.send_header("Access-Control-Allow-Origin", ORIGINE)
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._entetes_origine()
        self.end_headers()

    def _envoyer(self, code, corps, ctype="application/json"):
        if isinstance(corps, str):
            corps = corps.encode("utf-8")
        self.send_response(code)
        self._entetes_origine()
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self._envoyer(200, open(os.path.join(ICI, "suivi.html"), encoding="utf-8").read(), "text/html")
        if u.path == "/admin":
            return self._envoyer(200, open(os.path.join(ICI, "suivi_admin.html"), encoding="utf-8").read(), "text/html")
        if u.path.startswith("/api/"):
            return self._envoyer(200, json.dumps(api(u.path, urllib.parse.parse_qs(u.query), {}),
                                                 ensure_ascii=False))
        return self._envoyer(404, "introuvable", "text/plain")

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        n = int(self.headers.get("Content-Length", "0"))
        corps = json.loads(self.rfile.read(n) or b"{}")
        try:
            return self._envoyer(200, json.dumps(api(u.path, {}, corps), ensure_ascii=False))
        except Exception as e:
            return self._envoyer(500, json.dumps({"erreur": str(e)}))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if not JETON:
        print("Administration sans jeton : protegez /api/admin/ au proxy, avec la "
              "meme authentification que la console enseignante.")
    o, m = ouvert()
    print("Suivi OCamlTutor sur http://localhost:%d  (%s)" % (PORT, m))
    print("  apprenant      : http://localhost:%d/" % PORT)
    print("  administration : http://localhost:%d/admin" % PORT)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
