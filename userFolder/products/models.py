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

    base_price = models.DecimalField(max_digits=8, decimal_places=2) 
    offer_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True) 

    image_url = models.URLField(max_length=1024)
    image = models.ImageField(upload_to='products/', height_field=None, width_field=None, max_length=1024,null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    is_featured = models.BooleanField(default=False)
    is_selective = models.BooleanField(default=False)
    is_most_demanded = models.BooleanField(default=False)

    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=1024) 
    image = models.ImageField(upload_to='products/', height_field=None, width_field=None, max_length=1024,null=True,blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class Size(models.Model):
    size = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.size

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE,related_name='variants')
    price = models.DecimalField(max_digits=8,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')  

    def __str__(self):
        return f"{self.size.size}"

