from django.db import models


class OrderModel(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    total = models.FloatField()
    status = models.CharField(max_length=50)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"Order #{self.id}"
