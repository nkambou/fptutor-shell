"""Extension d'OCamlTutor chargee par la coquille : la seance de suivi.

La coquille charge ce module s'il existe dans le repertoire du tuteur. Il expose
l'API du suivi sous /api/ext/ et la page du suivi sous /suivi, dans le meme
processus que le tuteur : un seul service, une seule adresse, aucune entree de
proxy supplementaire.
"""
from suivi_serveur import api          # noqa: F401

PAGES = {"/suivi": "suivi.html"}
