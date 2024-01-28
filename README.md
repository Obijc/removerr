# Movie and TV Show Deletion Script

## Important !!!

Le script ne fonctionne que sur le système d'exploitation Windows.
Le script a besoin d'avoir un accès aux fichiers via le chemin que donne Radarr et Sonarr.

## Introduction

Ce script est conçu pour supprimer automatiquement les films et les séries de trois plateformes (Radarr, Overseerr, Sonarr) en fonction de certains critères. Avant d'exécuter le script, assurez-vous de bien configurer le fichier `settings.json` selon les instructions ci-dessous.

## Configuration

### Clés API

- `api_key_radarr`: Clé API Radarr
- `api_key_overseerr`: Clé API Overseerr
- `api_key_sonarr`: Clé API Sonarr

### Adresses IP des Plateformes (format IP:PORT)

- `url_radarr_ip`: Adresse IP de Radarr
- `url_overseerr_ip`: Adresse IP d'Overseerr
- `url_sonarr_ip`: Adresse IP de Sonarr

### Délais avant Suppression

- `days_max_movie`: Nombre de jours avant de supprimer un film
- `days_max_serie`: Nombre de jours avant de supprimer une série

### Intervalle de Scan

- `waiting_time`: Temps en heures avant un nouveau scan (ignoré si `start_all_day` est utilisé)
- `start_in`: Temps en heures avant le premier scan (ignoré si `start_all_day` est utilisé)
- `start_all_day`: Heure de début du scan toute la journée (format: HH:MM) ou `false` pour utiliser `start_in` et `waiting_time`

### Filtres 4K

- `is4k_movie`: `true` pour supprimer uniquement les films en 4K
- `is4k_serie`: `true` pour supprimer uniquement les séries en 4K

### Webhooks Discord

- `discord_webhook_info`: URL du webhook Discord pour les informations
- `discord_webhook_error`: URL du webhook Discord pour les erreurs

### Filtres d'URL

- `url_radarr`: Si l'URL de Radarr ne contient pas cette chaîne, le film ne sera pas supprimé (laisser `false` pour ne pas utiliser) (Utile si vous ne voulez suppimer que les films provenant d'un répertoire spécifique)
- `url_sonarr`: Si l'URL de Sonarr ne contient pas cette chaîne, la série ne sera pas supprimée (laisser `false` pour ne pas utiliser) (Utile si vous ne voulez suppimer que les séries provenant d'un répertoire spécifique)

### Utilisation manuel

- `manual_sort`: `true` pour utiliser le mode manuel de suppression

## Utilisation

1. Assurez-vous d'avoir correctement configuré le fichier `settings.json`.
2. Lancez l'exécutable ou le script detecte.py
