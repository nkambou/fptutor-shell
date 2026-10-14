# FPTutor-Shell, version 2 : base pour une nouvelle instanciation

Coquille à jour de toutes les corrections apportées lors de l'instanciation
OCaml. C'est la base à utiliser pour RacketTutor, et pour toute instance future.

## Ce qui a changé depuis la version 1

Sept modifications, détaillées dans `LISEZMOI_patches.md` : titre, langue par
défaut et compilateur venus du fournisseur ; page étudiante qui ne force plus
l'anglais ; inscription par pseudonyme, sans donnée nominative ; point
d'extension pour les instruments d'une étude ; validation des familles par le
fournisseur dans la console.

## Pour créer une instance

    cd fptutor-shell
    python3 creer_tuteur.py

Le gabarit `gabarit_language.py` liste les éléments à écrire, dont les attributs
facultatifs `titre`, `langue_defaut`, `compilateur` et `REFERENCES`. Le banc
d'essai `banc_essai.py` vérifie ensuite le fournisseur sur un jeu de cas.

## Exemples

`exemples/ocamltutor` et `exemples/pytutor` sont deux instances complètes, à lire
comme modèles. OCamlTutor est la plus proche de ce qu'il faudra pour Racket :
analyseur et normalisateur propres, familles validées par la console, solutions
de référence compilées, banc passé.

## À mesurer pendant l'instanciation

Pour l'article sur la généricité : le temps passé, les lignes écrites par élément
du fournisseur, et toute modification forcée de la coquille, consignée comme un
résultat au même titre que les sept précédentes.
