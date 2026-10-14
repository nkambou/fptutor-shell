#!/usr/bin/env bash
# Batterie de verification d'une instance, a lancer depuis la racine du depot.
#
#   outils/verifier.sh exemples/ocamltutor language_ml cas_ml.json
#   outils/verifier.sh exemples/rackettutor language_rkt cas_rkt.json
#
# Quatre controles, dans l'ordre ou ils doivent passer. Le premier qui echoue
# arrete la batterie : rien ne sert de valider les familles si les solutions de
# reference ne compilent pas.
set -u
TUTEUR="${1:-exemples/ocamltutor}"
LANGUE="${2:-language_ml}"
CAS="${3:-cas_ml.json}"
echec=0

titre() { printf "\n\033[1m== %s\033[0m\n" "$1"; }
bilan() { if [ "$1" = 0 ]; then printf "  \033[32mok\033[0m\n"; else printf "  \033[31mECHEC\033[0m\n"; echec=1; fi; }

titre "1. Solutions de reference (compilateur reel)"
python3 "$TUTEUR/compiler_references.py"; bilan $?
[ "$echec" = 1 ] && exit 1

titre "2. Banc d'essai du fournisseur (reunion, separation, messages)"
( cd fptutor-shell && python3 banc_essai.py "$LANGUE" --tuteur "$TUTEUR" --cas "../$TUTEUR/$CAS" ); bilan $?
[ "$echec" = 1 ] && exit 1

titre "3. Familles et obligations"
TUTOR_DIR="$TUTEUR" TUTOR_LANGUAGE="$LANGUE" python3 obligations.py; bilan $?

titre "4. Essai a blanc d'une session complete"
python3 "$TUTEUR/essai_a_blanc.py"; bilan $?

printf "\n"
[ "$echec" = 0 ] && echo "Batterie complete : rien a signaler." || echo "Batterie incomplete : voir ci-dessus."
exit $echec
