from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    category = models.CharField(max_length=200, null=True)
    color = models.CharField(max_length=200, null=True)
    price = models.IntegerField(null=True)
    sub_category = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=500 ,null=True, blank=True)
    gender = models.CharField(max_length=50, null=True)
    
    def __str__(self):
         return (f'{self.name} ({self.color})')

class Care(models.Model):
    product = models.ForeignKey(Product,null=True, on_delete=models.CASCADE)
    care = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return (f'{self.product.name} ({self.product.color})')

class Image(models.Model):
    product = models.ForeignKey(Product,null=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='',default='')
    
    def __str__(self):
        return (f'{self.product.name} ({self.product.color})')

class Sku(models.Model):

    product = models.ForeignKey(Product,null=True, on_delete=models.CASCADE)
    price = models.IntegerField(null=True)
    color = models.CharField(max_length=50,null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    out_of_stock = models.BooleanField(null=True)
    
    def __str__(self):
        return (f'{self.product.name} ({self.color}-{self.size})')

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=12)
    email = models.EmailField(max_length=254)

    def __str__(self):
        return self.name

class Order(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null= True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])

        return total
    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])

        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order=  models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product.name)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address