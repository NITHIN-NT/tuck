from django.db import models

# Create your models here.
class Category(models.Model):  # Changed from 'Categorie' for naming consistency
    name = models.CharField(max_length=1024, unique=True)
    description = models.TextField()
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2) 
    image = models.URLField(max_length=1024)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=99)
    size = models.ManyToManyField("Size",blank=True,related_name='sizes')
    created_at = models.DateTimeField(auto_now_add=True) 

    is_featured = models.BooleanField(default=False)
    is_selective = models.BooleanField(default=False)
    is_most_demanded = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=1024) # 

    def __str__(self):
        return f"Image for {self.product.name}"

class Size(models.Model):
    size = models.CharField(max_length=50)

    def __str__(self):
        return self.size

