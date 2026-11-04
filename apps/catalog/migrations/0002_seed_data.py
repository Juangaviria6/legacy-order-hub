from django.db import migrations


def seed_products(apps, schema_editor):
    ProductModel = apps.get_model("catalog", "ProductModel")
    if ProductModel.objects.exists():
        return
    ProductModel.objects.create(name="Laptop Legada", price=1200.00, stock=5)
    ProductModel.objects.create(name="Mouse USB", price=15.50, stock=50)


def unseed_products(apps, schema_editor):
    ProductModel = apps.get_model("catalog", "ProductModel")
    ProductModel.objects.filter(name__in=["Laptop Legada", "Mouse USB"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]
