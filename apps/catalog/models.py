from django.db import models


class ProductModel(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name
