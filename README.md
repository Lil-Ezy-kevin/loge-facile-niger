# Loge Facile Niger — Guide d'installation

## Structure du projet

```
loge-facile/
├── app.py              # Serveur Flask principal
├── config.py           # Configuration (email, WhatsApp, admin)
├── database.py         # Base de donnees SQLite
├── notifications.py    # Envoi email et WhatsApp
├── requirements.txt    # Dependances Python
├── static/
│   ├── index.html      # Site web frontend
│   └── uploads/        # Fichiers uploades (photos/videos)
└── README.md
```

---

## 1. Installation

### Python requis : 3.8 ou superieur

```bash
# Installer les dependances
pip install -r requirements.txt
```

---

## 2. Configuration (OBLIGATOIRE avant lancement)

Ouvre `config.py` et modifie ces valeurs :

### Email Gmail
```python
MAIL_USERNAME = 'logefacile.niger@gmail.com'   # Ton adresse Gmail
MAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'          # Mot de passe d'APPLICATION Gmail
MAIL_RECEIVER = 'logefacile.niger@gmail.com'   # Adresse qui recoit les notifications
```

> **Comment obtenir un mot de passe d'application Gmail :**
> 1. Va sur https://myaccount.google.com
> 2. Securite > Validation en 2 etapes (activer)
> 3. Securite > Mots de passe des applications
> 4. Cree un mot de passe pour "Mail" > copie les 16 caracteres

### WhatsApp via Twilio (OPTIONNEL)
Si tu veux les notifications WhatsApp, cree un compte sur https://twilio.com
```python
TWILIO_SID        = 'ACxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN = 'xxxxxxxxxxxxxxxx'
TWILIO_WHATSAPP_TO = 'whatsapp:+22797431619'
```
Si tu ne veux pas Twilio, laisse ces champs vides — les notifications email fonctionneront quand meme.

### Mot de passe admin
```python
ADMIN_PASSWORD = 'TonMotDePasseSecret!'
```

---

## 3. Lancement

```bash
python app.py
```

Le serveur demarre sur : http://localhost:5000

- **Site web** : http://localhost:5000
- **Admin**    : http://localhost:5000/admin
  - Utilisateur : `admin`
  - Mot de passe : celui defini dans config.py

---

## 4. Ce que fait le backend

### Quand un client soumet une demande de logement :
- Enregistre la demande en base SQLite
- Envoie un email de notification a l'equipe Loge Facile
- Envoie un message WhatsApp (si Twilio configure)

### Quand un proprietaire soumet son logement :
- Enregistre la proposition en base SQLite
- Sauvegarde les photos/videos uploadees dans `static/uploads/`
- Envoie un email detaille a l'equipe
- Envoie un message WhatsApp (si Twilio configure)

### Panneau admin (http://localhost:5000/admin) :
- Voir toutes les demandes et propositions
- Changer les statuts (nouveau / traite / publie)
- Voir les photos/videos des propositions
- Supprimer des entrees

---

## 5. Deploiement en ligne (optionnel)

Pour mettre en ligne sur un VPS ou Render/Railway :

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 6. Base de donnees

La base SQLite `logefacile.db` est creee automatiquement au premier lancement.
Pas besoin d'installer MySQL ou PostgreSQL.

---

## Contact & Support
- WhatsApp : +227 97 43 16 19
- Email    : logefacile.niger@gmail.com
