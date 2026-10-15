#!/usr/bin/env bash
# Mise a jour du depot, en une commande, depuis n'importe ou dans l'arborescence.
#
#   outils/pousser.sh                          applique la derniere archive puis pousse
#   outils/pousser.sh -m "mon message"         message de commit explicite
#   outils/pousser.sh --sans-archive           pousse les modifications locales seules
#   outils/pousser.sh --archive chemin.zip     applique cette archive-la
#   outils/pousser.sh --essai                  montre ce qui serait fait, sans rien faire
#
# Par defaut, le script cherche l'archive maj-*.zip la plus recente dans
# ~/Downloads, la decompresse a la racine du depot, montre ce qui change, demande
# confirmation, puis valide et pousse.
set -u

ARCHIVE=""
AVEC_ARCHIVE=1
MESSAGE=""
ESSAI=0
TELECHARGEMENTS="${TELECHARGEMENTS:-$HOME/Downloads}"

while [ $# -gt 0 ]; do
  case "$1" in
    -m|--message)     MESSAGE="${2:-}"; shift 2 ;;
    --archive)        ARCHIVE="${2:-}"; shift 2 ;;
    --sans-archive)   AVEC_ARCHIVE=0; shift ;;
    --essai)          ESSAI=1; shift ;;
    -h|--help)        sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Option inconnue : $1"; exit 2 ;;
  esac
done

annoncer() { printf "\n\033[1m== %s\033[0m\n" "$1"; }
echouer()  { printf "\033[31m%s\033[0m\n" "$1"; exit 1; }

# ------------------------------------------------------------ 1. le depot
RACINE="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || echouer "Ce dossier n'est pas un depot git. Placez-vous dans le depot cloné."
cd "$RACINE" || exit 1
DISTANT="$(git remote get-url origin 2>/dev/null || echo 'aucun')"
echo "Depot   : $RACINE"
echo "Distant : $DISTANT"
[ "$DISTANT" = "aucun" ] && echouer "Aucun depot distant : git remote add origin <url>"

# ------------------------------------------------------------ 2. l'archive
if [ "$AVEC_ARCHIVE" = 1 ]; then
  if [ -z "$ARCHIVE" ]; then
    ARCHIVE="$(ls -t "$TELECHARGEMENTS"/maj-*.zip 2>/dev/null | head -1)"
  fi
  if [ -z "$ARCHIVE" ]; then
    echo "Aucune archive maj-*.zip dans $TELECHARGEMENTS : seules les modifications locales seront poussees."
  elif [ ! -f "$ARCHIVE" ]; then
    echouer "Archive introuvable : $ARCHIVE"
  else
    annoncer "Archive appliquee"
    echo "$ARCHIVE"
    unzip -l "$ARCHIVE" | awk 'NR>3 && NF>3 {print "  " $4}' | grep -v '/$'
    if [ "$ESSAI" = 0 ]; then
      unzip -o -q "$ARCHIVE" -d "$RACINE" || echouer "Decompression impossible"
      rm -f "$RACINE/APPLIQUER.md"
    fi
  fi
fi

# ------------------------------------------------------------ 3. controles
annoncer "Ce qui change"
git status --short
if [ -z "$(git status --porcelain)" ]; then
  echo "Rien a valider : le depot est deja a jour."
  exit 0
fi

SUSPECTS="$(git status --porcelain | awk '{print $NF}' \
  | grep -E 'etat\.json|journal\.jsonl|etude\.json|\.log$|sauvegardes/|COLLECTE_EN_COURS' || true)"
if [ -n "$SUSPECTS" ]; then
  printf "\n\033[31mDonnees de seance detectees :\033[0m\n%s\n" "$SUSPECTS"
  echouer "Rien n'a ete pousse. Verifiez .gitignore avant de recommencer."
fi

# ------------------------------------------------------------ 4. confirmation
[ -z "$MESSAGE" ] && MESSAGE="Mise a jour du $(date +%d\ %B\ %Y)"
annoncer "Commit et envoi"
echo "Message : $MESSAGE"
if [ "$ESSAI" = 1 ]; then
  echo "(essai : rien n'est valide ni pousse)"
  exit 0
fi
printf "Continuer ? [o/N] "
read -r reponse
case "$reponse" in
  o|O|oui|Oui) ;;
  *) echo "Abandonne. Vos fichiers restent en place, rien n'a ete valide."; exit 0 ;;
esac

# ------------------------------------------------------------ 5. git
git add -A || echouer "git add a echoue"
git commit -q -m "$MESSAGE" || echouer "git commit a echoue"
git pull --rebase --quiet || echouer "Le rebasage a echoue. Resolvez les conflits, puis : git rebase --continue && git push"
git push --quiet || echouer "git push a echoue. Verifiez l'authentification, puis : git push"

annoncer "Fait"
git log --oneline -1
git status --short --branch | head -1
