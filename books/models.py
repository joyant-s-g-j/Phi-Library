from django.db import models
from categories.models import Category
from django.contrib.auth.models import User
# Create your models here.

class Book(models.Model):
    book_name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    content = models.TextField()
    book_price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='upload/', blank=True, null=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.book_name
    
class Order(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_order = models.DecimalField(decimal_places=2, max_digits=12)
    timestamp = models.DateTimeField(auto_now_add=True)
    returned = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']

    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='review')
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name}"
 