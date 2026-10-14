# Trois modifications de la coquille, à consigner

Ces trois changements touchent la coquille et non l'instance. Ils sont à
consigner dans l'article sur la généricité, parce qu'ils désignent deux endroits
où le langage et la langue fuyaient dans le cadre commun.

## 1. `serveur.py` : le nom affiché vient du fournisseur

Les deux pages portaient « HaskellTutor » et « HaskellTutor4Teacher » en dur. Le
serveur substitue désormais le nom au moment de servir la page, d'après le
fournisseur : `titre` s'il le déclare, sinon `TUTOR_TITRE`, sinon l'identifiant
du langage capitalisé suivi de `Tutor`. Le message de démarrage suit la même
règle.

Trois lignes de substitution et une constante ; aucune page n'est modifiée, ce
qui évite d'avoir à maintenir une copie des interfaces par langage.

## 2. `serveur.py` : la langue par défaut vient du fournisseur

`langue_de` rendait l'anglais dès qu'aucun paramètre n'était fourni. Elle rend
maintenant, dans l'ordre : la langue demandée si la requête en précise une, celle
que le fournisseur déclare dans `langue_defaut`, la variable d'environnement
`TUTOR_LANGUE`, puis le français. Le lien de bascule de l'en-tête continue de
fonctionner dans les deux sens.

## 3. L'atelier engendre les deux champs

`gabarit_language.py` déclare désormais `titre` et `langue_defaut`, et
`creer_tuteur.py` accepte `--titre` :

    python3 creer_tuteur.py ml ocamltutor --interprete ocaml --extension .ml \
        --titre OCamlTutor

Sans l'option, le titre vaut l'identifiant capitalisé suivi de `Tutor`, soit
`MlTutor` pour `ml`, ce qui reste préférable à `HaskellTutor`.

## 4. `etudiant.html` : la page choisissait l'anglais elle-même

C'est la cause du texte anglais que l'on voit en parcourant l'interface. La page
contenait :

    const LANG = (... get("lang") === "fr") ? "fr" : "en";

Autrement dit, tout appel sans paramètre d'URL demandait explicitement l'anglais
au serveur, et la langue par défaut côté serveur n'était donc jamais consultée.
La page lit maintenant `window.LANGUE_DEFAUT`, que le serveur injecte dans
l'en-tête d'après le fournisseur, et le paramètre d'URL continue de l'emporter :

    const LANG_PARAM = new URLSearchParams(location.search).get("lang");
    const LANG = (LANG_PARAM === "fr" || LANG_PARAM === "en")
      ? LANG_PARAM
      : (window.LANGUE_DEFAUT === "en" ? "en" : "fr");

La console enseignante n'a pas ce défaut : elle ne fixe aucune langue et suit
donc le serveur.

## 5. `serveur.py` : un point d'extension du tuteur

Si le répertoire du tuteur contient `extension.py`, la coquille le charge dans le
même processus. L'extension peut exposer une API sous `/api/ext/`, déclarer des
pages servies depuis le répertoire du tuteur, et fournir deux volets insérés
d'office, l'un dans la console enseignante (`console_extension.html`), l'autre
dans la page des étudiants (`etudiant_extension.html`). Les réponses de l'API
d'extension ne passent pas par la traduction, puisqu'il s'agit de contenus
d'auteur. Les tuteurs qui n'ont pas ces fichiers ne voient rien changer.

C'est ainsi qu'OCamlTutor porte sa séance de suivi sans que la coquille la
connaisse. La modification est d'une autre nature que les quatre précédentes :
elles corrigeaient une fuite du langage ou de la langue dans le cadre commun,
celle-ci ouvre un point d'extension. Elle est à rapporter comme telle dans
l'article sur la généricité, avec son intérêt propre : une étude peut ajouter ses
instruments à une instance sans bifurquer la coquille.

## 6. Aucune donnée nominative à l'inscription

La page d'inscription demandait un « nom affiché », pré-rempli d'un nom de
personne, et un code de cours qui n'était pas celui du cours. Elle demande
désormais un pseudonyme, avec la consigne de ne pas y employer son nom, son code
permanent ni son adresse, et le serveur refuse un pseudonyme vide, qui contient
une adresse courriel, ou qui ressemble à un code permanent ou à un numéro. La
cohorte par défaut vient de la variable `TUTOR_COHORTE`.

La même page affirmait que les soumissions étaient « compilées par GHC », quel que
soit le langage : sixième fuite du langage dans le cadre commun. Le fournisseur
peut maintenant déclarer `compilateur`, et la page affiche le bon nom.

## 7. `noyau.py` : validation des familles par le fournisseur

La console validait les familles avec les solutions de référence et l'analyseur
Haskell du générateur. Pour OCaml, elle affichait « solutions de référence
absentes ». Et pour Python, elle validait en réalité les familles avec le corpus
Haskell, ce qui ne disait rien du fournisseur Python. Le noyau passe désormais par
le fournisseur lorsque celui-ci déclare `REFERENCES`, avec son analyse et
l'anti-unificateur commun ; sinon, le comportement antérieur est conservé.
Vérifié : HaskellTutor et PythonTutor inchangés, OCamlTutor conforme sur ses deux
familles, deux points pour deux déclarés et un pour un.

Le gabarit de fournisseur annonce maintenant les attributs facultatifs apparus
avec OCaml : `titre`, `langue_defaut`, `compilateur` et `REFERENCES`.

## Ce qui reste à faire sur le bilinguisme

La traduction s'applique encore au texte des énoncés d'activité, mot à mot : en
anglais, « un arbre binaire sur les entiers » devient « un arbre binaire on les
entiers ». Le français par défaut masque le problème pour la séance de novembre,
il ne le corrige pas. La correction propre consiste à exclure de la traduction
les champs qui viennent du référentiel et des activités, `enonce`, `amorce`,
`signature` et le texte des généralisations, puisque ce sont des contenus
d'auteur et non des messages du cadre. C'est une quatrième modification, plus
substantielle, à faire avant toute utilisation en anglais.
