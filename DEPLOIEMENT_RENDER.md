# Guide de deploiement sur Render.com
# Loge Facile Niger

## Etape 1 — Creer un compte GitHub

Va sur https://github.com et cree un compte gratuit si tu n'en as pas.

## Etape 2 — Creer un depot GitHub

1. Clique sur "New repository"
2. Nom : loge-facile-niger
3. Visibilite : Private (prive)
4. Clique "Create repository"

## Etape 3 — Pousser le code sur GitHub

Dans le terminal de ton PC, dans le dossier loge-facile :

  git init
  git add .
  git commit -m "Premier deploiement Loge Facile Niger"
  git branch -M main
  git remote add origin https://github.com/TON_USERNAME/loge-facile-niger.git
  git push -u origin main

Remplace TON_USERNAME par ton nom d'utilisateur GitHub.

## Etape 4 — Creer un compte Render

Va sur https://render.com et connecte-toi avec ton compte GitHub.

## Etape 5 — Creer le service Web

1. Clique "New +" puis "Web Service"
2. Connecte ton depot GitHub loge-facile-niger
3. Parametres :
   - Name : loge-facile-niger
   - Environment : Python 3
   - Build Command : pip install -r requirements.txt && python database.py
   - Start Command : gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
4. Plan : Free (gratuit)
5. Clique "Create Web Service"

## Etape 6 — Configurer les variables d'environnement

Dans Render, va dans "Environment" et ajoute ces variables :

  MAIL_USERNAME    = logefacile.niger@gmail.com
  MAIL_PASSWORD    = ton_mot_de_passe_app_gmail
  MAIL_RECEIVER    = logefacile.niger@gmail.com
  ADMIN_PASSWORD   = TonMotDePasseAdmin!
  SECRET_KEY       = une_chaine_aleatoire_longue

## Etape 7 — Configurer le disque persistant (important pour les photos)

1. Dans Render, va dans "Disks"
2. Clique "Add Disk"
3. Mount Path : /opt/render/project/src/static/uploads
4. Size : 1 GB

## Etape 8 — Ton site est en ligne !

Render te donne une URL du type :
  https://loge-facile-niger.onrender.com

Admin :
  https://loge-facile-niger.onrender.com/admin/login

## Notes importantes

- Le plan gratuit met le site en veille apres 15 min d'inactivite
  (premier chargement lent - 30 secondes environ)
- Pour un site toujours actif : plan Starter a 7$/mois
- La base de donnees SQLite est sur le disque persistant
- Les photos uploadees sont conservees sur le disque persistant

## Si tu veux un domaine personnalise

Dans Render > Settings > Custom Domain, tu peux ajouter :
  www.logefacile-niger.com (ou tout autre domaine que tu achetes)
