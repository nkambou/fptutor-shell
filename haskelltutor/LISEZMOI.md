# haskelltutor — tuteur hs

Engendre par l'atelier FPTutor. Rien du shell n'a ete modifie.

## Dans l'ordre

**1. Ecrire `analyse` dans `language_hs.py`.** C'est le seul element
substantiel des cinq. Il prend le nom de la fonction et son code, et rend la
forme, le cas de base et le cas recursif en vocabulaire commun.

Ecrivez-le contre trois ou quatre solutions de reference et imprimez les
formes canoniques avant de connecter quoi que ce soit :

    cd ../fptutor-shell && python3 banc_essai.py language_hs

Le banc rend le nombre de classes d'equivalence. Un fournisseur correct donne
une classe pour des variantes purement syntaxiques et des classes separees
pour des ecritures semantiquement distinctes. Si le compte est faux, la
normalisation n'est pas encore une fonction, et les comptes d'alignement
seraient instables.

**2. Completer `command` et `test_template`.** Deux lignes chacune. La seule
exigence du second est qu'une expression produise exactement une ligne.

**3. Projeter les messages du compilateur dans `categorise`.** Cinq categories
communes, et le cadre ne voit jamais le message.

**4. Ecrire les ancrages dans `activities_hs.py`,** puis lancer
l'inducteur d'obligations :

    cd .. && TUTOR_DIR=haskelltutor TUTOR_LANGUAGE=language_hs python3 obligations.py

Il dit, pour chaque famille, quels ancrages sont porteurs. Un ancrage porteur
est le seul de sa famille a exhiber une variation que la famille doit montrer ;
le retirer change le compte de points de variation. C'est le controle qui
remplace des semaines de tatonnement.

**5. Adapter `referentiel.json`.** Concepts, paliers, familles, obligations. Si
votre progression est celle du referentiel commun, vous pouvez supprimer ce
fichier : le noyau prend alors celui de la racine.

**6. Lancer.**

    cd .. && TUTOR_DIR=haskelltutor TUTOR_LANGUAGE=language_hs python3 serveur.py

## Verifier avant de servir a des apprenants

Declarez REFERENCES dans le fournisseur (solutions de reference par famille,
declarations comprises si l'analyse en depend), puis :

    cd .. && TUTOR_DIR=haskelltutor TUTOR_LANGUAGE=language_hs python3 obligations.py

L'inducteur aligne chaque famille avec votre fournisseur, compare au nombre de
points annonce par le referentiel et dit quels ancrages sont porteurs. La
console enseignante affiche le meme controle. Une famille non conforme n'est
pas servie : elle produirait un plateau, c'est-a-dire une phase d'abstraction
ouverte sur un corpus dont il n'y a rien a extraire.

## Textes d'aide

Les categories d'erreur sont communes ; les textes du cadre qui leur sont
attaches parlent de GHCi et d'equations. Declarez AIDES_ERREUR et LECTURES dans
le fournisseur pour les ecrire dans votre langage, et squelette pour la
charpente du mode expose.
