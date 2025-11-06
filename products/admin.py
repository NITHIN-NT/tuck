from django.contrib import admin
from .models import Category,Product,ProductImage,Size
# Register your models here.
admin.site.register(Category)
class ProductImageInline(admin.TabularInline): # or admin.StackedInline
    model = ProductImage
    extra = 1 
class ProductAdminView(admin.ModelAdmin):
    list_display=['name','description','base_price','offer_price','category','created_at','is_featured','is_most_demanded','is_selective']
admin.site.register(Product,ProductAdminView,inlines=[ProductImageInline])

class ProductImageAdminView(admin.ModelAdmin):
    list_display = ['product','image_url']
admin.site.register(ProductImage,ProductImageAdminView)
admin.site.register(Size)