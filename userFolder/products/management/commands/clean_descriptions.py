import html
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import strip_tags
from userFolder.products.models import Product  # Import your Product model

class Command(BaseCommand):
    help = 'Strips all HTML tags from the description field of all existing products.'

    @transaction.atomic  # Wrap the entire process in a single transaction
    def handle(self, *args, **options):
        self.stdout.write("Starting to clean product descriptions...")
        
        products_to_update = []
        total_checked = 0
        updated_count = 0

        # Use iterator() to handle potentially large numbers of products
        # without consuming too much memory.
        for product in Product.objects.all().iterator():
            total_checked += 1
            original_description = product.description
            
            if not original_description:
                continue  # Skip if description is already empty

            # 1. Use strip_tags to remove all HTML tags
            cleaned_description = strip_tags(original_description)
            
            # 2. Use html.unescape to fix things like '&nbsp;' or '&#39;'
            #    that might be left over (optional but good practice)
            cleaned_description = html.unescape(cleaned_description)
            
            # 3. Use strip() to remove any leading/trailing whitespace
            cleaned_description = cleaned_description.strip()

            # Only update if the description has actually changed
            if original_description != cleaned_description:
                product.description = cleaned_description
                products_to_update.append(product)
                updated_count += 1

            # Update in batches of 500 to be efficient
            if len(products_to_update) >= 500:
                self.stdout.write(f"Updating batch of {len(products_to_update)} products...")
                Product.objects.bulk_update(products_to_update, ['description'])
                products_to_update = []  # Clear the batch

        # Update any remaining products that are less than the batch size
        if products_to_update:
            self.stdout.write(f"Updating final batch of {len(products_to_update)} products...")
            Product.objects.bulk_update(products_to_update, ['description'])

        self.stdout.write(self.style.SUCCESS(f"\nCleaning finished!"))
        self.stdout.write(f"  - Total products checked: {total_checked}")
        self.stdout.write(f"  - Total products updated: {updated_count}")