"""Ancrages de l'instance Haskell : la famille du pli a droite sur une liste.

Meme forme que les autres instances, quintuplets
(identifiant, enonce, signature, amorce, tests). L'amorce donne la signature et
les deux equations a completer, puisque c'est ainsi que le cours ecrit une
definition recursive sur une liste.
"""

def _amorce(signature, nom, base, pas):
    return ("-- %s\n%s\n%s [] = %s\n%s (x:xs) = %s\n"
            % (signature, signature, nom, base, nom, pas))


ACTIVITES = {
 "F-liste": [
  ("somme",
   "Une liste d'entiers : donnez leur total.",
   "somme :: [Int] -> Int",
   _amorce("somme :: [Int] -> Int", "somme", "TODO", "TODO"),
   [("somme []", "0"), ("somme [1,2,3]", "6"), ("somme [5]", "5")]),

  ("longueur",
   "La meme liste, dont les elements importent peu : comptez-les.",
   "longueur :: [Int] -> Int",
   _amorce("longueur :: [Int] -> Int", "longueur", "TODO", "TODO"),
   [("longueur []", "0"), ("longueur [7,7,7]", "3")]),

  ("produit",
   "Une liste d'entiers : donnez le produit de ses elements.",
   "produit :: [Int] -> Int",
   _amorce("produit :: [Int] -> Int", "produit", "TODO", "TODO"),
   [("produit []", "1"), ("produit [2,3,4]", "24")]),

  ("tous_positifs",
   "Une liste d'entiers : tous ses elements sont-ils strictement positifs ?",
   "tous_positifs :: [Int] -> Bool",
   _amorce("tous_positifs :: [Int] -> Bool", "tous_positifs", "TODO", "TODO"),
   [("tous_positifs []", "True"), ("tous_positifs [1,2]", "True"),
    ("tous_positifs [1,-2]", "False")]),

  ("aplatir",
   "Une liste de listes d'entiers : donnez la liste de tous leurs elements, "
   "dans l'ordre.",
   "aplatir :: [[Int]] -> [Int]",
   _amorce("aplatir :: [[Int]] -> [Int]", "aplatir", "TODO", "TODO"),
   [("aplatir []", "[]"), ("aplatir [[1,2],[3]]", "[1,2,3]")]),
 ],
}

REEMPLOIS = {
 "F-liste": [
  ("compte_pairs",
   "Une liste d'entiers : combien de ses elements sont pairs ? Toute solution "
   "correcte est acceptee.",
   "compte_pairs :: [Int] -> Int",
   "-- compte_pairs :: [Int] -> Int\ncompte_pairs :: [Int] -> Int\ncompte_pairs = undefined\n",
   [("compte_pairs []", "0"), ("compte_pairs [1,2,3,4]", "2")]),

  ("maximum_liste",
   "Une liste d'entiers non vide : donnez le plus grand. Toute solution "
   "correcte est acceptee.",
   "maximum_liste :: [Int] -> Int",
   "-- maximum_liste :: [Int] -> Int\nmaximum_liste :: [Int] -> Int\nmaximum_liste = undefined\n",
   [("maximum_liste [3]", "3"), ("maximum_liste [1,7,4]", "7")]),
 ],
}
