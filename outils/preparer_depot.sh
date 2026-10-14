#!/usr/bin/env bash
# Premier depot sur GitHub, depuis la racine du projet.
#   outils/preparer_depot.sh git@github.com:<compte>/fptutor-shell.git
set -eu
DEPOT="${1:?usage: outils/preparer_depot.sh <url du depot distant>}"
git init -b main
git add .
git status --short | head -50
git commit -m "FPTutor-Shell v3 : coquille, instances OCaml, Racket et Python, documentation du stage"
git remote add origin "$DEPOT"
git push -u origin main
