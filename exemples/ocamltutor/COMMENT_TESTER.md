# Comment éprouver CamlTutor sans compilateur local

Trois voies. La première fonctionne sur votre portable dès maintenant, sans rien
installer. Les deux autres donnent un environnement réel, et l'une d'elles sera
de toute façon nécessaire pour la séance de novembre.

## 1. Compilateur simulé, tout de suite

`faux_compilateur.py` se substitue à l'interprète : même interface en ligne de
commande, même code de retour, même forme de message d'erreur.

    cd FPTutor/camltutor
    chmod +x faux_compilateur.py
    export OCAML_BIN=$PWD/faux_compilateur.py
    python3 verifier_environnement.py
    python3 essai_a_blanc.py
    python3 valider_familles_ml.py

**Ce que cela éprouve réellement**, et ce n'est pas peu : l'analyse et la
normalisation du code, qui sont du Python et ne dépendent d'aucun compilateur ;
l'admission au corpus, donc la mise à l'écart d'une solution correcte mais non
comparable, avec son motif ; l'anti-unification et le compte de points de
variation ; les trois conjonctions de la porte, donc le refus sur alignement
instable puis le déclenchement sur stabilité ; l'atelier d'abstraction et ses
trois niveaux d'étayage ; la détection du réemploi ; la progression du concept.
Autrement dit toute la politique, qui est ce que vous voulez éprouver avant les
écrans.

**Ce que cela n'éprouve pas**, et qu'il faut savoir : rien n'est exécuté. Le faux
compilateur ne détecte ni erreur de type, ni résultat faux, ni boucle infinie. Il
simule deux cas seulement, la souche non complétée et le filtrage non exhaustif.
Aucune mesure destinée à publication ne doit en provenir, et il ne doit jamais
être en place pendant une séance avec des étudiants. La règle simple : si
`OCAML_BIN` pointe vers ce fichier, vous êtes en essai, pas en collecte.

## 2. Un poste du département

Le laboratoire 01 donne déjà la procédure pour les salles du LAMISS, où le
dossier personnel est lent :

    export OPAMROOT=/tmp/$(whoami)-opam/
    opam init
    opam switch create 4.14.2
    eval $(opam env)

À répéter à chaque connexion, ce que le laboratoire signale aussi. C'est la voie
la plus proche de l'environnement des étudiants, et donc la bonne pour vérifier
les messages du compilateur que `categorise` projette sur les catégories
d'étayage.

## 3. Un conteneur

Si Docker est disponible sur une machine quelconque :

    docker run --rm -it -v "$PWD":/w -w /w ocaml/opam:debian-ocaml-4.14 bash
    python3 verifier_environnement.py

L'image porte la version du cours, et rien n'est installé sur l'hôte. C'est la
solution que je retiendrais pour le serveur de novembre, parce qu'elle fige la
version du compilateur et se reproduit à l'identique.

## Ce que je vérifierais dans cet ordre

D'abord la politique, avec le compilateur simulé, sur votre portable : c'est là
que se trouvent les décisions dont dépend l'étude. Ensuite les écrans, qui ne
demandent pas non plus de compilateur. Et seulement à la fin, sur un poste du
département ou dans un conteneur, la compilation réelle et les messages d'erreur,
qui sont la seule partie où la version compte.
