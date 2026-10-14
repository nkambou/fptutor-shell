#!/bin/bash
# Relance d'OCamlTutor avec remise a zero de l'etat.
#
#   ./relancer.sh             sauvegarde puis efface l'etat, et relance
#   ./relancer.sh -y          idem, sans demander confirmation
#   ./relancer.sh --garder    relance sans toucher a l'etat
#
# A lancer depuis le dossier FPTutor. Le script :
#   1. arrete le tuteur qui occupe deja le port ;
#   2. met de cote les fichiers d'etat dans sauvegardes/, puis les efface ;
#   3. verifie que les fichiers modifies sont bien en place ;
#   4. relance le tuteur et controle qu'il sert la bonne version.
# Control-C arrete le tuteur.
#
# referentiel.json n'est jamais touche : c'est la configuration, pas un etat.
# Si le fichier ocamltutor/COLLECTE_EN_COURS existe, la remise a zero est
# refusee : il protege les donnees reelles pendant l'experimentation.

set -u
PORT="${PORT:-8081}"
TUTEUR="${TUTEUR:-ocamltutor}"
COHORTE="${TUTOR_COHORTE:-INF6120-A26}"
ETATS="etat.json journal.jsonl suivi_config.json suivi_etat.json suivi_journal.jsonl"

GARDER=0; OUI=0
for a in "$@"; do
  case "$a" in
    --garder) GARDER=1 ;;
    -y|--oui) OUI=1 ;;
    -h|--aide) sed -n '2,19p' "$0"; exit 0 ;;
    *) echo "option inconnue : $a (voir --aide)"; exit 2 ;;
  esac
done

ok()   { printf "  [ok ] %s\n" "$1"; }
non()  { printf "  [NON] %s\n" "$1"; }
titre(){ printf "\n%s\n" "$1"; }

if [ ! -f serveur.py ] || [ ! -d "$TUTEUR" ]; then
  echo "A lancer depuis le dossier FPTutor, qui contient serveur.py et $TUTEUR/."
  exit 1
fi

# ------------------------------------------------------------- 1. arret
titre "1. Arret du tuteur en cours"
PIDS=""
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:"$PORT" 2>/dev/null)
else
  PIDS=$(pgrep -f "serveur.py" 2>/dev/null)
fi
if [ -n "$PIDS" ]; then
  kill $PIDS 2>/dev/null; sleep 1
  kill -9 $PIDS 2>/dev/null
  ok "processus arrete sur le port $PORT"
else
  ok "aucun tuteur ne tournait sur le port $PORT"
fi

# ------------------------------------------------ 2. remise a zero de l'etat
titre "2. Etat du tuteur"
if [ "$GARDER" = 1 ]; then
  ok "etat conserve (--garder)"
elif [ -f "$TUTEUR/COLLECTE_EN_COURS" ]; then
  non "COLLECTE_EN_COURS present : remise a zero refusee, etat conserve"
  echo "        (supprimez ce fichier seulement si la collecte est terminee)"
else
  PRESENTS=""
  for f in $ETATS; do [ -f "$TUTEUR/$f" ] && PRESENTS="$PRESENTS $f"; done
  if [ -z "$PRESENTS" ]; then
    ok "aucun fichier d'etat : depart propre"
  else
    if [ "$OUI" != 1 ]; then
      printf "  Effacer l'etat (%s ) ? Une copie sera gardee. [o/N] " "$PRESENTS"
      read -r rep
      case "$rep" in o|O|oui|OUI) ;; *) echo "  etat conserve"; PRESENTS="";; esac
    fi
    if [ -n "$PRESENTS" ]; then
      SAUV="sauvegardes/$(date +%Y%m%d-%H%M%S)"
      mkdir -p "$SAUV"
      for f in $PRESENTS; do mv "$TUTEUR/$f" "$SAUV/"; done
      ok "etat mis de cote dans $SAUV, puis efface"
    fi
  fi
fi

