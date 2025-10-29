import json
import os
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
# Corrected import based on your app structure
from userFolder.products.models import Category, Product, ProductImage, Size
from django.conf import settings # Import settings

# --- Configuration ---
# Build the path relative to the Django project's BASE_DIR
# This remains the primary, module-level path definition
MODULE_LEVEL_JSON_PATH = os.path.join(settings.BASE_DIR, 'userFolder', 'products', 'extracted_products_with_variants.json')
# ---------------------

class Command(BaseCommand):
    help = 'Loads product data from extracted_products_with_variants.json into the database'

    # Note on Django Warning: The warning "null has no effect on ManyToManyField"
    # means you can safely remove `null=True` from the `size` field in your
    # `userFolder/products/models.py` file. `blank=True` is sufficient.
    # This script will work fine either way, but fixing the model is good practice.

    @transaction.atomic # Ensure all operations succeed or fail together
    def handle(self, *args, **options):
        # Use a local variable within the handle method scope for the path
        effective_json_path = MODULE_LEVEL_JSON_PATH
        self.stdout.write(f"Looking for JSON data file at: {effective_json_path}")

        if not os.path.exists(effective_json_path):
            # Try an alternative path assuming the file might be in the project root
            alt_json_path = os.path.join(settings.BASE_DIR, 'extracted_products_with_variants.json')
            if os.path.exists(alt_json_path):
                 self.stdout.write(self.style.WARNING(f"File not found at primary path, using alternative: {alt_json_path}"))
                 effective_json_path = alt_json_path # Update the local variable
            else:
                 # Raise error using the original path and the alternative tried
                 raise CommandError(f"JSON file not found at {MODULE_LEVEL_JSON_PATH} or {alt_json_path}")

        try:
            # Use the determined effective_json_path
            with open(effective_json_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
        except json.JSONDecodeError:
            raise CommandError(f"Error decoding JSON from {effective_json_path}")
        except Exception as e:
            raise CommandError(f"Error reading file {effective_json_path}: {e}")

        self.stdout.write(f"Found {len(products_data)} products in the JSON file. Starting import...")

        created_count = 0
        updated_count = 0 # Added counter for updates
        skipped_count = 0
        error_count = 0
        all_sizes = {} # Cache Size objects to reduce DB queries
        all_categories = {} # Cache Category objects

        # Pre-fetch existing slugs to check for uniqueness efficiently
        existing_slugs = set(Product.objects.values_list('slug', flat=True))
        # Pre-fetch existing sizes for faster lookups
        for size_obj in Size.objects.all():
            all_sizes[size_obj.size] = size_obj
        # Pre-fetch existing categories for faster lookups
        for cat_obj in Category.objects.all():
            all_categories[cat_obj.name] = cat_obj


        for product_data in products_data:
            # Define product_slug here to ensure it's available in except block
            product_slug = None
            try:
                # --- 1. Get or Create Category ---
                category_name = product_data.get('category')
                if not category_name:
                    self.stdout.write(self.style.WARNING(f"Skipping product ID {product_data.get('id')} due to missing category."))
                    skipped_count += 1
                    continue

                if category_name in all_categories:
                    category = all_categories[category_name]
                else:
                    self.stdout.write(f"Creating new category: {category_name}")
                    category = Category.objects.create(
                        name=category_name,
                        description='' # Add default description if needed
                    )
                    all_categories[category_name] = category


                # --- 2. Get or Create Sizes ---
                size_list = []
                size_names = product_data.get('size_variants', [])
                if size_names: # Only process if there are sizes
                    for size_name in size_names:
                        if not size_name: continue # Skip empty size names

                        if size_name in all_sizes:
                            size_obj = all_sizes[size_name]
                        else:
                            self.stdout.write(f"Creating new size: {size_name}")
                            size_obj = Size.objects.create(size=size_name)
                            all_sizes[size_name] = size_obj
                        size_list.append(size_obj)

                # --- 3. Prepare Product Data ---
                product_name = product_data.get('title')
                handle = product_data.get('handle')
                description = product_data.get('description', '') # Default to empty string
                price_str = product_data.get('price', '0.00')
                images = product_data.get('images', [])
                first_image_url = images[0] if images else '' # Use first image for main Product image

                if not product_name or not handle:
                    self.stdout.write(self.style.WARNING(f"Skipping product ID {product_data.get('id')} due to missing title or handle."))
                    skipped_count += 1
                    continue

                # --- Price Handling ---
                try:
                    # Handle potential None or empty string price
                    price_str = price_str if price_str else '0.00'
                    # Handle cases where price might be "0" or similar non-decimal strings
                    if not isinstance(price_str, str): price_str = str(price_str)
                    price = Decimal(price_str)
                except InvalidOperation:
                    self.stdout.write(self.style.WARNING(f"Invalid price '{price_str}' for product '{product_name}'. Setting price to 0.00."))
                    price = Decimal('0.00')

                # --- Slug Handling (Ensure Uniqueness) ---
                base_slug = slugify(handle) # Use handle for slug base
                product_slug = base_slug
                counter = 1
                # Check against the set of slugs already used *in this run* AND slugs from DB
                while product_slug in existing_slugs: # Check combined set
                    product_slug = f"{base_slug}-{counter}"
                    counter += 1
                existing_slugs.add(product_slug) # Add the guaranteed unique slug


                # --- 4. Create or Update Product ---
                product, created = Product.objects.update_or_create(
                    slug=product_slug, # Use slug as the unique identifier
                    defaults={
                        'name': product_name[:1024], # Truncate if necessary
                        'description': description,
                        'price': price,
                        'image': first_image_url[:1024] if first_image_url else '', # Truncate URL
                        'category': category,
                    }
                )

                # --- 5. Set ManyToMany Sizes ---
                if size_list:
                    product.size.set(size_list)
                elif not created: # If updating and there are no sizes now, clear existing ones
                     product.size.clear()


                # --- 6. Create Product Images ---
                if not created:
                    product.images.all().delete()

                image_objects_to_create = []
                for image_url in images:
                    if image_url:
                         image_objects_to_create.append(
                            ProductImage(product=product, image_url=image_url[:1024]) # Truncate URL
                         )
                if image_objects_to_create:
                    ProductImage.objects.bulk_create(image_objects_to_create)


                if created:
                    created_count += 1
                else:
                    self.stdout.write(self.style.NOTICE(f"Updated existing product with slug: {product_slug}"))
                    updated_count += 1


            except Exception as e:
                # Ensure product_slug has a value for the error message
                slug_for_error = product_slug if product_slug is not None else (product_data.get('handle') or 'N/A')
                self.stdout.write(self.style.ERROR(f"Error processing product ID {product_data.get('id', 'N/A')} (Slug attempt: {slug_for_error}): {e}"))
                import traceback
                self.stdout.write(traceback.format_exc()) # Print full traceback for debugging
                error_count += 1
                # The transaction.atomic will roll back this specific product on error

        # --- Summary ---
        self.stdout.write(self.style.SUCCESS(f"\nImport finished!"))
        self.stdout.write(f"  - Successfully created products: {created_count}")
        self.stdout.write(f"  - Successfully updated products: {updated_count}")
        self.stdout.write(f"  - Skipped products (missing data): {skipped_count}")
        self.stdout.write(f"  - Errors encountered: {error_count}")

