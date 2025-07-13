import graphene
from graphene_django import DjangoObjectType
from .models import Product, Order, Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

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
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType, order_date_gte=graphene.Date())
    customers = graphene.List(CustomerType)
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info, order_date_gte=None):
        orders = Order.objects.all()
        if order_date_gte:
            orders = orders.filter(order_date__gte=order_date_gte)
        return orders
    
    def resolve_customers(self, info):
        return Customer.objects.all()

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
