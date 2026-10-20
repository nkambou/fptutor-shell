"""Localisation par catalogue de messages, applique a la frontiere.

Le texte source du systeme est en francais. Ce module rend la version anglaise
en substituant des phrases entieres, en une seule passe : une portion deja
traduite n'est jamais reexaminee, ce qui evite les substitutions en cascade du
genre « exclus » -> « excluded » -> « excludeded ».

Deux fonctions publiques :

    traduire_texte(s, langue)   une chaine
    traduire(obj, langue)       recursivement, une structure JSON

La langue par defaut du systeme est l'anglais : c'est celle des captures de
l'article et celle que voit un lecteur qui ouvre le depot. Le francais reste
disponible et sert le cours.
"""

import re

# ------------------------------------------------------------ catalogue
# Regle : une entree fait au moins quinze caracteres, ou figure dans ETIQUETTES
# et n'est alors substituee qu'en mot entier.

CATALOGUE = {
 # --- messages du tuteur, reussite
 "Bien vu.": "Well spotted.",
 "solution au dossier ; le tuteur en attend au moins":
   "solution in the dossier; the tutor expects at least",
 "solutions au dossier ; le tuteur en attend au moins":
   "solutions in the dossier; the tutor expects at least",
 "avant de vous les montrer ensemble.": "before showing them to you together.",
 "solutions au dossier. En les comparant, le tuteur y voit":
   "solutions in the dossier. Comparing them, the tutor sees",
 "chose qui change d'une solution à l'autre. Il en cherche":
   "thing that changes from one solution to the next. It is looking for",
 "choses qui changent d'une solution à l'autre. Il en cherche":
   "things that change from one solution to the next. It is looking for",
 "Le tuteur vérifie sur une solution de plus que ce compte ne bouge pas.":
   "The tutor checks on one more solution that this count does not move.",
 "et le compte ne bouge plus.": "and the count no longer moves.",
 "point de variation, et le compte ne bouge plus.":
   "variation point, and the count no longer moves.",
 "points de variation, et le compte ne bouge plus.":
   "variation points, and the count no longer moves.",
 "c'est le compte attendu.": "that is the expected count.",
 "Vous allez pouvoir les regarder ensemble.":
   "You will be able to look at them together.",
 "Votre solution est enregistrée.": "Your solution is recorded.",
 "Elle est conservée à part.": "It is kept separately.",

 # --- messages du tuteur, solution correcte mais hors forme
 "C'est juste, et votre solution fonctionne.":
   "That is right, and your solution works.",
 "Pour la suite, le tuteur a besoin de solutions écrites de la même manière, parce qu'il va vous les montrer côte à côte : c'est en les comparant que vous trouverez ce qu'elles ont en commun.":
   "For what follows, the tutor needs solutions written in the same way, because it is going to show them to you side by side: it is by comparing them that you will find what they have in common.",
 "La votre est correcte mais elle ne se compare pas terme à terme avec les autres.":
   "Yours is correct, but it does not compare term by term with the others.",
 "Le tuteur passe à un autre problème de même nature. Écrivez-le en distinguant le cas de la liste vide et le cas ou elle a au moins un élément : c'est cette forme-la qu'il faut pour la suite.":
   "The tutor moves to another problem of the same kind. Write it by distinguishing the case of the empty list from the case where it has at least one element: that is the form needed for what follows.",
 "Réécrivez la même fonction en distinguant explicitement le cas de la liste vide et le cas ou elle a au moins un élément.":
   "Write the same function again, distinguishing explicitly the case of the empty list from the case where it has at least one element.",
 "Vous savez visiblement déjà obtenir ce résultat sans le détailler. Écrivez-le maintenant detaille, et vous aurez les deux versions sous les yeux.":
   "You evidently already know how to obtain this result without spelling it out. Write it out now, and you will have both versions in front of you.",
 "Elle est correcte, mais elle n'entre pas dans la comparaison :":
   "It is correct, but it does not enter the comparison:",
 "correcte mais non alignable": "correct but not alignable",
 "correcte mais sans récursion explicite": "correct but without explicit recursion",
 "schéma déjà employé": "schema already used",
 "aucun cas récursif reconnu": "no recursive case recognised",
 "tests non reussis": "tests not passed",
 "Non admise à l'alignement :": "Not admitted to the alignment:",
 "Soumission admise au corpus d'alignement.":
   "Submission admitted to the alignment corpus.",
 "Compilation reussie.": "Compiled successfully.",
 "tests reussis.": "tests passed.",

 # --- raisons de non-comparabilite
 "une compréhension donne le même résultat et masque cet endroit précis":
   "a comprehension gives the same result and hides that precise place",
 "un accumulateur applique l'opération avant l'appel récursif, ce qui est un autre schéma":
   "an accumulator applies the operation before the recursive call, which is another schema",
 "une fonction toute faite donne le résultat sans montrer la marche":
   "a library function gives the result without showing the procedure",
 "il n'y a pas de cas récursif a comparer":
   "there is no recursive case to compare",

 # --- etayage
 "Trois niveaux, à la demande. Aucun ne donne la solution ni ne nomme le schéma.":
   "Three levels, on request. None gives the solution or names the schema.",
 "Le compilateur signale un motif non couvert. Quelle forme d'entrée votre définition ne traite-t-elle pas ?":
   "The compiler reports an uncovered pattern. Which form of input does your definition not handle?",
 "Le compilateur signale qu'une forme d'entrée n'est pas traitée.":
   "The compiler reports that one form of input is not handled.",
 "Vous pouvez demander un étayage : trois niveaux, aucun ne donne la solution.":
   "You may ask for scaffolding: three levels, none of which gives the solution.",
 "Vous pouvez demander un indice : trois niveaux, aucun ne donne la solution.":
   "You may ask for a hint: three levels, none of which gives the solution.",
 "fonde sur votre dernière erreur :": "based on your last error:",
 "Il vous manque une équation dont le motif est":
   "You are missing an equation whose pattern is",
 "Sa valeur est celle qui ne change rien à l'opération que vous employez.":
   "Its value is the one that changes nothing in the operation you are using.",
 "Deux tentatives sans succès : vous pouvez":
   "Two attempts without success: you may",

 # --- consigne de forme et explication epistemique
 "Forme attendue": "Expected form",
 "Écrivez cette fonction en distinguant explicitement le cas de la liste vide et le cas ou elle a au moins un élément. Une solution correcte écrite autrement sera acceptee et conservée, mais elle ne pourra pas être comparee aux autres.":
   "Write this function by distinguishing explicitly the case of the empty list from the case where it has at least one element. A correct solution written otherwise will be accepted and kept, but it will not be comparable with the others.",
 "Pourquoi cette forme ?": "Why this form?",
 "Pour que la comparaison soit possible, il faut voir deux choses dans chaque solution :":
   "For the comparison to be possible, two things must be visible in each solution:",
 "Autrement dit, la contrainte de forme n'est pas une exigence de style : c'est ce qui rend la comparaison possible.":
   "The form requirement is therefore not a matter of style: it is what makes the comparison possible.",
 "La contrainte porte donc sur ce que la solution rend visible, pas sur sa qualité.":
   "The requirement concerns what the solution makes visible, not its quality.",
 "Une compréhension donne le même résultat et masque cet endroit précis.":
   "A comprehension gives the same result and hides that precise place.",

 # --- verification par explication
 "Que rend votre fonction sur l'entrée vide ?":
   "What does your function return on the empty input?",
 "Dans votre cas récursif, quelle expression désigne le résultat déjà calculé sur le reste de l'entrée ?":
   "In your recursive case, which expression denotes the result already computed on the rest of the input?",
 "Cette valeur est celle qui ne change rien à l'opération que vous employez : c'est ainsi qu'on la trouve.":
   "That value is the one that changes nothing in the operation you are using, which is how it is found.",
 "C'est l'appel récursif : vous supposez que la fonction sait déjà répondre sur le reste, et vous vous contentez de combiner ce résultat avec le premier élément.":
   "That is the recursive call: you assume the function already answers on the rest, and you simply combine that result with the first element.",
 "soumission très rapide après l'ouverture de l'activité":
   "submission arriving within seconds of the activity being opened",
 "aucune tentative intermédiaire, aucun étayage":
   "no intermediate attempt, no scaffolding",
 "mise en forme inhabituelle pour une saisie au fil de l'écriture":
   "layout unusual for text typed as it is written",
 "Merci : votre explication correspond à ce que votre code fait.":
   "Thank you: your explanation matches what your code does.",
 "Votre réponse ne correspond pas à ce que votre code fait. La solution reste enregistrée ; reprenez-la si vous voulez, et demandez un étayage au besoin.":
   "Your answer does not match what your code does. The solution stays recorded; revise it if you wish, and ask for scaffolding if you need it.",

 # --- decisions et motifs
 "corpus insuffisant": "corpus insufficient",
 "alignement stable a": "alignment stable at",
 "points de variation": "variation points",
 "point de variation": "variation point",
 "alignement a": "alignment at",
 "mais pas encore stable": "but not yet stable",
 "plus d'ancrage disponible dans la famille":
   "no anchor left in the family",
 "plafond d'instances atteint": "instance ceiling reached",
 "réemploi a servir": "reuse item to serve",
 "concept acquis": "concept acquired",

 # --- variantes accentuees, telles qu'elles figurent dans le referentiel
 "Des notes sur cent : ne gardez que les reçues.":
   "Marks out of a hundred: keep only the passing ones.",
 "Types définis par l'utilisateur":
   "User-defined types",
 "Listes et filtrage par patterns":
   "Lists and pattern matching",
 "Récursion structurelle":
   "Structural recursion",
 "Évaluation paresseuse":
   "Lazy evaluation",
 "Échec, choix, effets":
   "Failure, choice, effects",
 "Les trois schémas":
   "The three schemas",
 "Ordre supérieur":
   "Higher order",

 "Fichier lu par le générateur. Un enseignant qui change de progression ne modifie que ce fichier.":
   "File read by the generator. A teacher changing the progression edits this file only.",
 "le cas de base doit varier, sinon la troisième variation reste invisible":
   "the base case must vary, otherwise the third variation stays invisible",
 "rendre un type personnel utilisable par une fonction générique":
   "make a user-defined type usable by a generic function",
 "supprimer un argument nommé dans trois définitions existantes":
   "remove a named argument from three existing definitions",
 "Enchaîner deux fonctions sans nommer la valeur intermédiaire":
   "Chain two functions without naming the intermediate value",
 "séparer le calcul pur de l'entrée-sortie dans un programme":
   "separate pure computation from input and output in a program",
 "La récursion suit la forme du type, pas celle de la liste":
   "Recursion follows the shape of the type, not that of the list",
 "Cas de base, cas récursif, décroissance sur la structure":
   "Base case, recursive case, decrease on the structure",
 "écrire le pli d'un type défini par l'apprenant lui-même":
   "write the fold of a type the learner defined",
 "Une fonction à deux arguments en est une à un argument":
   "A two-argument function is a one-argument function",
 "Une liste est une structure récursive, pas un tableau":
   "A list is a recursive structure, not an array",
 "au moins un ancrage dont l'opération ignore l'élément":
   "at least one anchor whose operation ignores the element",
 "écrire une récursion sur une liste non vue en cours":
   "write a recursion over a list not seen in the course",
 "Une fonction qui peut échouer le dit dans son type":
   "A function that may fail says so in its type",
 "Ce qui sort du programme est marqué dans le type":
   "What leaves the program is marked in the type",
 "Le compilateur connaît le type avant l'exécution":
   "The compiler knows the type before execution",
 "écart de surface maximal, écart de structure nul":
   "maximal surface variation, null structural variation",
 "Une même opération sur des types différents":
   "One operation on several types",
 "De Haskell à la programmation fonctionnelle":
   "From Haskell to functional programming",
 "modéliser un domaine en trois constructeurs":
   "model a domain with three constructors",
 "remplacer une fonction partielle du prélude":
   "replace a partial function from the prelude",
 "Ce qui n'est pas demandé n'est pas calculé":
   "What is not asked for is not computed",
 "écrire un motif à deux niveaux (x:y:reste)":
   "write a two-level pattern (x:y:rest)",
 "Enchaîner des calculs qui peuvent échouer":
   "Chain computations that may fail",
 "Deux plis, deux comportements en mémoire":
   "Two folds, two behaviours in memory",
 "redéfinir map ou filter à l'aide du pli":
   "redefine map or filter using the fold",
 "Garder ou écarter selon une condition":
   "Keep or discard on a condition",
 "employer le schéma sans y être invité":
   "use the schema unprompted",
 "map se généralise au-delà des listes":
   "map generalises beyond lists",
 "réécrire un pipeline de trois étapes":
   "rewrite a three-stage pipeline",
 "supprimer trois filtrages imbriqués":
   "remove three nested filters",
 "écrire fmap pour un type personnel":
   "write fmap for a user-defined type",
 "Réduire une liste à une valeur":
   "Reduce a list to a value",
 "Transformer chaque élément":
   "Transform each element",
 "arithmétique unaire":
   "unary arithmetic",
 "ignore l'élément":
   "ignores the element",
 "sur la chaîne":
   "on the string",
 "arithmétique":
   "arithmetic",

 "avez écrites. Le tuteur a aligné leurs cas de base et leurs cas récursifs. Écrivez une seule définition qui les remplace toutes.":
   "have written. The tutor has aligned their base cases and their recursive cases. Write a single definition that replaces them all.",
 "écrire assez de solutions comparables, y trouver ce qu'elles ont en commun, puis l'employer sans y être invité":
   "write enough comparable solutions, find what they share, then use it unprompted",
 "écrire assez de solutions comparables, y trouver ce qu'elles ont en commun, puis l'employer sans y être invite":
   "write enough comparable solutions, find what they share, then use it unprompted",
 "Cliquez sur une solution pour la revoir et la reprendre. La reprendre remplace votre version dans le dossier.":
   "Click a solution to review and revise it. Revising replaces your version in the dossier.",
 "Un concept passe à « acquis » au réemploi spontané du schéma, pas à la réussite de l'activité.":
   "A concept becomes acquired on spontaneous reuse of the schema, not on completing the activity.",
 "Écrivez votre définition ci-dessous. Elle est conservée et servira à l'atelier d'équipe.":
   "Write your definition below. It is kept and will be used in the team workshop.",
 "Vous pouvez quitter la séance à tout moment ; votre dossier est conservé.":
   "You may leave the session at any time; your dossier is kept.",
 "Aucun groupe sur ce concept.":
   "No group on this concept.",
 "Ce qu'il faut atteindre :":
   "What has to be reached:",
 "enchaîner automatiquement":
   "advance automatically",
 "Valider ma généralisation":
   "Submit my generalisation",
 "attendre que je continue":
   "wait until I continue",
 "Voici les fonctions que <b>vous</b> avez écrites. Le tuteur a aligné leurs cas de base et leurs cas récursifs. Écrivez une seule définition qui les remplace toutes.":
   "These are the functions <b>you</b> have written. The tutor has aligned their base cases and their recursive cases. Write a single definition that replaces them all.",
 "Voici les fonctions que":
   "These are the functions",
 "Après une réussite :":
   "After a success:",
 "Rester sur cet écran":
   "Stay on this screen",
 "Demander un étayage":
   "Ask for scaffolding",
 "Atelier de remontée":
   "Abstraction workshop",
 "Compiler et tester":
   "Compile and test",
 "Carte des concepts":
   "Concept map",
 "Décision du tuteur":
   "Tutor's decision",
 "Activité engendrée":
   "Generated activity",
 "Quitter la séance":
   "Leave the session",
 "Activité suivante":
   "Next activity",
 "Gérer mon groupe":
   "Manage my group",
 "Ma progression":
   "My progress",
 "Mes solutions":
   "My solutions",
 "hors forme :":
   "off-form:",
 "Mon activité":
   "My activity",
 "instance(s)":
   "instance(s)",
 "hors ligne":
   "offline",
 "Pas encore":
   "Not yet",
 "au dossier":
   "in the dossier",
 "réemployer":
   "reuse",
 "Décision :":
   "Decision:",
 "Le tuteur":
   "The tutor",
 "Régime :":
   "Regime:",
 "comparer":
   "compare",
 "Étayage":
   "Scaffolding",
 "verrou":
   "locked",
 "Séance":
   "Session",
 "Groupe":
   "Group",
 "écrire":
   "write",

 "Le tuteur ne vous montrera vos solutions ensemble que lorsque ce compte sera atteint et stable. Il n'y a rien à mémoriser d'ici là.":
   "The tutor will show your solutions together only once that count is reached and stable. There is nothing to memorise until then.",
 "avez écrites. Le tuteur a aligné leurs cas de base et leurs cas récursifs. Écrivez une seule définition qui les remplace toutes.":
   "have written. The tutor has aligned their base cases and their recursive cases. Write a single definition that replaces them all.",
 "Cliquez sur une solution pour la revoir et la reprendre. La reprendre remplace votre version dans le dossier.":
   "Click a solution to review and revise it. Revising replaces your version in the dossier.",
 "Un concept passe à « acquis » au réemploi spontané du schéma, pas à la réussite de l'activité.":
   "A concept becomes acquired on spontaneous reuse of the schema, not on completing the activity.",
 "Écrivez votre définition ci-dessous. Elle est conservée et servira à l'atelier d'équipe.":
   "Write your definition below. It is kept and will be used in the team workshop.",
 "Ces réussites sont enregistrées ; elles ne servent simplement pas à la comparaison.":
   "These successes are recorded; they simply do not serve the comparison.",
 "Trois niveaux, à la demande. Aucun ne donne la solution ni ne nomme le schéma.":
   "Three levels, on request. None gives the solution or names the schema.",
 "Vous pouvez demander un étayage : trois niveaux, aucun ne donne la solution.":
   "You may ask for scaffolding: three levels, none of which gives the solution.",
 "Vous pouvez quitter la séance à tout moment ; votre dossier est conservé.":
   "You may leave the session at any time; your dossier is kept.",
 "Enchaîner deux fonctions sans nommer la valeur intermédiaire":
   "Chain two functions without naming the intermediate value",
 "La récursion suit la forme du type, pas celle de la liste":
   "Recursion follows the shape of the type, not that of the list",
 "Cas de base, cas récursif, décroissance sur la structure":
   "Base case, recursive case, decrease on the structure",
 "Une fonction à deux arguments en est une à un argument":
   "A two-argument function is a one-argument function",
 "Une liste est une structure récursive, pas un tableau":
   "A list is a recursive structure, not an array",
 "Une fonction qui peut échouer le dit dans son type":
   "A function that may fail says so in its type",
 "Le compilateur connaît le type avant l'exécution":
   "The compiler knows the type before execution",
 "Ce qui sort du programme est marqué dans le type":
   "What leaves the program is marked in the type",
 "Une même opération sur des types différents":
   "One operation on several types",
 "Ce qui n'est pas demandé n'est pas calculé":
   "What is not asked for is not computed",
 "Enchaîner des calculs qui peuvent échouer":
   "Chain computations that may fail",
 "Ce qui change d'une solution à l'autre :":
   "What varies from one solution to the next:",
 "Deux plis, deux comportements en mémoire":
   "Two folds, two behaviours in memory",
 "Garder ou écarter selon une condition":
   "Keep or discard on a condition",
 "map se généralise au-delà des listes":
   "map generalises beyond lists",
 "— fondé sur votre dernière erreur :":
   "— based on your last error:",
 "fondé sur votre dernière erreur":
   "based on your last error",
 "Types définis par l'utilisateur":
   "User-defined types",
 "Réduire une liste à une valeur":
   "Reduce a list to a value",
 "Problèmes résolus autrement :":
   "Problems solved otherwise:",
 "Aucun groupe sur ce concept.":
   "No group on this concept.",
 "et le compte ne bouge plus.":
   "and the count no longer moves.",
 "Écartées de l'alignement :":
   "Set aside from the alignment:",
 "Transformer chaque élément":
   "Transform each element",
 "enchaîner automatiquement":
   "advance automatically",
 "Solutions au dossier :":
   "Solutions in the dossier:",
 "Récursion structurelle":
   "Structural recursion",
 "Évaluation paresseuse":
   "Lazy evaluation",
 "le tuteur en cherche":
   "the tutor is looking for",
 "Après une réussite :":
   "After a success:",
 "Échec, choix, effets":
   "Failure, choice, effects",
 "Demander un étayage":
   "Ask for scaffolding",
 "Atelier de remontée":
   "Abstraction workshop",
 "remontée discovery":
   "abstraction discovery",
 "Activité engendrée":
   "Generated activity",
 "Décision du tuteur":
   "Tutor's decision",
 "Quitter la séance":
   "Leave the session",
 "Activité suivante":
   "Next activity",
 "Les trois schémas":
   "The three schemas",
 "remontée exposed":
   "abstraction exposed",
 "Gérer mon groupe":
   "Manage my group",
 "Étayage, niveau":
   "Scaffolding, level",
 "remontée guided":
   "abstraction guided",
 "Ordre supérieur":
   "Higher order",
 "Ma progression":
   "My progress",
 "Mes solutions":
   "My solutions",
 "Mon activité":
   "My activity",
 "hors forme :":
   "off-form:",
 "régime free":
   "regime free",
 "régime solo":
   "regime solo",
 "régime pair":
   "regime pair",
 "régime team":
   "regime team",
 "au minimum.":
   "at least.",
 "Décision :":
   "Decision:",
 "réemployer":
   "reuse",
 "Régime :":
   "Regime:",
 "Étayage":
   "Scaffolding",
 "Séance":
   "Session",
 "écrire":
   "write",

 "mode discovery · 1 point(s) de variation":
   "discovery mode · 1 variation point",
 "Voici les fonctions que <b>vous</b> avez écrites. Le tuteur a aligné leurs cas de base et leurs cas récursifs. Écrivez une seule définition qui les remplace toutes.":
   "These are the functions <b>you</b> have written. The tutor has aligned their base cases and their recursive cases. Write a single definition that replaces them all.",
 "Voici les fonctions que":
   "These are the functions",
 "point(s) de variation":
   "variation point(s)",

 "Le tuteur vous demande de temps à autre d'expliquer ce que fait votre code. Cela ne met pas votre travail en doute : mettre une solution en mots est une des façons les plus efficaces de l'apprendre.":
   "The tutor asks from time to time what your code does. This does not call your work into question: putting a solution into words is one of the most effective ways of learning it.",
 "Multipliez chaque élément par deux.":
   "Multiply each element by two.",
 "Multipliez chaque élément par deux.":
   "Multiply each element by two.",
 "Une question sur votre solution.":
   "A question about your solution.",
 "Continuer":
   "Continue",
 "Répondre":
   "Answer",

 "Dans votre cas récursif, quelle expression désigne le résultat déjà calculé sur le reste de l'entrée ?":
   "In your recursive case, which expression denotes the result already computed on the rest of the input?",
 "Que rend votre fonction sur l'entrée vide ?":
   "What does your function return on the empty input?",
 "Compilation réussie. 2 tests réussis.":
   "Compiled successfully. 2 tests passed.",
 "Compilation réussie. 3 tests réussis.":
   "Compiled successfully. 3 tests passed.",
 "Compilation réussie.":
   "Compiled successfully.",
 "tests réussis.":
   "tests passed.",

 "votre solution ne donne pas le bon résultat":
   "your solution does not give the right result",
 "Compilation réussie, mais ":
   "Compiled successfully, but ",
 "Compilation réussie. ":
   "Compiled successfully. ",
 " tests réussis.":
   " tests passed.",

 " au lieu de ": " instead of ",



 "La votre est correcte mais elle ne distingue pas les cas : on n'y voit ni ce que vaut le résultat sur une liste vide, ni ce que vous faites du premier élément.":
   "Yours is correct, but it does not distinguish the cases: it shows neither what the result is on an empty list nor what you do with the first element.",

 " sur 3 au minimum.": " of 3 at least.",
 " sur 4 au minimum.": " of 4 at least.",
 " sur 5 au minimum.": " of 5 at least.",
 "(0 sur 3)": "(0 of 3)", "(1 sur 3)": "(1 of 3)", "(2 sur 3)": "(2 of 3)",
 "(3 sur 3)": "(3 of 3)", "(0 sur 4)": "(0 of 4)", "(1 sur 4)": "(1 of 4)",
 "(2 sur 4)": "(2 of 4)", "(3 sur 4)": "(3 of 4)",
 "niveau 1 sur 3": "level 1 of 3", "niveau 2 sur 3": "level 2 of 3",
 "niveau 3 sur 3": "level 3 of 3",
 "Votre solution est enregistrée.": "Your solution is recorded.",

 "Non admise à l'alignement :": "Not admitted to the alignment:",
 "Non admise à l'alignement :": "Not admitted to the alignment:",

 "Non admise à l'alignement :":
   "Not admitted to the alignment:",
 "Soumission admise au corpus d'alignement.":
   "Submission admitted to the alignment corpus.",
 "Une question sur votre solution.":
   "A question about your solution.",
 "Votre solution est enregistrée.":
   "Your solution is recorded.",

 "exposée": "exposed",
 "été produit": "been produced",

 # --- etayage et lectures d'erreur
 "L'auto-organisation ne s'exerce que dans l'ensemble eligible : seuls les pairs au même état sur le concept visé sont proposes.":
   "Self-organisation operates only within the eligible set: only peers at the same state on the target concept are offered.",
 "Il vous manque une équation dont le motif est [] . Sa valeur est celle qui ne change rien à l'opération que vous employez.":
   "You are missing an equation whose pattern is [] . Its value is the one that changes nothing in the operation you are using.",
 "seuls les pairs au même état sur le concept visé sont proposes.":
   "only peers at the same state on the target concept are offered.",
 "L'auto-organisation ne s'exerce que dans l'ensemble eligible :":
   "Self-organisation operates only within the eligible set:",
 "change rien à l'opération que vous employez.":
   "changes nothing in the operation you are using.",
 "C'est l'appel récursif : vous supposez que la fonction sait déjà répondre sur le reste, et vous vous contentez de combiner ce résultat avec le premier élément.":
   "That is the recursive call: you assume the function already answers on the rest, and you simply combine that result with the first element.",
 "Une liste est soit vide, soit un élément suivi d'une liste. Vous avez écrit une équation pour la seconde forme seulement.":
   "A list is either empty or an element followed by a list. You have written an equation for the second form only.",
 "Une liste en compréhension, ou un appel a une fonction toute faite, donne le bon résultat sans montrer ces deux choses.":
   "A list comprehension, or a call to a library function, gives the right result without showing those two things.",
 "Autrement dit, la contrainte de forme n'est pas une exigence de style : c'est ce qui rend la comparaison possible.":
   "The form requirement is therefore not a matter of style: it is what makes the comparison possible.",
 "Le tuteur a fait l'alignement pour vous : les colonnes ci-dessus montrent le cas":
   "The tutor has done the alignment for you: the columns above show the case",
 "Votre solution est juste. Mais ce que le cours construit ici est la comparaison":
   "Your solution is right. But what the course is building here is the comparison",
 "Vous savez déjà obtenir ce résultat. Ce que le cours cherche a construire n'est":
   "You already know how to obtain this result. What the course is trying to build is not",
 "Charpente : f [] = Z et f (x:xs) = ... x ... (f xs). Pour Z, cherchez la valeur":
   "Skeleton: f [] = Z and f (x:xs) = ... x ... (f xs). For Z, look for the value",
 "Votre solution fonctionne. Ce que le cours cherche ici est ce qui reste commun":
   "Your solution works. What the course is after here is what remains common",
 "Comparez le type attendu et le type trouve, puis demandez a GHCi le type de la":
   "Compare the expected type with the type found, then ask GHCi for the type of the",
 "Charpente : f [] = [] puis f (x:xs) avec deux gardes, dont l'une conserve x et":
   "Skeleton: f [] = [] then f (x:xs) with two guards, one of which keeps x and",
 "fois que vous résolvez un problème autrement que ce que la comparaison attend.":
   "time you have solved a problem otherwise than the comparison expects.",
 "Votre solution est juste. La forme demandée n'est pas une question de style :":
   "Your solution is right. The form asked for is not a matter of style:",
 "Le désaccord porte sur l'argument que le message nomme. Vérifiez ce que votre":
   "The disagreement concerns the argument the message names. Check what your",
 "Écrivez une définition qui reçoit en arguments ce qui varie, et qui garde tel":
   "Write a definition that takes what varies as arguments, and keeps as it is",
 "Il vous manque une équation dont le motif est [] . Sa valeur est celle qui ne":
   "You are missing an equation whose pattern is [] . Its value is the one that",
 "Une équation tient sur une ligne, ou ses suites sont indentées davantage que":
   "An equation fits on one line, or its continuations are indented more than",
 "Écrite en distinguant le cas vide et le cas ou il reste un élément, avec une":
   "Written by distinguishing the empty case from the case where an element remains, with a",
 "Pour que la comparaison soit possible, il faut voir deux choses dans chaque":
   "For the comparison to be possible, two things must be visible in each",
 "Comparez le résultat obtenu et le résultat attendu sur le premier test qui":
   "Compare the result obtained with the result expected on the first test that",
 "Écrivez vos définitions les unes sous les autres et rayez tout ce qui est":
   "Write your definitions one below the other and strike out everything that is",
 "Vérifiez l'orthographe et la casse : un nom de fonction commence par une":
   "Check the spelling and the case: a function name begins with a",
 "Déroulez votre définition à la main sur l'entrée du test qui échoue, en":
   "Unfold your definition by hand on the input of the failing test,",
 "Un entier et un nombre fractionnaire se rencontrent dans la même":
   "An integer and a fractional number meet in the same",
 "Cette valeur est celle qui ne change rien à l'opération que":
   "That value is the one that changes nothing in the operation you",
 "Dans votre cas récursif, quelle expression désigne le":
   "In your recursive case, which expression denotes the",
 "C'est juste, et votre solution fonctionne. C'est la":
   "That is right, and your solution works. This is the",
 "Cette fonction produit une liste plus courte, sans modifier les éléments gardes.":
   "This function produces a shorter list, without modifying the elements it keeps.",
 "Deux conduites sont possibles pour un élément : le garder ou l'ignorer. Une ":
   "Two courses of action are available for an element, keeping it or ignoring it. One ",
 "Cette fonction produit une liste de même longueur que celle qu'elle reçoit.":
   "This function produces a list of the same length as the one it receives.",
 "Deux choses sont a decider : ce que vaut le résultat sur la liste vide, et ":
   "Two things have to be decided: what the result is on the empty list, and ",
 "Traitez le premier élément, puis laissez la récursion s'occuper du reste.":
   "Deal with the first element, then let the recursion take care of the rest.",
 "Cette fonction ne produit pas une liste : elle produit une seule valeur.":
   "This function does not produce a list: it produces a single value.",
 "Si la fonction vient d'un module, il faut l'importer en tête de fichier.":
   "If the function comes from a module, it must be imported at the top of the file.",
 "Mettez chaque chaîne en majuscules. import Data.Char (toUpper) autorise.":
   "Put each string in upper case. import Data.Char (toUpper) is allowed.",
 "Enveloppez chaque opérande entier dans fromIntegral avant de diviser.":
   "Wrap each integer operand in fromIntegral before dividing.",
 "Les résultats de plusieurs verifications : toutes ont-elles réussi ?":
   "The results of several checks: did they all pass?",
 "Votre code compile : l'erreur n'est pas de forme mais de calcul.":
   "Your code compiles: the error is not one of form but of computation.",
 "Le compilateur a trouvé un type là où il en attendait un autre.":
   "The compiler found one type where it expected another.",
 "Le fichier ne s'analyse pas : le problème est en amont du sens.":
   "The file does not parse: the problem lies upstream of meaning.",
 "Vérifiez l'indentation et les parenthèses de la ligne signalée.":
   "Check the indentation and the parentheses of the reported line.",
 "Votre code compile. L'erreur n'est pas de forme mais de calcul.":
   "Your code compiles. The error is not one of form but of computation.",
 "Une division exige des nombres fractionnaires des deux côtés.":
   "Division requires fractional numbers on both sides.",
 "Un nom employé dans votre code n'est défini nulle part.":
   "A name used in your code is not defined anywhere.",
 "Charpente : f [] = ... et f (x:xs) = ... x ... : f xs":
   "Skeleton: f [] = ... and f (x:xs) = ... x ... : f xs",
 "Ne gardez que les mots de moins de quatre lettres.":
   "Keep only the words of fewer than four letters.",
 "Le compilateur a refusé votre définition.":
   "The compiler rejected your definition.",
 "Aucun indice supplementaire a ce niveau.":
   "No further hint at this level.",
 "Remplacez chaque élément par son carre.":
   "Replace each element by its square.",
 "Recollez des mots en une seule chaîne.":
   "Join words into a single string.",
 "Un texte : ne gardez que les voyelles.":
   "A text: keep only the vowels.",
 "Un nom employé n'est pas défini.":
   "A name you used is not defined.",
 "Compile et passe les tests.":
   "Compiles and passes the tests.",

 # --- console enseignante
 "concept(s) en abstraction exposée : le concept sera présenté avant d'avoir été produit, et l'indicateur de réemploi y perdra sa valeur diagnostique. Le réglage est conservé : la console signale, elle n'interdit pas.":
   "concept(s) set to exposed abstraction: the concept will be presented before it has been produced, and the reuse indicator loses its diagnostic value there. The setting is kept: the console reports, it does not forbid.",
 "généralisation produite":
   "generalization produced",
 "abstraction exposée":
   "exposed abstraction",
 "vérification":
   "verification",
 "expliquées":
   "unexplained",
 "assistance":
   "scaffolding",
 "étayages":
   "scaffolding",
 "réemploi":
   "reuse",
 "conservé":
   "kept",
 "présenté":
   "presented",
 "remontée":
   "abstraction",
 "séquence":
   "sequence",
 "réglage":
   "setting",
 "régime":
   "regime",
 "palier":
   "tier",
 "réglé":
   "set",
 "délai":
   "allowance",
 "état":
   "state",
 ", la demande est déclenchée par des indices — soumission très rapide, aucune tentative intermédiaire, aucun étayage — qui sont des indices et non des preuves. Une explication qui ne correspond pas au code est signalée dans la cohorte ; la solution reste enregistrée et rien n'est retiré à l'apprenant.":
   " mode the request is triggered by indicators, a very fast submission, no intermediate attempt and no scaffolding taken, which are indicators and not evidence. An explanation that does not match the code is reported in the cohort view; the solution stays recorded and nothing is withdrawn from the learner.",
 "exposée : le concept sera présenté avant d'avoir été produit, et l'indicateur de réemploi y perdra sa valeur diagnostique. Le réglage est conservé : la console signale, elle n'interdit pas.":
   "exposed abstraction: the concept will be presented before it has been produced, and the reuse indicator loses its diagnostic value there. The setting is kept: the console reports, it does not forbid.",
 "demande la seconde écriture comme une comparaison plutôt que comme une correction. Dans les trois cas la réussite est comptée et la solution conservée.":
   "asks for the second writing as a comparison rather than a correction. In all three the success is counted and the solution kept.",
 "Le tuteur demande de temps à autre à l'apprenant d'expliquer sa propre solution, par deux questions engendrées à partir du code soumis. En régime":
   "The tutor asks the learner from time to time to explain their own solution, through two questions generated from the submitted code. In",
 "Une soumission hors délai est enregistrée comme telle mais compte quand même : le délai informe, il ne sanctionne pas.":
   "A late submission is recorded as such and still counts: the allowance informs, it does not penalise.",
 "l'apprenant ne pourra pas quitter la séance avant d'avoir acquis le concept. À réserver aux séances encadrées.":
   "the learner may not leave the session before acquiring the concept, and this should be reserved for supervised sessions.",
 "L'échelle d'étayage compte 3 niveaux ; aucun ne donne la solution ni ne nomme le schéma. En régime":
   "The scaffolding ladder has 3 levels; none gives the solution or names the schema. In",
 ", le tuteur propose l'étayage de lui-même après deux tentatives infructueuses.":
   " mode, the tutor offers scaffolding of its own accord after two failed attempts.",
 "passe à un autre problème de même nature avec une consigne de forme ;":
   "moves to another problem of the same kind with a form instruction;",
 "maintient l'exercice et demande une seconde écriture ;":
   "keeps the exercise and asks for a second writing;",
 "Le choix de l'apprenant ne s'y appliquera pas.":
   "The learner's choice will not apply there.",
 "Solution correcte mais hors forme.":
   "Correct but off-form solution.",
 "Appliquer à tous les concepts :":
   "Apply to every concept:",
 "Vérification par explication.":
   "Verification by explanation.",
 "concept(s) sans assistance":
   "concept(s) with scaffolding closed",
 "GENERALISATION PRODUITE":
   "GENERALIZATION PRODUCED",
 "GÉNÉRALISATION PRODUITE":
   "GENERALIZATION PRODUCED",
 "Tout remettre au défaut":
   "Reset everything to default",
 "Familles et validation":
   "Families and validation",
 "concept(s) en remontée":
   "concept(s) set to",
 "Contrats pédagogiques":
   "Pedagogical contracts",
 "Collaboration imposée":
   "Imposed collaboration",
 "aucune généralisation":
   "no generalization",
 "Séquence à compléter":
   "Sequence to be completed",
 "Délai par activité":
   "Allowance per activity",
 "État de la cohorte":
   "Cohort state",
 "NON EXPLIQUÉES":
   "UNEXPLAINED",
 "NON EXPLIQUEES":
   "UNEXPLAINED",
 "Avertissement.":
   "Warning.",
 "délai_minutes":
   "allowance_minutes",
 "VÉRIFICATION":
   "VERIFICATION",
 "HORS FORME":
   "OFF-FORM",
 "ASSISTANCE":
   "SCAFFOLDING",
 "réglés sur":
   "set out of",
 "hors forme":
   "off-form",
 "Activités":
   "Activities",
 "APPRENANT":
   "LEARNER",
 "Contrats":
   "Contracts",
 "Réglages":
   "Settings",
 "ETAYAGES":
   "SCAFFOLDING",
 "ÉTAYAGES":
   "SCAFFOLDING",
 "REMONTÉE":
   "ABSTRACTION",
 "SÉQUENCE":
   "SEQUENCE",
 "Groupes":
   "Groups",
 "Cohorte":
   "Cohort",
 "Relevés":
   "Records",
 "PALIER":
   "TIER",
 "RÉGIME":
   "REGIME",
 "Étude":
   "Study",
 "DÉLAI":
   "ALLOWANCE",
 "RÉGLÉ":
   "SET",
 " sur ":
   " on ",
 "ETAT":
   "STATE",
 "ÉTAT":
   "STATE",

 # --- lignes de contrat et pluriels
 "Contrat : assistance indices": "Contract: scaffolding on request",
 "Contrat : assistance guidage": "Contract: scaffolding proactive",
 "Contrat : assistance aucune": "Contract: scaffolding none",
 "Contrat : assistance": "Contract: scaffolding",
 "remontée decouverte": "abstraction discovery",
 "remontée guidee": "abstraction guided",
 "remontée exposee": "abstraction exposed",
 "regime libre": "regime free",
 "regime solo": "regime solo",
 "sequence libre": "sequence free",
 "1 points de variation": "1 variation point",
 "1 point de variation": "1 variation point",
 "1 chose qui change": "1 thing that changes",
 "mode decouverte": "discovery mode",
 "mode guide": "guided mode",
 "sans contrainte de temps": "no time allowance",
 "Aucune solution enregistrée pour ce concept.":
   "No solution recorded for this concept.",
 "Ecartees de l'alignement :": "Set aside from the alignment:",
 "Problemes resolus autrement :": "Problems solved otherwise:",
 "Ces reussites sont enregistrees ; elles ne servent simplement pas à la comparaison.":
   "These successes are recorded; they simply do not serve the comparison.",
 "Solutions au dossier :": "Solutions in the dossier:",
 "au minimum.": "at least.",
 "Ce qui change d'une solution à l'autre :":
   "What varies from one solution to the next:",
 "le tuteur en cherche": "the tutor is looking for",
 "et le compte ne bouge plus": "and the count no longer moves",
 "Ce qu'il faut atteindre : écrire assez de solutions comparables, y trouver ce qu'elles ont en commun, puis l'employer sans y être invite.":
   "What has to be reached: write enough comparable solutions, find what they share, then use it unprompted.",
 "Le tuteur ne vous montrera vos solutions ensemble que lorsque ce compte sera atteint et stable. Il n'y a rien à mémoriser d'ici la.":
   "The tutor will show your solutions together only once that count is reached and stable. There is nothing to memorise until then.",
 "Une activité de plus vous est servie.": "One more activity is served to you.",

 # --- libelles de concepts
 "Expressions, valeurs, types": "Expressions, values, types",
 "Listes et filtrage par motifs": "Lists and pattern matching",
 "Récursion structurelle": "Structural recursion",
 "Les trois schemas": "The three schemas",
 "Ordre supérieur": "Higher order",
 "Types definis par l'utilisateur": "User-defined types",
 "Classes de types": "Type classes",
 "Échec, choix, effets": "Failure, choice, effects",
 "Evaluation paresseuse": "Lazy evaluation",
 "Le compilateur connaît le type avant l'exécution":
   "The compiler knows the type before execution",
 "Une liste est une structure recursive, pas un tableau":
   "A list is a recursive structure, not an array",
 "Cas de base, cas récursif, decroissance sur la structure":
   "Base case, recursive case, decrease on the structure",
 "Transformer chaque élément": "Transform each element",
 "Garder ou ecarter selon une condition": "Keep or discard on a condition",
 "Réduire une liste a une valeur": "Reduce a list to a value",
 "Une fonction à deux arguments en est une a un argument":
   "A two-argument function is a one-argument function",
 "Enchainer deux fonctions sans nommer la valeur intermédiaire":
   "Chain two functions without naming the intermediate value",
 "Un type est une somme de constructeurs": "A type is a sum of constructors",
 "La récursion suit la forme du type, pas celle de la liste":
   "Recursion follows the shape of the type, not that of the list",
 "Une même opération sur des types differents":
   "One operation on several types",
 "map se generalise au-dela des listes": "map generalises beyond lists",
 "Une fonction qui peut échouer le dit dans son type":
   "A function that may fail says so in its type",
 "Enchainer des calculs qui peuvent échouer":
   "Chain computations that may fail",
 "Ce qui sort du programme est marque dans le type":
   "What leaves the program is marked in the type",
 "Ce qui n'est pas demande n'est pas calcule":
   "What is not asked for is not computed",
 "Deux plis, deux comportements en memoire":
   "Two folds, two behaviours in memory",

 # --- enonces d'activite, familles executables
 "Des quantites a convertir : multipliez chaque élément par deux.":
   "Quantities to convert: multiply each element by two.",
 "Mettez chaque chaîne en majuscules.": "Put each string in upper case.",
 "Donnez la premiere lettre de chaque chaîne.":
   "Give the first letter of each string.",
 "Une liste de prenoms : donnez la premiere lettre de chacun.":
   "A list of first names: give the first letter of each.",
 "Des mesures a mettre au carre.": "Measurements to square.",
 "Un relevé nom-note. Ne gardez que les notes.":
   "A name-and-mark record. Keep only the marks.",
 "Un relevé de couples (nom, note) : ne gardez que les notes.":
   "A record of (name, mark) pairs: keep only the marks.",
 "Des numéros de place : ne gardez que les pairs.":
   "Seat numbers: keep only the even ones.",
 "Des champs de formulaire : écartez ceux laisses vides.":
   "Form fields: discard those left empty.",
 "Des notes sur cent : ne gardez que celles qui atteignent soixante.":
   "Marks out of a hundred: keep only those that reach sixty.",
 "Des mots : ne gardez que ceux de plus de trois lettres.":
   "Words: keep only those longer than three letters.",
 "Le total des relevés de temperature.": "The total of the temperature readings.",
 "Des relevés de temperature : donnez le total.":
   "Temperature readings: give the total.",
 "Un facteur d'echelle par étage : donnez le facteur global.":
   "One scale factor per floor: give the overall factor.",
 "Un inventaire dont les éléments importent peu : comptez-les.":
   "An inventory whose items matter little: count them.",
 "Des paragraphes découpés en listes de mots : remettez-les bout a bout.":
   "Paragraphs split into word lists: put them end to end.",
 "Des morceaux de texte : recollez-les en une seule chaîne.":
   "Pieces of text: join them into a single string.",
 "Changez le signe de chaque élément.": "Change the sign of each element.",
 "Donnez la longueur de chaque chaîne.": "Give the length of each string.",
 "Ne gardez que les nombres strictement positifs.":
   "Keep only the strictly positive numbers.",
 "Ne gardez que les voyelles d'un texte.": "Keep only the vowels of a text.",
 "Le plus grand élément d'une liste non vide.":
   "The largest element of a non-empty list.",
 "Plusieurs verifications : toutes ont-elles réussi ?":
   "Several checks: did they all pass?",

 # --- interface etudiante simplifiee (2026-10-20) : vocabulaire et disposition
 "2 · Mode de travail": "2 · Way of working",
 "Mode de travail": "Way of working",
 "4 · Exercices": "4 · Exercises",
 "Ce que vous apprenez": "What you are learning",
 "Les paliers s'ouvrent dans l'ordre : un palier marqué « plus tard » s'ouvre quand "
 "le précédent est acquis. Un palier est acquis quand vous réutilisez par vous-même ce "
 "que vous avez découvert, pas seulement quand vous réussissez les exercices.":
   "Stages open in order: a stage marked \"later\" opens once the previous one is "
   "acquired. A stage is acquired when you reuse what you discovered on your own, "
   "not just when you solve the exercises.",
 "Nouvel exercice": "New exercise",
 "Code fourni : il est déjà là, vous n'avez pas à le modifier.":
   "Provided code: it is already there, you do not need to change it.",
 "Écrivez votre fonction ici": "Write your function here",
 ", à la place de": ", in place of",
 "Dans les messages d'erreur, les numéros de ligne comptent aussi les lignes de ce code "
 "fourni.": "In error messages, line numbers also count the lines of this provided code.",
 "Demander un indice": "Ask for a hint",
 "Indices épuisés": "Hints used up",
 "Trois indices par exercice, du plus général au plus précis. Aucun ne donne la solution.":
   "Three hints per exercise, from the most general to the most precise. None gives "
   "the solution.",
 "le tuteur vous propose un indice.": "the tutor offers you a hint.",
 "demander un indice.": "ask for a hint.",
 "à propos de votre dernière erreur :": "about your last error:",
 "Atelier : ce que vos fonctions ont en commun": "Workshop: what your functions share",
 "Comparer vos solutions, avec le tuteur": "Comparing your solutions, with the tutor",
 "élément(s) qui changent d'une fonction à l'autre":
   "element(s) that change from one function to the next",
 "Votre fonction": "Your function",
 "Cas récursif": "Recursive case",
 "désigne un appel récursif de la fonction sur une partie plus petite de l'entrée. "
 "Les valeurs propres à chaque fonction sont gardées telles que vous les avez écrites.":
   "stands for a recursive call of the function on a smaller part of the input. The "
   "values specific to each function are kept as you wrote them.",
 "Écrivez ici une seule fonction qui peut remplacer toutes celles du tableau":
   "Write here a single function that can replace all those in the table",
 "Elle est conservée, et servira si vous travaillez en groupe.":
   "It is kept, and will be used if you work in a group.",
 "Valider ma fonction": "Submit my function",
 "Pas encore : un exercice de plus": "Not yet: one more exercise",
 "Quand un exercice est réussi :": "When an exercise is solved:",
 "passer au suivant": "go to the next one",
 "attendre que je clique": "wait for my click",
 "Exercice suivant": "Next exercise",
 "Exercice suivant dans": "Next exercise in",
 "Solutions comparables :": "Comparable solutions:",
 "Réutilisations de votre découverte :": "Reuses of your discovery:",
 "Une réutilisation ne compte que si vous employez ce que vous venez de trouver, "
 "plutôt qu'une récursion écrite à la main.":
   "A reuse only counts if you use what you have just found, rather than recursion "
   "written by hand.",
 "Palier acquis.": "Stage acquired.",
 "Solution ajoutée à vos solutions comparables.":
   "Solution added to your comparable solutions.",
 "Solution juste, mais elle ne peut pas être comparée aux autres :":
   "Correct solution, but it cannot be compared with the others:",
 "Vous avez réutilisé votre découverte : la réutilisation est comptée.":
   "You reused your discovery: the reuse is counted.",
 "Solution juste, mais écrite sans réutiliser votre découverte : la réutilisation "
 "n'est pas comptée.":
   "Correct solution, but written without reusing your discovery: the reuse is not "
   "counted.",
 "Détails techniques (pour l'enseignant)": "Technical details (for the teacher)",
 "Revenir aux exercices": "Back to the exercises",
 "Le tuteur ne va pas plus loin : la suite vous appartient. Voici les indices déjà reçus.":
   "The tutor goes no further: the rest is up to you. Here are the hints already "
   "received.",
 "un exercice de plus avant l'atelier, à votre demande":
   "one more exercise before the workshop, at your request",
 "en distinguant explicitement le cas de base et le cas récursif":
   "explicitly distinguishing the base case and the recursive case",
 "1 · Écrire des solutions": "1 · Write solutions",
 "2 · Trouver ce qu'elles ont en commun": "2 · Find what they share",
 "3 · Nouveaux exercices": "3 · New exercises",
 "Palier acquis": "Stage acquired",
 "Réutilisations :": "Reuses:",
 "solutions comparées : à vous de trouver ce qui leur est commun":
   "solutions compared: your turn to find what they share",
 "Solutions écrites :": "Solutions written:",
 "la comparaison s'ouvre après 3 ou 4 solutions":
   "the comparison opens after 3 or 4 solutions",
 "exercice(s) réussi(s) autrement, enregistré(s) à part":
   "exercise(s) solved another way, recorded separately",
 "Plus d'informations : mes solutions, ce que j'apprends, mon groupe":
   "More information: my solutions, what I am learning, my group",
 "Solutions réussies :": "Solutions solved:",
 "Bravo : ce palier est terminé.": "Well done: this stage is complete.",
 "Le tuteur vous montre vos solutions ensemble : cherchez ce qu'elles ont en commun.":
   "The tutor shows you your solutions together: look for what they share.",
 "Quand vous en aurez écrit assez, le tuteur vous les montrera ensemble.":
   "Once you have written enough of them, the tutor will show them to you together.",
 "Pseudonyme": "Pseudonym",
 "Un pseudonyme, sans votre nom": "A pseudonym, not your name",
 "Code du cours": "Course code",
 "Retenez bien votre pseudonyme.": "Remember your pseudonym.",
 "Il vous servira à reprendre votre travail, et à la séance de suivi la semaine prochaine. "
 "Notez-le quelque part dès maintenant.":
   "You will need it to resume your work, and for the follow-up session next week. "
   "Write it down now.",
 "Notez votre identifiant :": "Write down your identifier:",
 "il vous permet de retrouver votre travail depuis un autre poste, et à la séance de suivi.":
   "it lets you find your work again from another computer, and at the follow-up session.",
 "Ce navigateur s'en souvient, mais un autre poste ne le saura pas.":
   "This browser remembers it, but another computer will not.",
 "Votre enseignant peut vous le redonner si vous l'oubliez.":
   "Your instructor can give it back to you if you forget it.",
 "Vous reprenez votre travail exactement où vous en êtes.":
   "You resume your work exactly where you left off.",
 "Vous travaillez depuis un autre poste ?": "Working from another computer?",
 "Saisissez l'identifiant de quatre caractères reçu à l'inscription.":
   "Enter the four-character identifier you received when you registered.",
 "Il figure aussi en haut de la page des exercices, à côté de votre pseudonyme.":
   "It also appears at the top of the exercise page, next to your pseudonym.",
 "Quatre caractères, par exemple a3f9": "Four characters, for example a3f9",
 "Reprendre avec cet identifiant": "Resume with this identifier",
 "Compilation réussie, mais certains tests échouent :":
   "Compilation succeeded, but some tests fail:",
 "Obtenu": "Got",
 "Attendu": "Expected",
 "Les arbres t0, t1, t2, t3 et example_tree sont définis dans le code fourni.":
   "The trees t0, t1, t2, t3 and example_tree are defined in the provided code.",
 "Terminé pour aujourd'hui": "Done for today",
 "Bravo, vous avez fait tous les exercices prévus pour cette séance.":
   "Well done, you have completed all the exercises planned for this session.",
 "Votre travail est enregistré. D'autres exercices vous seront proposés lors de la prochaine "
 "séance : gardez votre pseudonyme et votre identifiant.":
   "Your work is saved. More exercises will be offered at the next session: keep your "
   "pseudonym and your identifier.",
 "Vous pouvez revoir vos solutions dans « Plus d'informations », plus bas, ou retourner au "
 "laboratoire.": "You can review your solutions under \"More information\" below, or go back "
   "to the lab.",
 "Plus de nouvel exercice": "No new exercise",
 "Vous avez résolu les exercices, mais d'une autre manière que celle que le tuteur peut "
 "comparer. Pour continuer, reprenez un ou deux exercices et réécrivez-les":
   "You solved the exercises, but in a way other than the one the tutor can compare. To "
   "continue, go back to one or two exercises and rewrite them",
 "Choisir un exercice à reprendre": "Choose an exercise to redo",
 "Ce pseudonyme est déjà pris. Si c'est le vôtre, revenez à l'écran de reprise et "
 "saisissez votre identifiant ; sinon, choisissez-en un autre.":
   "This pseudonym is already taken. If it is yours, go back to the resume screen and "
   "enter your identifier; otherwise, choose another one.",
 "Chaque pseudonyme ne peut servir qu'une fois": "Each pseudonym can only be used once",
 "s'il est déjà pris, le tuteur vous demandera d'en choisir un autre.":
   "if it is already taken, the tutor will ask you to choose another one.",
 "Que rend votre fonction dans le cas de base ?":
   "What does your function return in the base case?",
 "C'est la valeur de votre cas de base : ce que la fonction doit rendre sur l'entrée la "
 "plus simple, d'après l'énoncé.":
   "It is the value of your base case: what the function must return on the simplest "
   "input, according to the statement.",
}

