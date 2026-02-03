# 🚀 Guide de Déploiement CISO Assistant sur Coolify/Hetzner

## 📋 Informations de déploiement

- **Domaine**: rssi.ccdigital.fr
- **Plateforme**: Coolify + Hetzner
- **Base de données**: PostgreSQL externe (recommandé)
- **Repository**: GitHub (source)

---

## ✅ Prérequis

- [ ] Serveur Hetzner avec Coolify installé
- [ ] Accès SSH au serveur
- [ ] Nom de domaine `rssi.ccdigital.fr` pointant vers l'IP du serveur
- [ ] Repository GitHub accessible

---

## 📝 Étape 1 : Configuration DNS

Configurez les enregistrements DNS pour `rssi.ccdigital.fr` :

```
Type: A
Nom: rssi (ou @)
Valeur: [IP_DE_VOTRE_SERVEUR_HETZNER]
TTL: 3600
```

Vérifiez la propagation DNS :
```bash
nslookup rssi.ccdigital.fr
```

---

## 🗄️ Étape 2 : Créer la base de données PostgreSQL dans Coolify

1. **Connectez-vous à Coolify** (https://[IP_SERVEUR]:8000)

2. **Créez une nouvelle base de données PostgreSQL** :
   - Allez dans **Databases** → **+ New Database**
   - Sélectionnez **PostgreSQL**
   - Configuration :
     - **Name**: `ciso-assistant-db`
     - **Database Name**: `ciso_assistant_prod`
     - **Username**: `ciso_assistant`
     - **Password**: Générez un mot de passe fort
     - **Version**: PostgreSQL 15 ou supérieur

3. **Notez les informations de connexion** :
   - Host: `ciso-assistant-db` (nom du service)
   - Port: `5432`
   - Database: `ciso_assistant_prod`
   - User: `ciso_assistant`
   - Password: [le mot de passe généré]

---

## 🔐 Étape 3 : Générer les secrets

### 3.1 Générer la clé secrète Django

Sur votre machine locale ou sur le serveur :

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copiez la clé générée, vous en aurez besoin pour `DJANGO_SECRET_KEY`.

### 3.2 Définir le mot de passe admin

Choisissez un mot de passe fort pour le compte superutilisateur initial.

---

## 🚢 Étape 4 : Déployer l'application dans Coolify

### 4.1 Créer un nouveau projet

1. Dans Coolify, allez dans **Projects** → **+ New Project**
2. **Name**: `CISO Assistant`
3. **Environment**: `Production`

### 4.2 Ajouter l'application depuis GitHub

1. Cliquez sur **+ New Resource** → **Application**
2. **Source**: Sélectionnez votre repository GitHub
   - Repository: `[VOTRE_USERNAME]/ciso-assistant-industry`
   - Branch: `main` (ou votre branche de production)
3. **Build Pack**: `Docker Compose`
4. **Docker Compose File**: `docker-compose.prod.yml`

### 4.3 Configurer les variables d'environnement

Dans l'onglet **Environment Variables**, ajoutez :

```env
# Domaine
DOMAIN=rssi.ccdigital.fr
CISO_ASSISTANT_URL=https://rssi.ccdigital.fr
ALLOWED_HOSTS=rssi.ccdigital.fr,backend
CSRF_TRUSTED_ORIGINS=https://rssi.ccdigital.fr
CORS_ALLOWED_ORIGINS=https://rssi.ccdigital.fr
ORIGIN=https://rssi.ccdigital.fr
PUBLIC_BACKEND_API_URL=https://rssi.ccdigital.fr/api

# Django
DJANGO_SECRET_KEY=[LA_CLE_GENEREE_ETAPE_3.1]
DJANGO_DEBUG=False

# Base de données (depuis Étape 2)
POSTGRES_NAME=ciso_assistant_prod
POSTGRES_USER=ciso_assistant
POSTGRES_PASSWORD=[MOT_DE_PASSE_BDD_ETAPE_2]
POSTGRES_HOST=ciso-assistant-db
POSTGRES_PORT=5432

# Superutilisateur initial
DJANGO_SUPERUSER_EMAIL=admin@rssi.ccdigital.fr
DJANGO_SUPERUSER_PASSWORD=[MOT_DE_PASSE_ADMIN_ETAPE_3.2]
DJANGO_SUPERUSER_FIRSTNAME=Admin
DJANGO_SUPERUSER_LASTNAME=CISO

# Email (optionnel - à configurer plus tard si besoin)
# EMAIL_HOST=smtp.example.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=noreply@rssi.ccdigital.fr
# EMAIL_HOST_PASSWORD=[MOT_DE_PASSE_EMAIL]
# EMAIL_USE_TLS=True
# DEFAULT_FROM_EMAIL=noreply@rssi.ccdigital.fr
```

### 4.4 Configurer le domaine

1. Dans l'onglet **Domains**, ajoutez :
   - **Domain**: `rssi.ccdigital.fr`
   - **HTTPS**: Activé (Let's Encrypt automatique)

### 4.5 Configurer les ports

Coolify devrait détecter automatiquement les ports depuis `docker-compose.prod.yml` :
- Port 80 (HTTP)
- Port 443 (HTTPS)

---

## 🚀 Étape 5 : Déployer

1. Cliquez sur **Deploy** dans Coolify
2. Surveillez les logs de déploiement
3. Attendez que tous les services soient **healthy** (✅)

Le déploiement peut prendre 5-10 minutes.

---

## ✅ Étape 6 : Vérification post-déploiement

### 6.1 Vérifier l'accès à l'application

1. Ouvrez votre navigateur : https://rssi.ccdigital.fr
2. Vous devriez voir la page de connexion CISO Assistant

### 6.2 Se connecter en tant qu'admin

- **Email**: `admin@rssi.ccdigital.fr`
- **Mot de passe**: [celui défini dans `DJANGO_SUPERUSER_PASSWORD`]

### 6.3 Vérifier les frameworks IEC 62443

1. Allez dans **Libraries** → **Frameworks**
2. Vérifiez que les frameworks IEC 62443 sont présents :
   - IEC 62443 - Security for Industrial Automation and Control Systems (v2)
   - IEC 62443-4-2 - Component Security Requirements (v2)
3. Vérifiez les traductions françaises

### 6.4 Vérifier les logs

Dans Coolify, consultez les logs de chaque service :
- **backend**: Pas d'erreurs Django
- **huey**: Worker actif
- **frontend**: SvelteKit démarré
- **caddy**: Certificat SSL obtenu

---

## 🔧 Étape 7 : Configuration post-installation

### 7.1 Charger les bibliothèques IEC 62443

Si les frameworks ne sont pas chargés automatiquement :

```bash
# Se connecter au conteneur backend
docker exec -it [CONTAINER_ID_BACKEND] sh

# Charger les bibliothèques
python manage.py storelibraries
python manage.py autoloadlibraries
```

### 7.2 Configurer les emails (optionnel)

Si vous souhaitez activer l'envoi d'emails :

1. Configurez un service SMTP (Gmail, SendGrid, Mailgun, etc.)
2. Ajoutez les variables d'environnement EMAIL_* dans Coolify
3. Redéployez l'application

---

## 📊 Monitoring et Maintenance

### Logs

Accédez aux logs via Coolify :
- **Application logs**: Coolify → Votre app → Logs
- **Database logs**: Coolify → Database → Logs

### Backups

**Base de données** :
1. Dans Coolify, allez dans votre base de données PostgreSQL
2. Activez les **Automated Backups**
3. Configurez la fréquence (recommandé : quotidien)

**Volumes Docker** :
Les données persistantes sont dans :
- `backend-data` : Base de données SQLite locale (non utilisée en prod)
- `backend-media` : Fichiers uploadés
- `caddy-data` : Certificats SSL

### Mises à jour

Pour mettre à jour l'application :

1. Poussez vos changements sur GitHub
2. Dans Coolify, cliquez sur **Redeploy**
3. Coolify va automatiquement :
   - Pull les dernières modifications
   - Rebuild les images
   - Redémarrer les services

---

## 🆘 Dépannage

### L'application ne démarre pas

1. Vérifiez les logs dans Coolify
2. Vérifiez que la base de données est accessible :
   ```bash
   docker exec -it [BACKEND_CONTAINER] sh
   python manage.py dbshell
   ```

### Erreur 502 Bad Gateway

- Le backend n'est pas encore démarré (attendez le healthcheck)
- Vérifiez les logs du backend

### Certificat SSL non généré

1. Vérifiez que le DNS pointe bien vers le serveur
2. Vérifiez que les ports 80 et 443 sont ouverts
3. Redéployez l'application

### Les frameworks IEC 62443 ne sont pas visibles

```bash
# Vérifier si les bibliothèques sont stockées
docker exec -it [BACKEND_CONTAINER] python manage.py shell -c "from core.models import StoredLibrary; print(StoredLibrary.objects.filter(urn__icontains='iec-62443').count())"

# Si 0, charger manuellement
docker exec -it [BACKEND_CONTAINER] python manage.py storelibraries
docker exec -it [BACKEND_CONTAINER] python manage.py autoloadlibraries
```

---

## 🔒 Sécurité

### Recommandations

- ✅ HTTPS activé automatiquement (Let's Encrypt)
- ✅ Headers de sécurité configurés dans Caddy
- ✅ Base de données avec mot de passe fort
- ✅ Django en mode production (`DEBUG=False`)
- ⚠️ Configurez un pare-feu (UFW) sur Hetzner
- ⚠️ Activez les backups automatiques
- ⚠️ Configurez des alertes de monitoring

### Pare-feu Hetzner

```bash
# Autoriser SSH
ufw allow 22/tcp

# Autoriser HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Activer le pare-feu
ufw enable
```

---

## 📞 Support

En cas de problème :

1. Consultez les logs dans Coolify
2. Vérifiez la documentation CISO Assistant : https://docs.ciso-assistant.com
3. Vérifiez les issues GitHub du projet

---

## ✨ Félicitations !

Votre instance CISO Assistant est maintenant déployée en production sur **rssi.ccdigital.fr** ! 🎉

Prochaines étapes recommandées :
- [ ] Configurer les emails
- [ ] Créer des utilisateurs supplémentaires
- [ ] Importer vos premiers projets d'évaluation
- [ ] Configurer les backups automatiques
- [ ] Mettre en place un monitoring (Uptime Kuma, etc.)
