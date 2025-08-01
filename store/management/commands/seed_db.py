from django.core.management.base import BaseCommand
import random
from decimal import Decimal
from uuid import uuid4
from model_bakery import baker
from django.contrib.auth import get_user_model
from store.models import (
    Promotion, Collection, Product,
    Customer, Order, OrderItem,
    Address, Cart, CartItem, Review
)
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with collections and products'

    def handle(self, *args, **options):
        def create_users(n=5):
            users = baker.make(User, _quantity=n)
            # Include admin user in operations as well...
            admin = User.objects.filter(id=1).first()
            if admin is None:
                admin = User.objects.create_superuser(username="admin",
                                            password="admin")
                users.append(admin)
            else:
                users.append(admin)
            return users

        def create_promotions(n=3):
            promotions = baker.make(Promotion, _quantity=n)
            return promotions

        def create_collections(n=3):
            collections = baker.make(Collection, _quantity=n)
            return collections

        def create_products(n=10, collections=None, promotions=None):
            products = []
            for _ in range(n):
                product = baker.make(Product)
                if random.choice([True, False]):
                    product.promotions.set(random.sample(promotions, random.randint(1, len(promotions))))
                products.append(product)
            for collection in collections:
                collection.featured_product = random.choice(products)
                collection.save()
            return products

        def get_customers(users):
            customers = []
            for user in users:
                # Customers are automatically created when users are because of signals
                customers.append(Customer.objects.get(user=user))
            return customers

        def create_orders(customers, n=5):
            orders = []
            for customer in customers:
                order = baker.make(Order, customer=customer, _quantity=n)
                orders.append(order)
            return orders

        def create_addresses(customers):
            count = 0
            for customer in customers:
                baker.make(Address, customer=customer)

        def create_carts_and_items(products, n=3):
            for _ in range(n):
                cart = Cart.objects.create(id=uuid4())
                for _ in range(random.randint(1, 4)):
                    product=random.choice(products)
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=random.randint(1, 5)
                    )
                    products.remove(product)


        def create_reviews(products):
            for product in products:
                baker.make(Review, product=product, _quantity=random.randint(1, 3))

        print("Seeding database...")
        with transaction.atomic():
            users = create_users()
            promotions = create_promotions()
            collections = create_collections()
            products = create_products(collections=collections, promotions=promotions)
            customers = get_customers(users)
            create_addresses(customers)
            create_orders(customers)
            create_carts_and_items(products)
            create_reviews(products)

            print("✅ Seeding complete!")

