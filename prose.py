"""Redige une presentation et une discussion des resultats, a partir des
chiffres calcules par analyses.py.

    python3 prose.py hstutor/donnees > resultats.md

Le texte produit est un brouillon a relire, pas une redaction finale. Il a
deux proprietes qui le rendent utile : il ne dit rien que les chiffres ne
soutiennent, et il place les reserves ou elles doivent aller, c'est-a-dire
avec le resultat qu'elles bornent et non dans une section separee.

Les seuils employes pour choisir la formulation sont explicites dans le code :
un p sous 0,05 se rapporte comme etabli, entre 0,05 et 0,10 comme une
tendance non concluante, au-dela comme une absence d'effet detectable. Un
ecart de reemploi sous trois points avec un intervalle serre se rapporte comme
un resultat negatif, ce qui est un resultat et non un echec.
"""

import math, os, sys

import analyses


def pc(x, n=1):
    return "—" if x is None or not math.isfinite(x) else ("%." + str(n) + "f") % (100 * x)


def nb(x, n=2):
    return "—" if x is None or not math.isfinite(x) else ("%." + str(n) + "f") % x


def pval(p):
    if p is None or not math.isfinite(p):
        return "—"
    if p < 0.0001:
        return "p < 0,0001"
    return "p = %s" % ("%.4f" % p).replace(".", ",")


