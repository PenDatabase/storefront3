from django.core.management.base import BaseCommand
import random
from decimal import Decimal
from uuid import uuid4
from faker import Faker
from django.contrib.auth import get_user_model
from store.models import (
    Promotion, Collection, Product,
    Customer, Order, OrderItem,
    Address, Cart, CartItem, Review
)
from django.db import transaction

User = get_user_model()
faker = Faker()


class Command(BaseCommand):
    help = 'Populates the database with collections and products'

    def handle(self, *args, **options):
        def create_users(n=5):
            users = []
            for _ in range(n):
                first_name = faker.first_name()
                last_name = faker.last_name()
                email = faker.email()
                password = "password123"
                user = User.objects.create_user(
                    username=email, email=email, password=password,
                    first_name=first_name, last_name=last_name
                )
                users.append(user)
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
            promotions = []
            for _ in range(n):
                promotion = Promotion.objects.create(
                    description=faker.sentence(nb_words=5),
                    discount=round(random.uniform(5, 50), 2)
                )
                promotions.append(promotion)
            return promotions

        def create_collections(n=3):
            collections = []
            for _ in range(n):
                collections.append(Collection.objects.create(
                    title=faker.word().capitalize()
                ))
            return collections

        def create_products(n=10, collections=None, promotions=None):
            products = []
            for _ in range(n):
                product = Product.objects.create(
                    title=faker.word().capitalize(),
                    slug=faker.slug(),
                    description=faker.text(),
                    unit_price=round(Decimal(random.uniform(10, 100)), 2),
                    inventory=random.randint(1, 100),
                    collection=random.choice(collections)
                )
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

        def create_orders(customers, products, n=5):
            orders = []
            for _ in range(n):
                customer = random.choice(customers)
                order = Order.objects.create(
                    customer=customer,
                    payment_status=random.choice(['P', 'C', 'F'])
                )
                for _ in range(random.randint(1, 4)):
                    OrderItem.objects.create(
                        order=order,
                        product=random.choice(products),
                        quantity=random.randint(1, 5),
                        unit_price=random.choice(products).unit_price
                    )
                orders.append(order)
            return orders

        def create_addresses(customers):
            for customer in customers:
                Address.objects.create(
                    customer=customer,
                    street=faker.street_address(),
                    city=faker.city()
                )

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
                for _ in range(random.randint(1, 3)):
                    Review.objects.create(
                        product=product,
                        name=faker.name(),
                        description=faker.text()
                    )

        print("Seeding database...")
        with transaction.atomic():
            users = create_users()
            promotions = create_promotions()
            collections = create_collections()
            products = create_products(collections=collections, promotions=promotions)
            customers = get_customers(users)
            create_addresses(customers)
            create_orders(customers, products)
            create_carts_and_items(products)
            create_reviews(products)

            print("✅ Seeding complete!")

