# Ultimate Discord Bot Suite

Ultimate Discord Bot Suite est une solution tout-en-un combinant un bot Discord professionnel, un tableau de bord desktop premium et un backend de licences sécurisé. Chaque composant est conçu pour fonctionner ensemble afin d'offrir une expérience stable, élégante et sécurisée.

## 🧩 Architecture globale

```
BotDiscord-Ultimate/
├── backend/            # API FastAPI pour la gestion des licences et l'antivirus
├── bot/                # Bot Discord (discord.py) + API de contrôle
├── desktop/            # Application PySide6 (packaging .exe via PyInstaller)
├── installer/          # Script d'installation multi-plateforme
├── scripts/            # Scripts de démarrage convenables
├── docs/               # Guides détaillés (utilisateur, développeur, hébergement)
└── README.md           # Ce document
```

## ✨ Fonctionnalités principales

- **Sécurité avancée** : anti-raid, anti-spam, détection de liens, filtrage NSFW (placeholder), antivirus par hash.
- **AutoMod intelligent** : filtres personnalisables, gestion du flood, caps, spam emoji, et plus.
- **Gestion de tickets** : création via slash-command, transcription automatique et logs dédiés.
- **Module musique** : YouTube/Spotify/SoundCloud (via recherche automatique yt-dlp), file d'attente, commandes slash `/play`, `/pause`, `/stop`, `/queue`, `/skip`, `/nowplaying`, `/lyrics`.
- **Dashboard desktop premium** : interface style macOS glassmorphism, édition de configuration, validation licences, logs temps réel (préparé), packaging `.exe` via PyInstaller.
- **Système de licences complet** : génération/validation/expiration, limitation par serveur, API sécurisée avec journaux.
- **Installateur complet** : création d'environnements virtuels et installation des dépendances.

## 🚀 Mise en route rapide

1. **Cloner le dépôt**
   ```bash
   git clone <repo>
   cd BotDiscord-Ultimate
   ```
2. **Lancer l'installateur**
   ```bash
   python installer/install.py
   ```
3. **Configurer le bot**
   ```bash
   cp bot/config_example.yml bot/config.yml
   # Éditer bot/config.yml avec votre token, la clé de licence et la configuration souhaitée
   ```
4. **Démarrer les services**
   ```bash
   ./scripts/start_backend.sh   # API licences
   ./scripts/start_bot.sh       # Bot Discord
   ```
5. **Lancer l'application desktop**
   ```bash
   source venv_desktop/bin/activate
   python desktop/app.py
   ```

Les utilisateurs Windows disposent d'équivalents `.ps1` pour les scripts de démarrage.

## 📚 Documentation

- [Guide utilisateur](docs/USER_GUIDE.md)
- [Guide d'installation & hébergement](docs/HOSTING.md)
- [Guide développeur](docs/DEV_GUIDE.md)

## 🛡️ Sécurité

- Signatures HMAC et tokens JWT pour sécuriser l'API de licences.
- Journaux d'audit détaillés pour chaque action sur une licence.
- Filtrage proactif anti-phishing, flood et comportement suspect.
- Scans de fichiers via base de hash locale (extensible à une API antivirus).

## 🧪 Tests

- Lancement local du backend : `uvicorn backend.app:app`.
- Exécution du bot : `python bot/main.py`.
- Démarrage de l'app desktop : `python desktop/app.py`.
- Packaging `.exe` : `pyinstaller desktop/build.spec` (depuis l'environnement virtuel desktop).

## 🤝 Contribution

1. Créer une branche de fonctionnalité.
2. Effectuer les modifications et ajouter des tests.
3. Ouvrir une Pull Request détaillant les changements et l'impact.

## 📄 Licence

Ce projet est livré sans licence explicite. Merci de contacter l'auteur avant toute utilisation commerciale.
