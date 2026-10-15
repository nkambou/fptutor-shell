# HaskellTutor

Quatrième instance de FPTutor-Shell, et retour au langage dont la coquille est
issue. L'analyse n'est pas réécrite : `language_hs.py` enveloppe
`normalisation.py`, hérité de HaskellTutor, et traduit son vocabulaire vers
celui du cadre. Résultats et coût mesuré dans `RAPPORT_instanciation.md`.

| Fichier | Rôle |
|---|---|
| `language_hs.py` | fournisseur : exécution, gabarit de test, catégorisation, enveloppe de l'analyse |
| `activities_hs.py` | cinq ancrages de la famille du pli à droite, deux réemplois |
| `referentiel.json` | concept `liste-pli`, famille `F-liste`, trois points de variation |
| `compiler_references.py` | solutions de référence, exécutées par `runghc` |
| `cas_hs.json` | jeu de cas du banc d'essai |
| `essai_a_blanc.py` | session complète par le noyau |

## Lancer

GHC doit être installé, `runghc` dans le PATH ou donné par `GHC_BIN`.

    TUTOR_DIR=exemples/haskelltutor TUTOR_LANGUAGE=language_hs PORT=8082 python3 serveur.py

## Vérifier

    outils/verifier.sh exemples/haskelltutor language_hs cas_hs.json
