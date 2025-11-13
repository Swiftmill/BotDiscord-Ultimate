# Guide Utilisateur

Bienvenue dans Ultimate Discord Bot Suite ! Ce guide explique comment utiliser le bot, le backend de licences et l'application desktop.

## 1. Préparation

1. Assurez-vous d'avoir exécuté `python installer/install.py`.
2. Copiez `bot/config_example.yml` vers `bot/config.yml` et remplissez les champs requis (token, licence, etc.).
3. Démarrez le backend de licences : `./scripts/start_backend.sh`.
4. Démarrez le bot : `./scripts/start_bot.sh`.
5. Lancez l'application desktop : `python desktop/app.py` (depuis l'environnement `venv_desktop`).

## 2. Application Desktop

### 2.1 Dashboard
- Affiche le statut global du bot.
- Bouton "Redémarrer le bot" pour demander un redémarrage (requiert intégration avec un service supervisor).

### 2.2 Logs
- Zone de texte réservée aux logs en temps réel. (Connexion websocket à implémenter en production.)

### 2.3 Configuration
- Visualise et édite `bot/config.yml`.
- Cliquez sur **Enregistrer** pour sauvegarder vos modifications.

### 2.4 Licences
- Saisissez la clé pour vérifier sa validité via le backend.
- Résultat affiché dans le panneau inférieur.

## 3. Commandes Bot

### 3.1 Musique (slash commands)
- `/play <recherche ou URL>`
- `/pause`
- `/stop`
- `/skip`
- `/queue`
- `/nowplaying`
- `/lyrics <titre>`

### 3.2 Tickets
- `/ticket` crée un salon dédié.
- `/ticket-close` clôture le ticket, génère une transcription et la journalise.

## 4. Sécurité & AutoMod

- Anti-raid, anti-spam, anti-flood et anti-liens actifs par défaut.
- Filtres insultes/majuscule/lien gérés via `bot/assets/bad_words.txt` et `bot/assets/allowed_links.txt`.
- Les actions automatiques (mute/kick/ban) se déclenchent en fonction des scores comportementaux.

## 5. Système de licences

- La validation se fait automatiquement au démarrage du bot.
- Chaque validation met à jour `guild_id` et vérifie l'expiration.
- Pour gérer les licences, utilisez l'application desktop (onglet Licences) ou l'API (`/licenses`).

## 6. Mise à jour

1. Mettez à jour le dépôt (`git pull`).
2. Relancez `python installer/install.py` si des dépendances ont changé.
3. Redémarrez le backend, le bot et l'application desktop.

## 7. Support

- Consultez `docs/DEV_GUIDE.md` pour des informations avancées.
- Créez une issue sur le dépôt en cas de bug.
