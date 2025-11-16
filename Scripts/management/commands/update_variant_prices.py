import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, ProductVariant

class Command(BaseCommand):
    help = 'Updates all existing product variants with random prices and offers.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting variant price update...'))

        # Define your price range and offer percentage
        MIN_PRICE = Decimal('650.00')
        MAX_PRICE = Decimal('7999.00')
        OFFER_PERCENTAGE = Decimal('0.075') # 7.5%
        
        variants_to_update = []
        total_variants_updated = 0

        # Get all products and prefetch their variants to be efficient
        all_products = Product.objects.all().prefetch_related('variants__size')

        for product in all_products:
            self.stdout.write(f"Processing product: {product.name}")
            
            # Get all variants for this one product
            product_variants = list(product.variants.all())
            
            if not product_variants:
                self.stdout.write(self.style.WARNING(f"  -> No variants found for this product. Skipping."))
                continue

            # Loop through each variant (e.g., S, M, L) and give it a unique price
            for variant in product_variants:
                # 1. Generate a new random base price for THIS variant
                base_price = Decimal(random.uniform(float(MIN_PRICE), float(MAX_PRICE)))
                base_price = base_price.quantize(Decimal('0.01')) # Round to 2 decimal places

                # 2. Calculate the offer price
                offer_price = (base_price * (Decimal('1') - OFFER_PERCENTAGE))
                offer_price = offer_price.quantize(Decimal('0.01')) # Round to 2 decimal places

                # 3. Update the variant object in memory
                variant.base_price = base_price
                variant.offer_price = offer_price
                
                # 4. Add it to our list for bulk updating
                variants_to_update.append(variant)
                total_variants_updated += 1
                
                self.stdout.write(f"  -> Queued update for size '{variant.size.size}': Base=₹{base_price}, Offer=₹{offer_price}")

        # Now, update all variants in the database in one single query
        if variants_to_update:
            self.stdout.write(self.style.SUCCESS(f'\nApplying bulk update to {total_variants_updated} variants...'))
            ProductVariant.objects.bulk_update(variants_to_update, ['base_price', 'offer_price'])
            self.stdout.write(self.style.SUCCESS('All variant prices have been updated successfully!'))
        else:
            self.stdout.write(self.style.SUCCESS('No variants found to update.'))