# climatometre-rt
# 🌍 Projet Climatomètre RT - Documentation Technique
**BUT Réseaux et Télécommunications**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Raphoxrr28/Climatom-tre-RT)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-orange.svg)](https://www.sqlite.org/)

## 📝 Introduction
Le **Climatomètre RT** est une application full-stack conçue pour centraliser, cartographier et analyser les données climatiques des lieux de vie des étudiants. Ce projet combine le développement d'interfaces dynamiques, la gestion de bases de données relationnelles et la communication avec des services API tiers.

---

## 🏗️ Architecture du Système

### 1. Choix Technologiques
* **Backend :** Python avec le micro-framework **Flask**. Choisi pour sa souplesse et sa capacité à gérer des tâches asynchrones (threading).
* **Base de Données :** **SQLite3**. Un moteur robuste sans serveur, idéal pour la portabilité du projet entre collaborateurs.
* **Cartographie :** **Leaflet.js**. Utilisation de plugins de *Clustering* pour gérer la superposition des marqueurs dans les zones à forte densité étudiante (ex: résidences universitaires).
* **Frontend :** Design personnalisé en CSS3 avec l'utilisation de **Glassmorphism** (effets de flou et transparence).

### 2. Modèle de Données (Schéma Relationnel)
L'application s'appuie sur une structure SQL normalisée pour garantir l'intégrité des données :

| Table | Rôle |
| :--- | :--- |
| **Etudiants** | Stocke l'identité (Nom, Prénom). |
| **Residences** | Stocke la localisation (Ville, Adresse, Type), liée à un étudiant. |
| **Releves_Meteo** | Stocke l'historique climatique (Température, Humidité, Ciel) lié à une résidence. |

---

## 🛠️ Analyse des Composants Logiciels

### A. Gestion du rafraîchissement météo (Threading)
Pour assurer une expérience utilisateur fluide sans latence réseau, l'application utilise un **Thread daemon** en arrière-plan :
* **Processus :** Au lancement du serveur, une boucle infinie est initiée. Elle interroge l'API OpenWeatherMap pour chaque ville enregistrée toutes les 60 secondes.
* **Optimisation :** Les données sont stockées en base de données. L'interface utilisateur ne consulte que la base locale, évitant ainsi des appels API superflus et coûteux lors du chargement des pages.

### B. Algorithme du Climat Médian
Plutôt qu'une simple moyenne, nous avons implémenté le calcul de la **médiane** pour éliminer l'influence des valeurs aberrantes (étudiants en stage à l'étranger ou erreurs de capteurs API).
$$\tilde{x} = \begin{cases} x_{(\frac{n+1}{2})} & \text{si } n \text{ est impair} \\ \frac{x_{(\frac{n}{2})} + x_{(\frac{n}{2}+1)}}{2} & \text{si } n \text{ est pair} \end{cases}$$

### C. Cartographie & Géocodage
Lors de l'ajout d'un étudiant, l'application effectue un **géocodage inverse** via l'API pour récupérer les coordonnées GPS (`lat`, `lon`). Ces coordonnées permettent à Leaflet de positionner précisément les marqueurs sur la carte de la promotion.

---

## 🚀 Installation et Déploiement

### 1. Clonage et Environnement
```bash
git clone [https://github.com/Raphoxrr28/Climatom-tre-RT.git](https://github.com/Raphoxrr28/Climatom-tre-RT.git)
cd Climatom-tre-RT
python -m venv venv
# Activation (Windows) : venv\Scripts\activate
# Activation (Linux/Mac) : source venv/bin/activate