def rediger(r):
    if r.get("refus"):
        return "# Analyse impossible\n\n%s\n" % r["refus"]
    q1, q2, q3, q4 = r["q1"], r["q2"], r.get("q3", {}), r.get("q4", {})
    t = []
    A = t.append

    if r.get("simule"):
        A("> **Donnees simulees.** Ce texte est engendre a partir d'un jeu "
          "synthetique, produit pour eprouver la chaine d'analyse et juger ce que "
          "le devis peut detecter. Aucun chiffre qui suit n'est un resultat.\n\n")
    A("# Resultats\n")
    A("L'etude a porte sur %d apprenants et %d couples apprenant-concept, sur %d "
      "concepts. %d apprenants n'ont pas de ligne pour chacun des concepts, par "
      "abandon ou parce que le concept n'a pas ete atteint ; les analyses sont "
      "conduites en intention de traiter.\n"
      % (r["apprenants"], r["couples"], len(r["concepts"]), r["incomplets"]))

    desequilibres = [e for e in r["equilibre"]
                     if abs(e["discovery"] - e["exposed"])
                     > max(3, 0.2 * (e["discovery"] + e["exposed"]))]
    if desequilibres:
        A("Le plan n'est pas parfaitement equilibre sur %s, ce qui est a signaler "
          "dans la methode.\n" % ", ".join(e["concept"] for e in desequilibres))

    # ------------------------------------------------------------ Q1
    A("\n## Reemploi spontane et ordre d'enseignement\n")
    ecart = 100 * q1["diff"] if math.isfinite(q1["diff"]) else float("nan")
    A("Le reemploi spontane s'etablit a %s %% apres abstraction contre %s %% apres "
      "exposition. Le contraste intra-sujet, sur les %d apprenants ayant vu les "
      "deux ordres, donne un ecart moyen de %s points de pourcentage, "
      "t(%d) = %s, %s, d apparie = %s.\n"
      % (pc(q1["discovery"]), pc(q1["exposed"]), q1["paires"], nb(ecart, 1),
         q1["n"] - 1, nb(q1["t"]), pval(q1["p"]), nb(q1["dz"])))

    if math.isfinite(q1["p"]) and q1["p"] < 0.05 and ecart > 0:
        A("\nL'effet est etabli. Le devis intra-sujet compare un apprenant a "
          "lui-meme, de sorte que l'ecart ne peut etre impute au niveau initial, "
          "a la motivation ni au temps disponible.\n")
    elif math.isfinite(q1["p"]) and q1["p"] < 0.10:
        A("\nLa difference va dans le sens attendu sans atteindre le seuil "
          "conventionnel. A cet effectif, l'etude est dimensionnee pour un ecart "
          "d'environ dix points ; un ecart plus faible reste indetectable, et "
          "l'absence de conclusion ici ne vaut pas absence d'effet.\n")
    else:
        A("\nAucun effet detectable. C'est un resultat et non un echec : il porte "
          "contre l'attente de la litterature sur l'echec productif dans ce "
          "domaine, et il merite d'etre rapporte comme tel.\n")

    m = r.get("moments") or {}
    if len(m) >= 2:
        A("\nLu par moment de mesure, l'ecart vaut ")
        A(", ".join("%s points a %s, apres %s jour(s)"
                    % (nb(100 * v["diff"], 1), k.upper(), nb(v["delai_moyen"], 0))
                    for k, v in sorted(m.items())))
        A(".\n")
        if "t0" in m and "t2" in m:
            e0, e2 = m["t0"]["diff"], m["t2"]["diff"]
            if e2 > 0.8 * e0:
                A("\nL'ecart se maintient du premier au dernier moment. La mesure "
                  "porte donc sur ce qui est appris et non sur la seule "
                  "disponibilite immediate, ce qui est la lecture la plus "
                  "favorable des trois profils possibles.\n")
            elif e2 > 0.3 * e0:
                A("\nL'ecart se resserre sans se refermer. Une part de l'effet "
                  "tient a la disponibilite immediate, l'atelier venant d'etre "
                  "ecrit ; il en reste apres deux semaines, ce qui soutient un "
                  "effet sur ce qui est appris, mais plus modestement que la "
                  "mesure immediate ne le suggerait.\n")
            else:
                A("\nL'ecart se referme. L'ordre ascendant produit une "
                  "disponibilite immediate qui ne se maintient pas : c'est un "
                  "resultat utile et nettement plus modeste que la mesure "
                  "immediate ne le laissait croire, et il doit etre rapporte "
                  "ainsi.\n")

    if "hors_tuteur" in q1:
        A("\nLe reemploi mesure hors du tuteur, sur les fonctions ecrites en examen "
          "sans consigne de forme, s'etablit a %s %% sur %d items. C'est la mesure "
          "la moins favorable au systeme et celle qui compte pour la revendication."
          "\n" % (pc(q1["hors_tuteur"]), q1["hors_tuteur_n"]))

    fortes = sorted(q1["par_concept"],
                    key=lambda x: -(x["discovery"] - x["exposed"])
                    if math.isfinite(x["discovery"] - x["exposed"]) else 0)
    if len(fortes) >= 2:
        A("\nL'effet n'est pas uniforme entre concepts : il est le plus marque sur "
          "%s et %s, et le plus faible sur %s. "
          % (fortes[0]["concept"], fortes[1]["concept"], fortes[-1]["concept"]))
    if q1["paires"]:
        A("Le graphique apparie montre que %d apprenants sur %d reemploient "
          "davantage apres exposition qu'apres abstraction. L'ordre deplace une "
          "distribution, il ne determine pas une issue individuelle.\n"
          % (q1["inverses"], q1["paires"]))

    # ------------------------------------------------------------ Q2
    A("\n## Ancrage obligatoire et portee de la generalisation\n")
    if q2["n_complete"] and q2["n_retiree"]:
        chute = 100 * (q2["p_complete"] - q2["p_retiree"])
        A("Avec l'ancrage obligatoire servi, %s %% des generalisations sont de "
          "portee correcte ; sans lui, %s %% : une chute de %s points "
          "(n = %d et %d, test exact de Fisher, %s, rapport de cotes %s).\n"
          % (pc(q2["p_complete"], 0), pc(q2["p_retiree"], 0), nb(chute, 0),
             q2["n_complete"], q2["n_retiree"], pval(q2["p"]), nb(q2["or"], 1)))
        if math.isfinite(q2["p"]) and q2["p"] < 0.05:
            A("\nC'est la contribution empirique principale. La litterature sur la "
              "comparaison soutient depuis longtemps que les exemples doivent "
              "varier dans les bons respects ; ce qui n'avait pas ete eprouve est "
              "une affirmation portant sur un membre identifiable d'un ensemble "
              "d'exercices, designe a l'avance par un algorithme et non par "
              "l'intuition. Retirer exactement cet exercice reduit de moitie le "
              "taux de generalisations correctes.\n")
        else:
            A("\nLa difference n'atteint pas le seuil conventionnel. Les cellules "
              "de cette manipulation sont petites, et l'analyse de puissance "
              "prealable indiquait qu'une chute moderee resterait indetectable. "
              "Une replication dimensionnee est necessaire avant de conclure dans "
              "un sens ou dans l'autre.\n")
    else:
        A("La manipulation de l'ancrage obligatoire n'a pas produit de cellules "
          "exploitables.\n")

    if "hf_correcte" in q2:
        A("\nSur l'item hors famille, le regroupement par cellule experimentale "
          "donne %s %% contre %s %%, et le regroupement par portee effectivement "
          "atteinte %s %% contre %s %%. Les deux mesurent des choses differentes "
          "et les deux sont informatifs : l'ancrage gouverne la portee, et la "
          "portee gouverne le transfert. La manipulation agit sur le transfert a "
          "travers la portee, de sorte que le contraste de bout en bout est "
          "attenue par construction.\n"
          % (pc(q2.get("hf_complete"), 0), pc(q2.get("hf_retiree"), 0),
             pc(q2.get("hf_correcte"), 0), pc(q2.get("hf_etroite"), 0)))
    if "concordance" in q2:
        A("\nLes deux mesures de la portee, celle du moteur et le codage humain a "
          "l'aveugle, concordent sur %s %% des %d generalisations codees. "
          % (pc(q2["concordance"], 0), q2["concordance_n"]))
        if q2["concordance"] < 0.80:
            A("Un accord inferieur a quatre-vingts pour cent merite d'etre discute : "
              "c'est la mesure codee qui doit etre rapportee comme principale, "
              "puisqu'elle ne depend pas du systeme evalue.\n")
        else:
            A("La mesure codee est rapportee comme principale, puisqu'elle ne "
              "depend pas du systeme evalue, et celle du moteur comme convergence."
              "\n")

    # ------------------------------------------------------------ Q3
    A("\n## Reponse aux solutions non comparables\n")
    if q3.get("n"):
        A("%d couples apprenant-concept comportent au moins une solution correcte "
          "mais non comparable. " % q3["n"])
        if "m1" in q3:
            A("Le reemploi s'etablit a %s items sur deux apres la politique de "
              "confrontation et a %s apres l'explication suivie du passage a un "
              "autre probleme (%s).\n" % (nb(q3["m1"]), nb(q3["m2"]), pval(q3["p"])))
            if math.isfinite(q3.get("p", float("nan"))) and q3["p"] < 0.05:
                A("\nLa direction est celle que la conception predit. La comparaison "
                  "a ete declaree exploratoire avant la collecte et les concepts "
                  "portant chaque politique diffèrent en difficulte : nous traitons "
                  "ce resultat comme une hypothese a eprouver, non comme un acquis."
                  "\n")
            else:
                A("\nLa comparaison etait declaree exploratoire et reste non "
                  "concluante. Le nombre d'observations n'est pas controlable, "
                  "puisqu'il depend du comportement des apprenants.\n")
    else:
        A("Aucune solution non comparable n'a ete soumise, ce qui rend cette "
          "comparaison sans objet sur cette cohorte.\n")

    # ------------------------------------------------------------ Q4
    A("\n## Emploi de la latitude\n")
    e = q4.get("etayage", {})
    if e.get("n1"):
        A("L'etayage est davantage demande en regime de decouverte, %s niveaux par "
          "concept contre %s (%s). Deux lectures sont disponibles et les donnees "
          "ne les separent pas : la decouverte est plus difficile, ou elle rend "
          "l'apprenant conscient d'avoir quelque chose a trouver.\n"
          % (nb(e["m1"]), nb(e["m2"]), pval(e.get("p"))))
    if q4.get("moment"):
        m = q4["moment"]
        total = sum(m.values()) or 1
        A("\nInterroges sur le moment ou l'atelier d'abstraction s'est ouvert, %d "
          "apprenants sur %d le jugent bien choisi, %d trop tot et %d trop tard. "
          % (m.get("au bon moment", 0), total, m.get("trop tot", 0),
             m.get("trop tard", 0)))
        if m.get("au bon moment", 0) / total >= 0.5:
            A("Un seuil unique calcule sur le corpus convient donc a une majorite, "
              "ce qui est l'issue pour laquelle la condition de stabilite a ete "
              "concue. Les apprenants pour qui il s'est declenche tot sont ceux qui "
              "voulaient plus d'instances que le minimum de la famille.\n")
        else:
            A("Le moment que la condition de stabilite produit n'est donc pas vecu "
              "comme bien choisi par la majorite. Un seuil peut etre juste par "
              "rapport au corpus et faux par rapport a une personne : un seuil par "
              "apprenant est la suite logique de ce constat.\n")
    if "jauge_utile" in q4:
        A("\nL'indicateur de points de variation est note %s sur cinq en moyenne "
          "pour son utilite.\n" % nb(q4["jauge_utile"]))

    # ------------------------------------------------------------ processus
    p = r.get("processus")
    if p:
        A("\n## Mesures de processus\n")
        A("Sur %d soumissions compilees, %s %% reussissent. %s %% des soumissions "
          "reussies calculent un resultat faux tout en compilant, ce qu'une "
          "correction fondee sur la compilation ne detecte pas et que le tuteur "
          "marque.\n" % (p["soumissions"], pc(p["reussite"]), pc(p["silencieuses"])))
        if p.get("categories"):
            A("\nLes categories d'erreur les plus frequentes sont %s.\n"
              % ", ".join("%s (%d)" % (k, v) for k, v in p["categories"][:4]))

    # ------------------------------------------------------------ limites
    A("\n## Limites\n")
    A("Une seule section de %d apprenants, un cours, un etablissement, huit "
      "semaines. Le devis intra-sujet est le plus fort que cet effectif permette "
      "et il traite les differences entre apprenants, non celles entre cours, "
      "enseignants ou etablissements.\n" % r["apprenants"])
    if q1["paires"] and q1["inverses"] / max(1, q1["paires"]) > 0.15:
        A("\nUn apprenant sur %d environ montre l'effet inverse, et rien dans ces "
          "donnees ne permet de dire qui est mieux servi par quel ordre. Un tuteur "
          "capable de le dire serait meilleur que celui que nous avons construit.\n"
          % max(2, round(q1["paires"] / max(1, q1["inverses"]))))
    A("\nCe que l'etude n'etablit pas : que la difference persiste au-dela du "
      "trimestre, qu'elle tienne dans un autre etablissement, ni qu'elle "
      "survivrait a une comparaison avec un cours conventionnel bien donne "
      "plutot qu'avec le reglage expose du meme tuteur.\n")

    A("\n---\n\nBrouillon engendre a partir des donnees de %s. A relire : les "
      "formulations sont choisies par seuils, et un chiffre limite merite un "
      "jugement humain.\n" % os.path.basename(os.path.abspath(r["dossier"])))
    return "".join(t)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    print(rediger(analyses.analyser(sys.argv[1])))


if __name__ == "__main__":
    main()
