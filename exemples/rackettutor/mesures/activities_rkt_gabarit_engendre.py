"""Ancrages et reemplois pour rkt.

ACTIVITES donne, par famille, les exercices servis en phase d'instance.
REEMPLOIS donne ceux servis apres la phase d'abstraction, sur lesquels le
reemploi spontane du schema se mesure.

Un ancrage est un quadruplet :

    (nom, enonce, amorce, [(expression, valeur attendue), ...])

Regle de composition, qui est le point le plus couteux a decouvrir par soi-meme
et que l'inducteur d'obligations verifie : les membres d'une famille doivent
differer autant que possible en surface et pas du tout en structure. Une
famille dont tous les ancrages consomment le premier element ne permettra pas
de decouvrir que l'operation peut l'ignorer.

Lancez l'inducteur des que la famille est ecrite :

    cd .. && python3 obligations.py
"""

ACTIVITES = {
    "F-map": [
        ("double", "Des quantites a convertir : multipliez chaque element par deux.",
         "double xs = TODO", [("double [1,2,3]", "[2, 4, 6]")]),
        # au moins trois autres ancrages, de surfaces tres differentes
    ],
    "F-filter": [
        ("pairs", "Des numeros de place : ne gardez que les pairs.",
         "pairs xs = TODO", [("pairs [1,2,3,4]", "[2, 4]")]),
    ],
    "F-fold": [
        ("somme", "Des releves : donnez le total.",
         "somme xs = TODO", [("somme [1,2,3]", "6")]),
        # un ancrage dont l'operation ignore l'element est obligatoire ici :
        # sans lui, l'apprenant conclut que la combinaison consomme la tete
        ("longueur", "Un inventaire dont les elements importent peu : comptez-les.",
         "longueur xs = TODO", [("longueur [7,7,7]", "3")]),
    ],
}

REEMPLOIS = {
    "F-map": [
        ("negatif", "Changez le signe de chaque element.",
         "negatif xs = TODO", [("negatif [1,-2]", "[-1, 2]")]),
    ],
    "F-filter": [],
    "F-fold": [],
}