# etiquettes courtes, substituees en mot entier seulement
ETIQUETTES = {
 "instance": "instance", "remontee": "abstraction", "abstraction": "abstraction",
 "reemploi": "reuse", "guidage": "guidance", "acquis": "acquired",
 "generalise": "generalised", "instances": "instances",
 "solo": "solo", "libre": "free", "oui": "yes", "non": "no",
 "toujours": "always", "jamais": "never",
 
}

_ENTREES = None


def _entrees():
    global _ENTREES
    if _ENTREES is None:
        _ENTREES = sorted(CATALOGUE.items(), key=lambda kv: -len(kv[0]))
    return _ENTREES


def traduire_texte(s, langue="en"):
    """Substitution en une passe : les portions deja traduites sont figees."""
    if langue == "fr" or not isinstance(s, str) or not s:
        return s
    morceaux = [(s, False)]                      # (texte, deja traduit)
    for fr, en in _entrees():
        suivants = []
        for texte, fige in morceaux:
            if fige or fr not in texte:
                suivants.append((texte, fige))
                continue
            parts = texte.split(fr)
            for i, p in enumerate(parts):
                if i:
                    suivants.append((en, True))
                if p:
                    suivants.append((p, False))
        morceaux = suivants
    sortie = "".join(t for t, _ in morceaux)
    for fr, en in ETIQUETTES.items():
        if fr != en:
            sortie = re.sub(r"(?<![\w-])%s(?![\w-])" % re.escape(fr), en, sortie)
    return sortie


def traduire(obj, langue="en"):
    if langue == "fr":
        return obj
    if isinstance(obj, str):
        return traduire_texte(obj, langue)
    if isinstance(obj, list):
        return [traduire(x, langue) for x in obj]
    if isinstance(obj, dict):
        return {k: (v if k in ("code", "canon", "message_ghc", "message", "texte_generalisation")
                    else traduire(v, langue)) for k, v in obj.items()}
    return obj


def catalogue_json():
    """Le catalogue, pour que les clients traduisent leurs propres libelles."""
    return {"phrases": CATALOGUE, "etiquettes": ETIQUETTES}
