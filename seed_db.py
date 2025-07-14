#!/usr/bin/env python
"""
Seed script to populate the CRM database with sample data.
Run this script to create sample customers, products, and orders.
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from crm.models import Customer, Product, Order, OrderItem

def create_customers():
    """Create sample customers"""
    customers_data = [
        {'name': 'Alice Johnson', 'email': 'alice@example.com', 'phone': '+1234567890'},
        {'name': 'Bob Smith', 'email': 'bob@example.com', 'phone': '123-456-7890'},
        {'name': 'Carol Williams', 'email': 'carol@example.com', 'phone': '+1987654321'},
        {'name': 'David Brown', 'email': 'david@example.com', 'phone': '987-654-3210'},
        {'name': 'Eve Davis', 'email': 'eve@example.com', 'phone': '+1122334455'},
    ]
    
    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        customers.append(customer)
        if created:
            print(f"Created customer: {customer.name}")
    
    return customers

def create_products():
    """Create sample products"""
    products_data = [
        {'name': 'Laptop', 'price': 999.99, 'stock': 15},
        {'name': 'Mouse', 'price': 29.99, 'stock': 8},  # Low stock
        {'name': 'Keyboard', 'price': 79.99, 'stock': 25},
        {'name': 'Monitor', 'price': 299.99, 'stock': 5},  # Low stock
        {'name': 'Headphones', 'price': 159.99, 'stock': 20},
        {'name': 'Webcam', 'price': 89.99, 'stock': 3},  # Low stock
    ]
    
    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        products.append(product)
        if created:
            print(f"Created product: {product.name} (Stock: {product.stock})")
    
    return products

def create_orders(customers, products):
    """Create sample orders"""
    for i, customer in enumerate(customers):
        # Create 1-3 orders per customer
        num_orders = random.randint(1, 3)
        
        for j in range(num_orders):
            # Random order date within last 30 days
            order_date = timezone.now() - timedelta(days=random.randint(0, 30))
            
            # Select 1-3 random products
            order_products = random.sample(products, random.randint(1, 3))
            total_amount = sum(p.price for p in order_products)
            
            order = Order.objects.create(
                customer=customer,
                order_date=order_date,
                total_amount=total_amount
            )
            
            # Create order items
            for product in order_products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=random.randint(1, 3)
                )
            
            print(f"Created order {order.id} for {customer.name} - ${total_amount}")

def main():
    """Main seeding function"""
    print("Seeding CRM database...")
    
    # Clear existing data (optional)
    print("Clearing existing data...")
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    
    # Create sample data
    customers = create_customers()
    products = create_products()
    create_orders(customers, products)
    
    print(f"\nSeeding complete!")
    print(f"Created {Customer.objects.count()} customers")
    print(f"Created {Product.objects.count()} products")
    print(f"Created {Order.objects.count()} orders")
    print(f"Products with low stock (< 10): {Product.objects.filter(stock__lt=10).count()}")

if __name__ == '__main__':
    main()
