import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Product, Order, Customer
import re
from django.core.exceptions import ValidationError
from django.db import transaction

# Import filters when available
try:
    from .filters import CustomerFilter, ProductFilter, OrderFilter
    FILTERS_AVAILABLE = True
except ImportError:
    FILTERS_AVAILABLE = False

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        filter_fields = ['name', 'price', 'stock']
        interfaces = (graphene.relay.Node, )

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        filter_fields = ['name', 'email', 'created_at']
        interfaces = (graphene.relay.Node, )

# Task 1 & 2: Mutations
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    
    def mutate(self, info, input):
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists")
        
        # Validate phone format if provided
        if input.phone:
            phone_pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
            if not re.match(phone_pattern, input.phone):
                raise ValidationError("Invalid phone format")
        
        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=getattr(input, 'phone', '') or ''
        )
        
        return CreateCustomer(
            customer=customer,
            message="Customer created successfully"
        )

class BulkCreateCustomersInput(graphene.InputObjectType):
    customers = graphene.List(CreateCustomerInput, required=True)

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = BulkCreateCustomersInput(required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for customer_input in input.customers:
                try:
                    # Validate email uniqueness
                    if Customer.objects.filter(email=customer_input.email).exists():
                        errors.append(f"Email {customer_input.email} already exists")
                        continue
                    
                    # Validate phone format if provided
                    if hasattr(customer_input, 'phone') and customer_input.phone:
                        phone_pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
                        if not re.match(phone_pattern, customer_input.phone):
                            errors.append(f"Invalid phone format for {customer_input.name}")
                            continue
                    
                    customer = Customer.objects.create(
                        name=customer_input.name,
                        email=customer_input.email,
                        phone=getattr(customer_input, 'phone', '') or ''
                    )
                    customers.append(customer)
                    
                except Exception as e:
                    errors.append(f"Error creating {customer_input.name}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)
    
    product = graphene.Field(ProductType)
    
    def mutate(self, info, input):
        # Validate price is positive
        if input.price <= 0:
            raise ValidationError("Price must be positive")
        
        # Validate stock is non-negative
        if hasattr(input, 'stock') and input.stock is not None and input.stock < 0:
            raise ValidationError("Stock cannot be negative")
        
        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=getattr(input, 'stock', 0) or 0
        )
        
        return CreateProduct(product=product)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)
    
    order = graphene.Field(OrderType)
    
    def mutate(self, info, input):
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")
        
        # Validate products exist
        if not input.product_ids:
            raise ValidationError("At least one product must be selected")
        
        products = Product.objects.filter(id__in=input.product_ids)
        if len(products) != len(input.product_ids):
            raise ValidationError("Invalid product ID")
        
        # Calculate total amount
        total_amount = sum(product.price for product in products)
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=getattr(input, 'order_date', None)
        )
        
        # Associate products with order through OrderItem
        from .models import OrderItem
        for product in products:
            OrderItem.objects.create(order=order, product=product)
        
        return CreateOrder(order=order)

# Task 3: Update Low Stock Products (from cron project)
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass
    
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)
    
    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_products.append(product)
        
        return UpdateLowStockProducts(
            success=True,
            message=f"Updated {len(updated_products)} products",
            updated_products=updated_products
        )

class Query(graphene.ObjectType):
    hello = graphene.String()
    
    # Task 3: Filtered queries (when filters are available)
    if FILTERS_AVAILABLE:
        all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
        all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
        all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    # Simple list queries for compatibility
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType, order_date_gte=graphene.Date())
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info, order_date_gte=None):
        orders = Order.objects.all()
        if order_date_gte:
            orders = orders.filter(order_date__gte=order_date_gte)
        return orders

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)