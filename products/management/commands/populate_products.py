import os
from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Category, Product, ProductImage

class Command(BaseCommand):
    help = 'Populates the database with sample products and categories'

    def handle(self, *args, **options):
        # Create categories
        categories = {
            'Necklaces': 'Elegant necklaces for all occasions',
            'Earrings': 'Beautiful earrings to complement your style',
            'Rings': 'Stunning rings for every occasion',
            'Bracelets': 'Chic bracelets to adorn your wrist',
            'Bangles': 'Traditional bangles for a classic look',
            'Anklets': 'Delicate anklets to complete your look'
        }
        
        # Create products with their respective images
        products_data = [
            {
                'name': 'Gold Necklace',
                'category': 'Necklaces',
                'description': 'Elegant gold necklace with intricate design',
                'price': 299.99,
                'material': 'gold',
                'image': 'Gold_necklace_luxury_jewelry_ae92c463.png',
                'is_featured': True
            },
            {
                'name': 'Gold Earrings',
                'category': 'Earrings',
                'description': 'Beautiful gold drop earrings',
                'price': 149.99,
                'material': 'gold',
                'image': 'Gold_drop_earrings_luxury_0b12974e.png',
                'is_featured': True
            },
            {
                'name': 'Gold Rings Set',
                'category': 'Rings',
                'description': 'Set of elegant gold rings',
                'price': 199.99,
                'material': 'gold',
                'image': 'Gold_rings_collection_luxury_7dd17464.png',
                'is_featured': True
            },
            {
                'name': 'Gold Bracelet',
                'category': 'Bracelets',
                'description': 'Chic gold bracelet',
                'price': 249.99,
                'material': 'gold',
                'image': 'Gold_bracelets_luxury_jewelry_4bb08424.png'
            },
            {
                'name': 'Gold Bangles',
                'category': 'Bangles',
                'description': 'Traditional gold bangles',
                'price': 179.99,
                'material': 'gold',
                'image': 'Golden_bangles_luxury_jewelry_bd905fe5.png'
            },
            {
                'name': 'Gold Anklet',
                'category': 'Anklets',
                'description': 'Delicate gold anklet',
                'price': 129.99,
                'material': 'gold',
                'image': 'Gold_anklets_luxury_jewelry_368c21b5.png'
            },
            {
                'name': 'Silver Necklace',
                'category': 'Necklaces',
                'description': 'Elegant silver necklace',
                'price': 199.99,
                'material': 'silver',
                'image': 'Silver_necklace_luxury_jewelry_e4df7341.png'
            },
            {
                'name': 'Silver Earrings',
                'category': 'Earrings',
                'description': 'Beautiful silver earrings',
                'price': 99.99,
                'material': 'silver',
                'image': 'Silver_earrings_luxury_jewelry_9a6e993d.png'
            },
            {
                'name': 'Silver Bangles',
                'category': 'Bangles',
                'description': 'Traditional silver bangles',
                'price': 149.99,
                'material': 'silver',
                'image': 'Silver_bangles_luxury_jewelry_b12c6d8a.png'
            }
        ]

        # Create categories
        category_objects = {}
        for name, description in categories.items():
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            category_objects[name] = category
            self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))

        # Create products
        for product_data in products_data:
            category_name = product_data.pop('category')
            image_name = product_data.pop('image')
            is_featured = product_data.get('is_featured', False)
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    **product_data,
                    'category': category_objects[category_name],
                    'is_featured': is_featured
                }
            )
            
            if created:
                # Add product image
                image_path = os.path.join('attached_assets', 'generated_images', image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        product_image = ProductImage(
                            product=product,
                            is_primary=True,
                            alt_text=f"{product.name} - {product.category.name}"
                        )
                        product_image.image.save(
                            image_name,
                            File(f),
                            save=True
                        )
                        product_image.save()
                        self.stdout.write(self.style.SUCCESS(f'Added image for {product.name}'))
                
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with products and categories!'))
