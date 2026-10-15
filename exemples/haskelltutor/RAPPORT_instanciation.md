# HaskellTutor : quatrième instanciation, retour au langage d'origine

La coquille a été extraite de HaskellTutor, puis éprouvée sur Python, OCaml et
Racket. Cette instance referme la boucle : la coquille, corrigée par trois
instanciations, sait-elle encore accueillir le langage dont elle vient ?

## Le coût, et pourquoi il est si bas

| Élément | Haskell | Racket | OCaml |
|---|---|---|---|
| Normalisateur | 0 | 317 | 375 |
| Fournisseur | 84 | 126 | 70 |
| Ancrages | 50 | 156 | 178 |
| Références exécutées | 43 | 67 | 62 |
| Essai à blanc | 77 | 136 | 95 |

Aucun normalisateur à écrire : `normalisation.py`, hérité de HaskellTutor,
analyse déjà une définition Haskell sur une liste. Le fournisseur se borne à
l'envelopper et à traduire son vocabulaire, `structurel-droit` et
`structurel-garde` devenant `constructors`, `ELEM` devenant `C1`. Quatre-vingt
quatre lignes contre quatre cent quarante pour Racket, soit un cinquième.

C'est le résultat principal, et il confirme la thèse de l'article TLT sous une
forme mesurée : **la portabilité de la coquille est bornée par la disponibilité
d'un analyseur du langage, et par rien d'autre**. Une fois l'analyse acquise, le
branchement tient en quelques dizaines de lignes.

## Résultats de la batterie

Sept ancrages sur sept passent leurs tests sous `runghc`, du premier coup. Le
banc ramène dix écritures à cinq termes : la réunion couvre six écritures, dont
l'inversion des opérandes et une liaison locale ; la séparation distingue le
produit, la longueur, le pli de bibliothèque et l'accumulateur. Les cinq
catégories de messages se projettent sans réglage, les catégories du cadre ayant
été tirées de GHC. L'essai à blanc parcourt la séquence complète, atelier
compris, et atteint le palier suivant.

## Deux observations

**La liaison locale n'était pas substituée.** `somme (x:xs) = x + reste where
reste = somme xs` rendait `C1 + reste` au lieu de `C1 + REC`, donc comptait
comme une variation du schéma. La substitution est faite dans le fournisseur, et
non dans `normalisation.py`, dont dépendent les ablations publiées. Le défaut
existait donc dans HaskellTutor et n'avait jamais été vu, faute d'un banc
d'essai sur cette écriture.

**Deux granularités en désaccord.** Le référentiel annonce ses points de
variation à une granularité, la politique les compte à une autre. En OCaml les
deux valeurs coïncidaient, à deux, et le désaccord est resté invisible. Ici la
famille vaut deux points en blocs et trois en granularité fine, parce que
`longueur` remplace l'élément par une constante : l'atelier ne s'ouvrait jamais.
Le référentiel déclare désormais la granularité fine, et les deux comptes
s'accordent. À vérifier sur l'instance OCaml avant la séance : elle peut porter
le même désaccord sans le montrer.

## Portée et limites

L'instance sert une seule famille, le pli à droite sur une liste, parce que
l'analyseur hérité ne lit que les listes. Les arbres, servis par OCaml et par
Racket, lui sont hors de portée : un type somme déclaré par l'apprenant n'y est
pas reconnu. L'instance Haskell est donc la plus économique et la moins
extensible des quatre.

Le coût mesuré ne vaut pas pour un langage nouveau. Il dit ce que coûte le
branchement quand l'analyse existe déjà, ce qui est précisément la situation
d'un auteur qui disposerait d'un analyseur tiers.

## Reproduire

    apt-get install -y ghc          # ou brew install ghc
    outils/verifier.sh exemples/haskelltutor language_hs cas_hs.json
    TUTOR_DIR=exemples/haskelltutor TUTOR_LANGUAGE=language_hs PORT=8082 python3 serveur.py
