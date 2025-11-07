import json
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

# Replace 'store' with the name of your app where models are located
from products.models import Category, Product, ProductImage, Size, ProductVariant

class Command(BaseCommand):
    help = 'Loads products from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The path to the JSON file to load.')

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting product import...'))
        
        json_file_path = options['json_file']
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at: {json_file_path}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Error decoding JSON. Check the file for syntax errors.'))
            return

        total_products = len(products_data)
        skipped_count = 0
        processed_count = 0

        for i, item in enumerate(products_data):
            self.stdout.write(f'Processing product {i+1}/{total_products}: {item.get("title", "N/A")}')

            # --- 1. Handle Price ---
            # Skip products with a price of "0.00" or no price
            base_price_str = item.get('price', '0.00')
            if not base_price_str or float(base_price_str) == 0.0:
                self.stdout.write(self.style.WARNING(f"Skipping product '{item.get('title')}' due to zero or missing price."))
                skipped_count += 1
                continue
                
            base_price = Decimal(base_price_str)
            # Rule: Offer price is 10% off base price
            offer_price = base_price * Decimal('0.90') 

            # --- 2. Get or Create Category ---
            category_name = item.get('category')
            if not category_name:
                self.stdout.write(self.style.WARNING(f"Skipping product '{item.get('title')}' due to missing category."))
                skipped_count += 1
                continue
                
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Default description for {category_name}.'}
            )

            # --- 3. Handle Images ---
            images_list = item.get('images', [])
            if not images_list:
                self.stdout.write(self.style.WARNING(f"Skipping product '{item.get('title')}' due to no images."))
                skipped_count += 1
                continue
            
            # Use the first image as the main product image
            main_image_url = images_list[0]

            # --- 4. Create or Update Product ---
            # We use update_or_create to make the script re-runnable
            product, created = Product.objects.update_or_create(
                slug=item['handle'],
                defaults={
                    'name': item['title'],
                    'description': item['description'], # Rule: Load HTML description as-is
                    'base_price': base_price,
                    'offer_price': offer_price,
                    'image_url': main_image_url,
                    'image': None, # We populate image_url, not the ImageField (see note below)
                    'category': category,
                    # Add some randomness for the boolean fields
                    'is_featured': random.choice([True, False]),
                    'is_selective': random.choice([True, False]),
                    'is_most_demanded': random.choice([True, False]),
                    'is_blocked': False,
                }
            )
            
            if created:
                self.stdout.write(f"  Created new product: {product.name}")
            else:
                self.stdout.write(f"  Updated existing product: {product.name}")

            # --- 5. Populate Product Images ---
            # Delete old images for this product to avoid duplicates
            ProductImage.objects.filter(product=product).delete()
            for img_url in images_list:
                ProductImage.objects.create(
                    product=product,
                    image_url=img_url,
                    image=None # We populate image_url
                )
            self.stdout.write(f"  Added/Updated {len(images_list)} images for {product.name}")

            # --- 6. Populate Sizes and Variants ---
            size_variants_list = item.get('size_variants', [])
            
            # **Assumption**: If a product has no sizes (e.g., wallets, sunglasses),
            # we assign a default "One Size" variant.
            if not size_variants_list:
                size_variants_list = ["One Size"]

            # Delete old variants for this product to avoid duplicates
            ProductVariant.objects.filter(product=product).delete()

            for size_name in size_variants_list:
                # Get or create the Size object
                size_obj, _ = Size.objects.get_or_create(size=size_name)
                
                # Create the ProductVariant
                ProductVariant.objects.create(
                    product=product,
                    size=size_obj,
                    price=base_price, # JSON doesn't have per-size price, so use main price
                    stock=random.randint(50, 100) # Rule: Random stock 50-100
                )
            self.stdout.write(f"  Added/Updated {len(size_variants_list)} variants for {product.name}")
            processed_count += 1

        self.stdout.write(self.style.SUCCESS(f'\nImport complete!'))
        self.stdout.write(self.style.SUCCESS(f'Processed: {processed_count} products.'))
        self.stdout.write(self.style.WARNING(f'Skipped:   {skipped_count} products (due to zero price or missing data).'))