from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import F
from userFolder.products.models import Product

class Command(BaseCommand):
    help = 'Updates the offer_price for all products to be 10% less than the base_price.'

    def handle(self, *args, **options):
        self.stdout.write("Starting price update...")

        # We want to set offer_price = base_price * 0.90
        # We use F() expressions to do this in a single, efficient database query
        # without loading all products into memory.
        # We use Decimal('0.90') for currency precision.
        
        update_count = Product.objects.all().update(
            offer_price=F('base_price') * Decimal('0.90')
        )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully updated the offer_price for {update_count} products."
        ))