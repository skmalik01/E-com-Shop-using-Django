from django.db import models

# Create your models here.

class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=40)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=200)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")
    
    def __str__(self) -> str:
        return self.product_name
    
class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    subject = models.CharField(max_length=70)
    message = models.CharField(max_length=5000)
    
    def __str__(self) -> str:
        return self.name
    
class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=40)
    phone = models.CharField(max_length=30, default="")
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    zip_code = models.CharField(max_length=90, null=False, blank=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name

class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.update_desc[0:7] + "....."