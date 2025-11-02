import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
# Make sure to import your models from the correct app
# from yourapp.models import Category, Product, ProductImage, Size, ProductVariant
# Updated import path to match your project structure
from userFolder.products.models import Category, Product, ProductImage, Size, ProductVariant

class Command(BaseCommand):
    help = 'Loads product data from extracted_products_with_variants.json into the database'

    def handle(self, *args, **options):
        # Define the path to your JSON file
        # Updated path to look inside 'userFolder/products/'
        json_file_path = os.path.join(settings.BASE_DIR, 'userFolder', 'products', 'extracted_products_with_variants.json')

        if not os.path.exists(json_file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {json_file_path}"))
            self.stderr.write(self.style.WARNING("Please place 'extracted_products_with_variants.json' in your 'userFolder/products/' directory."))
            return

        with open(json_file_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(products_data)} products from JSON. Starting import..."))

        # Counters
        products_created = 0
        products_updated = 0
        variants_created = 0

        for item in products_data:
            # 1. Get or Create Category
            category_name = item.get('category', 'Uncategorized')
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Products in the {category_name} category.'}
            )
            if created:
                self.stdout.write(f"Created new category: {category_name}")

            # 2. Prepare Product Data
            try:
                # Use Decimal for price, handle potential '0.00' or empty strings
                price = Decimal(item.get('price', '0.00') or '0.00')
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Invalid price for {item.get('title')}: {item.get('price')}. Setting to 0.00. Error: {e}"))
                price = Decimal('0.00')

            # Ensure description is a string
            description = item.get('description', '')
            if not isinstance(description, str):
                description = str(description)

            # Get the first image as the main product image, if it exists
            main_image_url = item.get('images', [None])[0] or 'https://placehold.co/600x400/eeeeee/cccccc?text=No+Image'

            # 3. Create or Update Product
            # We use update_or_create to avoid duplicating products if the script is run again.
            # The 'handle' from the JSON seems like a good unique field for our 'slug'
            product, created = Product.objects.update_or_create(
                slug=item['handle'],
                defaults={
                    'name': item['title'],
                    'description': description,
                    'base_price': price,
                    'offer_price': price,  # Setting both to same price as JSON has one
                    'image': main_image_url,
                    'category': category,
                    # You can add logic for these flags if it's in your JSON
                    # 'is_featured': item.get('is_featured', False), 
                }
            )

            if created:
                products_created += 1
                self.stdout.write(f"Created product: {product.name}")
            else:
                products_updated += 1
                self.stdout.write(f"Updated product: {product.name}")

            # 4. Clear old images and Add Product Images
            # This prevents duplicating all images every time the script runs
            product.images.all().delete()
            for img_url in item.get('images', []):
                if img_url: # Ensure URL is not empty
                    ProductImage.objects.create(product=product, image_url=img_url)

            # 5. Clear old variants and Add Product Variants
            product.variants.all().delete()
            sizes = item.get('size_variants', [])
            
            if not sizes:
                # Handle products with no explicit sizes (like wallets, watches)
                sizes = ['One Size']

            for size_name in sizes:
                size_obj, _ = Size.objects.get_or_create(size=size_name)
                
                # Using 0 as default stock, you can change this
                ProductVariant.objects.create(
                    product=product,
                    size=size_obj,
                    price=price, # Using main product price for variant
                    stock=100      # Setting default stock to 100
                )
                variants_created += 1

        self.stdout.write(self.style.SUCCESS("---------------------------------"))
        self.stdout.write(self.style.SUCCESS("Data import complete!"))
        self.stdout.write(f"Products Created: {products_created}")
        self.stdout.write(f"Products Updated: {products_updated}")
        self.stdout.write(f"Product Variants Created: {variants_created}")

