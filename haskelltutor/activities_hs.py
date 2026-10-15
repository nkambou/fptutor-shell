"""Ancrages et reemplois pour hs.

ACTIVITES donne, par famille, les exercices servis en phase d'instance.
REEMPLOIS donne ceux servis apres la phase d'abstraction, sur lesquels le
reemploi spontane du schema se mesure.

Un ancrage est un quintuplet :

    (nom, enonce, signature, amorce, [(expression, valeur attendue), ...])

Regle de composition, qui est le point le plus couteux a decouvrir par soi-meme
et que l'inducteur d'obligations verifie : les membres d'une famille doivent
differer autant que possible en surface et pas du tout en structure. Une
famille dont tous les ancrages consomment le premier element ne permettra pas
de decouvrir que l'operation peut l'ignorer.

Lancez l'inducteur des que la famille est ecrite :

    cd .. && python3 obligations.py
"""

# Un ancrage est un quintuplet, dans l'ordre que le noyau et le serveur lisent :
#   (identifiant, enonce, signature, amorce, [(expression, valeur attendue), ...])

ACTIVITES = {
    "F-fold": [
        ("somme", "Des releves : donnez le total.",
         "somme : liste d'entiers -> entier",
         "somme xs = TODO",
         [("somme [1,2,3]", "6")]),
        # un ancrage dont l'operation ignore l'element est obligatoire ici :
        # sans lui, l'apprenant conclut que la combinaison consomme la tete
        ("longueur", "Un inventaire dont les elements importent peu : comptez-les.",
         "longueur : liste -> entier",
         "longueur xs = TODO",
         [("longueur [7,7,7]", "3")]),
    ],
}

REEMPLOIS = {
    "F-fold": [],
}
