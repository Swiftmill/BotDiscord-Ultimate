# Guide Développeur

Ce guide couvre la structure interne, les conventions et les workflows recommandés pour contribuer à Ultimate Discord Bot Suite.

## 1. Prérequis

- Python 3.11+
- Node.js (optionnel, uniquement si vous souhaitez ajouter un frontend web)
- Git, pip, virtualenv

## 2. Structure du projet

- `backend/` : API FastAPI pour licences et antivirus
  - `app.py` : points d'entrée
  - `database.py` : modèles SQLAlchemy
  - `models.py` : schémas Pydantic
  - `security.py` : HMAC + JWT
  - `settings.py` : configuration via Pydantic
- `bot/` : bot Discord
  - `main.py` : initialisation
  - `cogs/` : sécurité, automod, tickets, musique
  - `utils/` : chargement config, logging, licence, sécurité
  - `web.py` : mini API de contrôle (à étoffer pour la communication desktop)
- `desktop/` : application PySide6
  - `app.py` : entry point
  - `ui/main_window.py` : interface principale
  - `build.spec` : packaging PyInstaller
- `installer/` : script Python créant les environnements virtuels
- `docs/` : documentation

## 3. Environnements virtuels

Chaque composant utilise son propre venv. Après modification d'un `requirements.txt`, relancez `python installer/install.py`.

## 4. Lancement en développement

1. Backend :
   ```bash
   source venv_backend/bin/activate
   uvicorn backend.app:app --reload
   ```
2. Bot :
   ```bash
   source venv_bot/bin/activate
   cd bot
   python main.py
   ```
3. Desktop :
   ```bash
   source venv_desktop/bin/activate
   python desktop/app.py
   ```

## 5. Ajout d'un cog

1. Créez un fichier dans `bot/cogs/` (ex: `analytics.py`).
2. Implémentez la classe `commands.Cog`.
3. Chargez le cog dans `UltimateBot.setup_hook`.

## 6. API Backend

- `POST /auth/token` : génère un token admin (mot de passe = `Settings.secret_key`).
- `POST /licenses` : crée une licence.
- `GET /licenses` : liste les licences.
- `PUT /licenses/{key}` : mise à jour.
- `DELETE /licenses/{key}` : suppression.
- `POST /licenses/validate` : vérification (utilisé par le bot et l'app desktop).

## 7. Packaging desktop

1. Activez `venv_desktop`.
2. Installez PyInstaller si nécessaire : `pip install pyinstaller`.
3. Exécutez `pyinstaller desktop/build.spec`.
4. L'exécutable se trouve dans `dist/UltimateBotDashboard/`.

## 8. Tests et qualité

- Ajoutez des tests unitaires dans un futur dossier `tests/` (non inclus par défaut).
- Respectez PEP 8.
- Utilisez `logging` pour tracer les événements importants.

## 9. Publication

- Configurez un service (systemd, pm2, Docker) pour superviser backend et bot.
- Stockez les fichiers sensibles (token, secret key) dans des variables d'environnement.

## 10. Roadmap suggérée

- Intégration antivirus réelle (VirusTotal, etc.).
- Websocket entre bot et application desktop pour logs temps réel.
- Notifications push pour tickets/mises à jour.
- Gestion multi-utilisateurs avec rôles sur le backend.
