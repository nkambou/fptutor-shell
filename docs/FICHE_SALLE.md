# Fiche de salle

À remplir avant la séance, à imprimer, à garder sous les yeux. Une page.

## Coordonnées

| | |
|---|---|
| Salle et date | |
| Adresse étudiante | `https://gdac.uqam.ca/ocamltutor/` |
| Console enseignante | `https://gdac.uqam.ca/ocamltutor/enseignant` |
| Serveur, machine et compte | |
| Port | 8081 |
| Cohorte | |
| Téléphones : enseignant, auxiliaire, Roger Nkambou | |

## Avant l'arrivée des étudiants

- [ ] `COLLECTE_EN_COURS` créé dans le répertoire de l'instance
- [ ] Serveur lancé, et la page sert bien le titre OCamlTutor
- [ ] Aucun bandeau « MODE ESSAI » : `curl -s http://localhost:8081/api/ext/statut` rend `"compilateur_simule": false`
- [ ] Une inscription d'essai faite, puis une soumission fausse et une juste
- [ ] Console ouverte sur un second écran, contrats vérifiés (onglet Contrats, concept
      `arbre-pli`) : assistance `on-request`, abstraction `discovery`, régime `free`,
      séquence `free`, off_form `explain_and_continue`, vérification `never`, délai 0
- [ ] Phase 1 : `BASCULE_FAITE = False` dans `exemples/ocamltutor/activities_ml.py`
- [ ] Adresse écrite au tableau

## Relance

    cd FPTutor
    ./relancer.sh --garder          # garde l'état, donc les dossiers des étudiants

Jamais de remise à zéro en séance. Le journal du serveur est dans `tuteur.log`.

## Les trois pannes probables

**Bandeau « MODE ESSAI ».** Le serveur a été lancé avec `OCAML_BIN` pointant sur
le substitut. L'environnement d'un processus est figé à son démarrage, donc il
faut l'arrêter, corriger, relancer :

    unset OCAML_BIN && eval $(opam env) && ./relancer.sh --garder

**Un étudiant ne retrouve pas son dossier.** Son pseudonyme diffère d'un
caractère. Son identifiant à quatre chiffres est dans la console, qui permet de
le lui redonner.

**Le service ne répond plus.** Relancer avec `--garder` : l'état est sur disque
et les dossiers sont conservés. Si la relance échoue en moins de trois minutes,
le laboratoire reprend son cours, les étudiants continuent dans leur éditeur, et
on reporte le créneau.

## Bascule de phase, la veille du laboratoire 06

- [ ] Fenêtre de la phase 1 fermée à l'heure annoncée aux apprenants
- [ ] Export et sauvegarde faits avant toute modification
- [ ] Trois exercices différés ajoutés : passer `BASCULE_FAITE = True` dans
      `exemples/ocamltutor/activities_ml.py` (une seule ligne). S'ajoutent, dans cet
      ordre, `bintree_count_internal_nodes_fold`, `bintree_collect_internal_nodes_fold`
      et `bintree_all_positive` ; le suivi (séance 2) sert les mêmes
- [ ] Batterie de vérification relancée
- [ ] `./relancer.sh --garder`, qui conserve l'état et les dossiers
- [ ] Un dossier déjà constitué vérifié dans la console : le nouvel exercice est servi, l'historique est intact
- [ ] Heure de la présentation de `fold_tree` en classe notée, à l'heure près
- [ ] Corrigé de la dernière section NON publié : il paraît à la fin du second créneau
- [ ] Option d'exposition retenue vérifiée dans `OPTIONS_EXPOSITION.md`, et libellé de la première question du questionnaire conforme

## Après la séance

- [ ] Export des données, hors du dépôt
- [ ] Sauvegarde de `etat.json` et `journal.jsonl` dans `sauvegardes/`
- [ ] `COLLECTE_EN_COURS` conservé jusqu'à la sauvegarde vérifiée
- [ ] Notes du relevé mises au propre le jour même
