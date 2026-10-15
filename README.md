# FPTutor-Shell

Coquille d'écriture de tuteurs intelligents pour l'abstraction ascendante en
programmation fonctionnelle. Un tuteur sert des exercices concrets, évalue les
soumissions par le compilateur réel du langage, compare les solutions d'un même
apprenant terme à terme, et n'ouvre la phase de généralisation que lorsque ce
qui varie entre ses solutions ne bouge plus.

La coquille est indépendante du langage au sein du paradigme fonctionnel. Un
tuteur est engendré pour un nouveau langage en écrivant un fournisseur de
langage et un jeu d'ancrages, sans toucher à la couche de politique ni à
l'anti-unificateur.

## Instances

| Instance | Langage | État |
|---|---|---|
| `exemples/ocamltutor` | OCaml 4.14 | servie à l'automne 2026 dans INF6120 |
| `exemples/rackettutor` | Racket 8.x | troisième instanciation, sous protocole |
| `exemples/pytutor` | Python | fournisseur de démonstration |
| `exemples/haskelltutor` | Haskell | quatrième instanciation, analyse héritée |

## Arborescence

    noyau.py              politique, alignement, étayage, état de l'apprenant
    remontee.py           anti-unification des solutions
    serveur.py            service HTTP, API, contrats par concept
    etudiant.html         interface apprenant
    enseignant.html       console enseignante
    obligations.py        induction des obligations par ablation
    normalisation*.py     vocabulaire commun des termes
    simulateur.py         cohortes synthétiques
    ablations.py          ablations de la politique
    fptutor-shell/        atelier : creer_tuteur.py, gabarits, banc_essai.py
    exemples/<instance>/  fournisseur, ancrages, référentiel, scripts de l'instance
    outils/verifier.sh    batterie de vérification d'une instance
    outils/pousser.sh     mise à jour du dépôt en une commande

## Démarrage

Python 3.10 ou plus, et le compilateur du langage visé. Depuis la racine :

    outils/verifier.sh exemples/ocamltutor language_ml cas_ml.json
    TUTOR_DIR=exemples/ocamltutor TUTOR_LANGUAGE=language_ml PORT=8081 python3 serveur.py

Apprenant sur `http://localhost:8081/`, console sur `/enseignant`.

## Documents

- `GUIDE_STAGIAIRE.md` : prise en main et travaux à mener pour l'expérimentation
- `CONFIGURATION.md` : où se règlent les exercices, l'aide et les politiques
- `LISEZMOI_v2.md`, `LISEZMOI_v3.md` : corrections successives de la coquille
- `exemples/rackettutor/RAPPORT_instanciation.md` : ce que coûte une instanciation
- `exemples/ocamltutor/SUIVI_DEPLOIEMENT.md` : déploiement de l'instance servie
- `docs/CONCORDANCE_LABO.md` : concordance des ancrages avec le laboratoire du cours
- `docs/SEANCE2.md` : plan de la deuxième séance et questionnaire
- `docs/OPTIONS_EXPOSITION.md` : les deux options d'exposition au schéma, à trancher avec l'enseignant
- `docs/FICHE_SALLE.md` et `docs/GRILLE_RELEVE.md` : conduite d'une séance

## Données

Aucune donnée d'apprenant n'est versionnée. `etat.json`, `journal.jsonl` et les
exports sont exclus par `.gitignore`. L'inscription se fait par pseudonyme et le
serveur refuse un pseudonyme ressemblant à un nom, à une adresse ou à un code
permanent.
