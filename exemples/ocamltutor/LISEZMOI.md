# mltutor — tuteur ml

Engendre par l'atelier FPTutor. Rien du shell n'a ete modifie.

## Dans l'ordre

**1. Ecrire `analyse` dans `language_ml.py`.** C'est le seul element
substantiel des cinq. Il prend le nom de la fonction et son code, et rend la
forme, le cas de base et le cas recursif en vocabulaire commun.

Ecrivez-le contre trois ou quatre solutions de reference et imprimez les
formes canoniques avant de connecter quoi que ce soit :

    cd ../fptutor-shell && python3 banc_essai.py language_ml

Le banc rend le nombre de classes d'equivalence. Un fournisseur correct donne
une classe pour des variantes purement syntaxiques et des classes separees
pour des ecritures semantiquement distinctes. Si le compte est faux, la
normalisation n'est pas encore une fonction, et les comptes d'alignement
seraient instables.

**2. Completer `command` et `test_template`.** Deux lignes chacune. La seule
exigence du second est qu'une expression produise exactement une ligne.

**3. Projeter les messages du compilateur dans `categorise`.** Cinq categories
communes, et le cadre ne voit jamais le message.

**4. Ecrire les ancrages dans `activities_ml.py`,** puis lancer
l'inducteur d'obligations :

    cd .. && TUTOR_DIR=mltutor TUTOR_LANGUAGE=language_ml python3 obligations.py

Il dit, pour chaque famille, quels ancrages sont porteurs. Un ancrage porteur
est le seul de sa famille a exhiber une variation que la famille doit montrer ;
le retirer change le compte de points de variation. C'est le controle qui
remplace des semaines de tatonnement.

**5. Adapter `referentiel.json`.** Concepts, paliers, familles, obligations. Si
votre progression est celle du referentiel commun, vous pouvez supprimer ce
fichier : le noyau prend alors celui de la racine.

**6. Lancer.**

    cd .. && python3 fptutor mltutor

## Verifier avant de servir a des apprenants

    cd .. && TUTOR_DIR=mltutor TUTOR_LANGUAGE=language_ml python3 generateur.py

Le controle aligne les solutions de reference de chaque famille et compare le
resultat a ce que le referentiel annonce. Une famille non conforme n'est pas
servie : elle produirait un plateau, c'est-a-dire une phase d'abstraction
ouverte sur un corpus dont il n'y a rien a extraire.
