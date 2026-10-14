# RacketTutor

Troisième instance de FPTutor-Shell, engendrée par `creer_tuteur.py rkt
rackettutor --interprete racket --extension .rkt --titre RacketTutor`, puis
complétée sous protocole. Contenu pédagogique identique à OCamlTutor. Le
déroulement et les résultats sont dans `RAPPORT_instanciation.md`, les
données brutes dans `mesures/`.

## Fichiers

| fichier | rôle |
|---|---|
| `language_rkt.py` | fournisseur : exécution, gabarit de test, catégorisation, textes d'étayage, charpente, réemploi |
| `normalisation_rkt.py` | lecture des s-expressions, structures et accesseurs, rendu en vocabulaire commun |
| `activities_rkt.py` | neuf ancrages et six réemplois (laboratoire 05 d'INF6120) |
| `referentiel.json` | concepts, familles, obligations |
| `compiler_references.py` | solutions de référence, exécutées par Racket |
| `cas_rkt.json`, `cas_rkt_option.json` | jeux de cas du banc d'essai |
| `essai_a_blanc.py` | session complète par le noyau, avec sondes de mesure et d'étayage |
| `sonde_http.py` | essai de bout en bout par HTTP, dont la condition de stabilité |

## Lancer

Racket 8.x doit être installé (`racket` dans le PATH, ou `RACKET_BIN`).
Depuis la racine de la coquille :

    TUTOR_DIR=exemples/rackettutor TUTOR_LANGUAGE=language_rkt PORT=8093 python3 serveur.py

Apprenant sur http://localhost:8093/, console sur http://localhost:8093/enseignant.
