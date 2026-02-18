#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from iam.models import User

# Lister tous les utilisateurs
print("\n=== Utilisateurs existants ===")
for user in User.objects.all():
    print(f"Email: {user.email} | Superuser: {user.is_superuser}")

# Réinitialiser le mot de passe admin
print("\n=== Réinitialisation du mot de passe ===")
try:
    admin = User.objects.get(email='admin@ciso-assistant.local')
    admin.set_password('admin123')
    admin.save()
    print("✅ Mot de passe réinitialisé pour admin@ciso-assistant.local")
    print("   Nouveau mot de passe: admin123")
except User.DoesNotExist:
    print("❌ Utilisateur admin@ciso-assistant.local non trouvé")
    print("\n=== Création d'un nouveau superutilisateur ===")
    User.objects.create_superuser(
        email='admin@ciso-assistant.local',
        password='admin123',
        first_name='Admin',
        last_name='CISO'
    )
    print("✅ Superutilisateur créé: admin@ciso-assistant.local / admin123")