# ------------------------------------------ 3. fichiers modifies en place
titre "3. Versions des fichiers"
verifie() { # fichier motif libelle
  if [ -f "$1" ] && grep -q "$2" "$1"; then ok "$3"; else non "$3 : $1 n'est pas a jour"; MANQUE=1; fi
}
MANQUE=0
verifie serveur.py "pseudonyme_refuse" "serveur.py, pseudonyme sans donnee nominative"
verifie serveur.py "extension.py" "serveur.py, point d'extension"
verifie etudiant.html "Pseudonyme, sans votre nom" "etudiant.html, inscription par pseudonyme"
verifie "$TUTEUR/language_ml.py" "compilateur" "language_ml.py, nom du compilateur"
verifie "$TUTEUR/extension.py" "PAGES" "extension.py, seance de suivi"
verifie "$TUTEUR/console_extension.html" "Aperçu étudiant" "console_extension.html, volet de suivi"
verifie "$TUTEUR/suivi_serveur.py" "apercu" "suivi_serveur.py, apercu"
[ -f "$TUTEUR/referentiel.json" ] && ok "referentiel.json present" || { non "referentiel.json absent"; MANQUE=1; }
[ "$MANQUE" = 1 ] && echo "  Reprenez les fichiers signales dans l'archive de deploiement."

# ------------------------------------------------------- 4. interprete OCaml
titre "4. Interprete OCaml"
if [ -z "${OCAML_BIN:-}" ]; then
  if command -v ocaml >/dev/null 2>&1; then
    OCAML_BIN=$(command -v ocaml)
  elif [ -x "$TUTEUR/faux_compilateur.py" ]; then
    OCAML_BIN="$PWD/$TUTEUR/faux_compilateur.py"
  fi
fi
case "${OCAML_BIN:-}" in
  "") non "aucun interprete : installez OCaml ou definissez OCAML_BIN"; exit 1 ;;
  *faux_compilateur*) non "SUBSTITUT de compilateur : essai seulement, jamais en seance" ;;
  *) ok "$OCAML_BIN ($("$OCAML_BIN" -version 2>/dev/null | head -1))" ;;
esac
export OCAML_BIN

# ------------------------------------------------------------ 5. relance
titre "5. Relance"
export TUTOR_DIR="$TUTEUR" TUTOR_LANGUAGE=language_ml TUTOR_COHORTE="$COHORTE" PORT
python3 serveur.py > tuteur.log 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null; echo; echo "Tuteur arrete."; exit 0' INT TERM

PRET=0
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s "http://localhost:$PORT/api/version" >/dev/null 2>&1; then PRET=1; break; fi
  sleep 1
done
if [ "$PRET" != 1 ]; then
  non "le tuteur ne repond pas ; derniers messages :"
  tail -15 tuteur.log
  kill $PID 2>/dev/null; exit 1
fi
PAGE=$(curl -s "http://localhost:$PORT/")
echo "$PAGE" | grep -q "OCamlTutor" && ok "titre OCamlTutor" || non "le titre n'est pas OCamlTutor"
echo "$PAGE" | grep -q "Pseudonyme, sans votre nom" && ok "inscription par pseudonyme" || non "ancienne page d'inscription"
echo "$PAGE" | grep -q "compilées par OCaml" && ok "compilateur annonce : OCaml" || non "la page n'annonce pas OCaml"
curl -s "http://localhost:$PORT/enseignant" | grep -q "Séance de suivi" && ok "volet de suivi dans la console" || non "volet de suivi absent de la console"
curl -s "http://localhost:$PORT/api/ext/statut" | grep -q '"ouvert": false' && ok "suivi masque aux etudiants" || non "le suivi n'est pas masque"

cat <<FIN

  Etudiants   http://localhost:$PORT/
  Console     http://localhost:$PORT/enseignant
  Apercu      http://localhost:$PORT/suivi?apercu=1

  Rechargez les pages avec Cmd+Maj+R. Journal du tuteur : tuteur.log
  Control-C pour arreter.
FIN
wait $PID
