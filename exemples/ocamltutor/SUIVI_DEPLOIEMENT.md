# Séance de suivi : intégrée au tuteur, pilotée par l'enseignant

## Ce qui change

Le suivi n'est plus un service séparé. Il est chargé par le tuteur lui-même, dans
le même processus, par le point d'extension de la coquille : un seul service, une
seule adresse, aucune entrée de proxy supplémentaire, aucune variable à régler.

L'enseignant le pilote entièrement depuis sa console, dans un volet « Séance de
suivi » :

- **Aperçu étudiant**, qui ouvre exactement ce que verra un étudiant, suivi
  masqué ou non. L'aperçu est signalé par un bandeau, et rien de ce qui y est
  fait n'entre dans les résultats ni dans le journal.
- **Rendre visible maintenant** et **Masquer maintenant**.
- **Visible à partir de, jusqu'à**, pour une fenêtre programmée qui s'ouvre et se
  ferme seule.
- La liste des participants en direct, avec leurs exercices faits, leurs
  réemplois et leur questionnaire.

Côté étudiant, le suivi est invisible tant que l'enseignant ne l'a pas rendu
visible. Dès qu'il l'est, un bandeau apparaît au bas de la page habituelle
d'OCamlTutor, « La séance de suivi est ouverte », avec un bouton « Commencer le
suivi ». L'étudiant n'a aucune adresse à retenir.

## Fichiers, dans FPTutor/ocamltutor/

    extension.py              déclare l'extension à la coquille
    suivi_serveur.py          la logique du suivi : items, mesure, questionnaire
    suivi.html                la page du suivi, servie sous /suivi
    console_extension.html    le volet de la console enseignante
    etudiant_extension.html   le bandeau de la page étudiante
    normalisation_ml.py       à remplacer : il analysait mal un booléen en argument

Et, à la racine de FPTutor, `serveur.py` dans sa dernière version, qui porte le
point d'extension.

## Lancement

Rien de plus que le tuteur habituel :

    cd FPTutor
    OCAML_BIN=/chemin/absolu/vers/4.14.2/bin/ocaml \
    TUTOR_DIR=ocamltutor TUTOR_LANGUAGE=language_ml \
    PORT=8081 python3 serveur.py

Adresses, derrière le proxy existant :

    étudiants     https://gdac.uqam.ca/ocamltutor/
    console       https://gdac.uqam.ca/ocamltutor/enseignant
    suivi         https://gdac.uqam.ca/ocamltutor/suivi

## Protection

Aucun jeton. Les routes qui rendent le suivi visible et qui servent l'aperçu sont
sous `/api/ext/admin/` : il suffit de les protéger au proxy avec la même
authentification que la console enseignante, ce qui empêche un étudiant d'ouvrir
le suivi ou d'en voir les exercices en avance.

    <Location /ocamltutor/enseignant>
        AuthType Basic
        AuthName "OCamlTutor, enseignants"
        AuthUserFile /etc/apache2/ocamltutor.htpasswd
        Require valid-user
    </Location>
    <Location /ocamltutor/api/ext/admin>
        AuthType Basic
        AuthName "OCamlTutor, enseignants"
        AuthUserFile /etc/apache2/ocamltutor.htpasswd
        Require valid-user
    </Location>

Le navigateur de l'enseignant, authentifié pour la console, l'est aussi pour le
volet, puisque le domaine et le royaume sont les mêmes.

## Fichiers produits

`suivi_config.json`, la visibilité et la fenêtre ; `suivi_etat.json`, les
résultats par pseudonyme, les aperçus étant rangés à part ; `suivi_journal.jsonl`,
toutes les actions des étudiants, sans les aperçus.

## Vérifié, en un seul processus, avec le vrai compilateur

Volet inséré dans la console, bandeau dans la page étudiante, page du suivi
servie par le tuteur. Suivi masqué par défaut. Aperçu utilisable suivi masqué :
premier exercice servi, soumission évaluée, et aucun participant ni ligne de
journal créés. Étudiant refusé tant que le suivi est masqué, admis une fois
rendu visible. Le tuteur principal répond normalement.

## Ce qui reste disponible, sans être nécessaire

`suivi_serveur.py` peut encore tourner seul, avec `suivi_admin.html`, si l'on
voulait un jour séparer le suivi du tuteur. Ce n'est plus la configuration
recommandée.
