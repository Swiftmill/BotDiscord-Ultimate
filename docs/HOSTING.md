# Guide d'Hébergement & Compilation

Ce document décrit comment déployer les différents composants sur un serveur de production et compiler l'application desktop.

## 1. Backend Licences (FastAPI)

### 1.1 Configuration
- Créez un utilisateur système dédié.
- Copiez le dossier `backend/` sur le serveur.
- Définissez les variables d'environnement souhaitées :
  - `ULB_SECRET_KEY`
  - `ULB_DATABASE_URL` (par défaut SQLite)

### 1.2 Systemd service
```ini
[Unit]
Description=Ultimate License Backend
After=network.target

[Service]
User=ultimate
WorkingDirectory=/opt/ultimate
Environment="ULB_SECRET_KEY=change-me"
ExecStart=/opt/ultimate/venv_backend/bin/uvicorn backend.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Activez et démarrez :
```bash
sudo systemctl daemon-reload
sudo systemctl enable ultimate-backend
sudo systemctl start ultimate-backend
```

## 2. Bot Discord

### 2.1 Configuration
- Copiez `bot/config_example.yml` vers `bot/config.yml`.
- Renseignez `token`, `license.key`, `security`.
- Placez `config.yml` sur le serveur en sécurisant les permissions.

### 2.2 Systemd service
```ini
[Unit]
Description=Ultimate Discord Bot
After=network.target

[Service]
User=ultimate
WorkingDirectory=/opt/ultimate/bot
Environment="PATH=/opt/ultimate/venv_bot/bin"
ExecStart=/opt/ultimate/venv_bot/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 3. Application Desktop

### 3.1 Compilation Windows
1. Activez l'environnement : `venv_desktop\Scripts\activate`.
2. `pip install pyinstaller` (si nécessaire).
3. `pyinstaller desktop/build.spec`.
4. Distribuez `dist/UltimateBotDashboard/UltimateBotDashboard.exe` avec les assets.

### 3.2 Mise à jour automatique
- Utilisez un service de distribution (S3, GitHub Releases) et un script custom pour vérifier les versions.
- Ajoutez un module PySide6 dans `desktop/ui/main_window.py` pour télécharger et remplacer l'exécutable (non inclus par défaut).

## 4. Sécurité

- Configurez HTTPS (Nginx + Certbot) devant le backend si exposé publiquement.
- Activez les pare-feux nécessaires.
- Limitez l'accès au backend aux IPs autorisées.
- Sauvegardez la base SQLite régulièrement.

## 5. Sauvegardes

- `backend/licenses.db`
- `tickets/*.md`
- `bot/logs/`
- `bot/config.yml`

## 6. Monitoring

- Ajoutez Prometheus/Grafana ou tout outil de monitoring pour suivre la disponibilité du backend et du bot.
- Surveillez les logs (journalctl, files logs). Ajoutez une rotation via logrotate si nécessaire.

## 7. Résolution de problèmes

- **Licence invalide** : vérifiez que la clé est active et non expirée via l'API `/licenses`.
- **Bot ne se connecte pas** : assurez-vous que le token Discord est correct et que le backend répond.
- **Musique** : vérifiez la disponibilité de `ffmpeg` sur le serveur.
- **Application desktop** : assurez-vous que le backend est accessible depuis la machine cliente.
