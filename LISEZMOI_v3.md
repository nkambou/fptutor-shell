# FPTutor-Shell, version 3

Coquille à jour des corrections apportées par la troisième instanciation,
RacketTutor (`exemples/rackettutor`). Les modifications 1 à 7 sont celles de la
v2 (`LISEZMOI_patches.md`). Chacune des suivantes a été précédée de l'échec
observé qui la motive, consigné dans
`exemples/rackettutor/mesures/observations.md`.

## 8. `banc_essai.py` : séparation limitée aux formes admissibles

Deux écritures non alignables sont toutes deux refusées au corpus ; leur
coïncidence est sans effet. Elle est désormais signalée comme telle et non
comptée comme un échec. (Défaut de l'atelier, O4.)

## 9. `banc_essai.py` : plus de messages GHC par défaut

Sans messages dans le jeu de cas, le banc éprouvait tout fournisseur sur des
messages de GHC. Il ne contrôle plus alors que la catégorie commune à tous, le
résultat faux. (Fuite du langage, O6.)

## 10. `obligations.py` : induction par le fournisseur

Lancé avec `TUTOR_DIR` ou `TUTOR_LANGUAGE`, l'inducteur aligne les familles du
référentiel du tuteur avec les `REFERENCES` du fournisseur, à la granularité
annoncée puis en granularité fine. Il rendait auparavant, sans avertissement,
les obligations des familles Haskell. Rend inutile l'adaptateur de 67 lignes
écrit pour OCaml. (Fuite du langage, O7.)

## 11. `noyau.schema_employe` : mesure de réemploi

Une forme non analysable n'est jamais un réemploi. Si le fournisseur déclare
`reemploi(nom, code)`, c'est lui qui tranche, ce qui lui permet d'exiger une
abstraction d'ordre supérieur et d'écarter une enveloppe autour d'une récursion
écrite à la main. Les deux faux positifs corrigés dans l'instance OCaml sont
ainsi corrigés dans la coquille. (Défaut de mesure, O9 ; point d'extension.)

## 12. `noyau.py` : textes d'étayage déclarés par le fournisseur

`AIDES_ERREUR` et `LECTURES`, déclarés par le fournisseur, remplacent catégorie
par catégorie les textes du cadre, écrits pour Haskell (GHCi, équations,
listes). `squelette(forme)` écrit la charpente du mode exposé dans la syntaxe du
langage. (Fuite du langage, O11 ; point d'extension.)

## 13. Atelier : gabarits et marche à suivre

`creer_tuteur.py` engendre des ancrages en quintuplets, comme le noyau les lit ;
copie le référentiel d'un tuteur existant, `exemples/` compris, et prévient s'il
n'en trouve aucun ; prescrit la vraie commande de lancement ; renvoie, pour la
vérification finale, à `obligations.py` et à la console. `gabarit_language.py`
annonce les attributs facultatifs `AIDES_ERREUR`, `LECTURES`, `squelette` et
`reemploi`. (Défauts de l'atelier, O1, O2, O3, O8.)

## 14. `noyau.decider` : stabilité jugée une fois par corpus

La stabilité compare le compte d'alignement à celui du corpus précédent. Comme
`decider` est appelé à chaque lecture de l'état, et que la page étudiante relit
l'état après chaque soumission réussie, la relecture comparait le compte à
lui-même et ouvrait l'atelier une solution trop tôt. Le jugement est désormais
mémorisé avec une empreinte du corpus et refait seulement si le corpus a changé.
La progression affichée (`progres.stable`) lit ce jugement. Défaut de la couche
de politique, indépendant du langage, présent dans toutes les instances servies
(O12) ; vérifié par `exemples/rackettutor/sonde_http.py`.

## Non-régression

OCamlTutor : 15 références sur 15, banc (11 écritures, 6 termes), essai à blanc
à l'identique. PythonTutor : banc (7 écritures, 4 termes). `ablations.py` :
sortie identique à la v2.

## À faire sur les instances existantes

OCamlTutor ne déclare pas de textes d'étayage : ses apprenants reçoivent encore
les consignes écrites pour Haskell. Déployée sur la coquille v2, elle porte aussi
le défaut de stabilité (14).
