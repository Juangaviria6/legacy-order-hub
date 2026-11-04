import os

from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_users(apps, schema_editor):
    """Crea los usuarios iniciales.

    En produccion defina SEED_ADMIN_PASSWORD y SEED_USER_PASSWORD; los valores
    por defecto solo existen para desarrollo local y pruebas.
    """
    UserModel = apps.get_model("users", "UserModel")
    if UserModel.objects.exists():
        return
    admin_password = os.environ.get("SEED_ADMIN_PASSWORD") or "admin123"
    user_password = os.environ.get("SEED_USER_PASSWORD") or "123456"
    UserModel.objects.create(
        username="admin", password=make_password(admin_password), role="admin"
    )
    UserModel.objects.create(
        username="juan", password=make_password(user_password), role="client"
    )


def unseed_users(apps, schema_editor):
    UserModel = apps.get_model("users", "UserModel")
    UserModel.objects.filter(username__in=["admin", "juan"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_users, unseed_users),
    ]
