# 📚 Centre de Ressources et Veille Technologique (Mise à jour 2025)

Ce document recense les sources techniques et tutoriels consultés pour la réalisation du projet **Climatomètre RT**. Il témoigne de la démarche d'apprentissage et de veille technologique effectuée.

---

## 📺 Tutoriels Vidéo (Sélection 2024-2025)

### 🐍 Backend : Flask & Python
* **[Tuto] Flask Step-by-Step (Microsoft Learn 2025)** : Guide complet sur la structuration des projets Flask modernes et la gestion des environnements virtuels.  
  👉 [Consulter la documentation interactive](https://learn.microsoft.com/fr-fr/visualstudio/python/learn-flask-visual-studio-step-01-project-solution)
* **[Vidéo] SQLite3 avec Python (Janvier 2023)** : Tutoriel sur l'interaction entre Python et SQLite3, idéal pour comprendre le CRUD et la gestion des curseurs.  
  👉 [Lien YouTube](https://www.youtube.com/watch?v=JiEoZ8Z9oUQ)
* **[Vidéo] Python Threading & Tâches de fond** : Comprendre comment exécuter des processus en parallèle pour ne pas bloquer le serveur web lors des appels API.  
  👉 [Explication technique Docstring](https://www.docstring.fr/glossaire/threading/)

### 🗺️ Frontend : Leaflet & Cartographie
* **[Vidéo] JavaScript : Créer une carte géographique avec Leaflet** : Tutoriel pratique pour intégrer une carte, des marqueurs et gérer le zoom.  
  👉 [Lien YouTube](https://www.youtube.com/watch?v=xxuTFUWA9Nk)
* **[Guide] Leaflet Complet - Blog SIG & Territoires** : Un cours structuré sur l'affichage conditionnel et les symboles dynamiques sur une carte web.  
  👉 [Lire le tutoriel](https://www.sigterritoires.fr/index.php/tutoriel-leaflet/)

---

## 📖 Documentations Officielles & API

### API Météo (OpenWeatherMap)
* **Documentation API 2024** : Guide sur l'authentification par clé `appid` et la gestion des limites de requêtes (Rate Limiting) pour éviter les erreurs HTTP 429.  
  👉 [Documentation API OpenWeather](https://openweathermap.org/api)
* **Guide de sécurité** : Bonnes pratiques pour cacher ses clés API et utiliser le cache local (implémenté dans notre projet pour limiter les appels).  
  👉 [YouTube : How to use API keys safely](https://www.youtube.com/watch?v=HJvlgpoZNbQ)

### Framework & SQL
* **Flask Quickstart (v2.1+)** : Référence pour le rendu des templates Jinja2 et la gestion des objets `request`.  
  👉 [Documentation Flask FR](https://flask-fr.readthedocs.io/quickstart/)
* **SQLite Python Docs** : Référence officielle sur l'utilisation du module `sqlite3` et la sécurité contre les injections SQL.  
  👉 [Python.org - sqlite3 module](https://docs.python.org/3/library/sqlite3.html)

---

## 🛠️ Outils de Développement
* **VS Code (Microsoft)** : IDE principal avec gestionnaire Git intégré.
* **DB Browser for SQLite** : Outil utilisé pour visualiser les tables `residences` et `releves_meteo` en temps réel.
* **Postman** : Utilisé pour tester les réponses JSON de l'API OpenWeather avant intégration dans le script `update_weather.py`.

---
*Document mis à jour pour la soutenance finale de la SAÉ - Avril 2026*