import graphene
from graphene_django.types import DjangoObjectType
from .models import Product  # Assuming your Product model is in crm/models.py

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products_list = []

        for product in low_stock_products:
            product.stock += 10  # Increment stock by 10
            product.save()
            updated_products_list.append(product)

        message = f"Successfully updated stock for {len(updated_products_list)} products."
        return UpdateLowStockProducts(
            success=True,
            message=message,
            updated_products=updated_products_list
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(mutation=Mutation)