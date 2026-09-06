"""Entrée Vercel : expose l'application Flask sans démarrer de serveur local."""
from dashboard.app import app

# Vercel détecte automatiquement l'objet WSGI nommé `app`.
