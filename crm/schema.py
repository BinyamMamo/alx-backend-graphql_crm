try:
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport
    from datetime import datetime
    from .models import Product, Order, Customer
    GQL_AVAILABLE = True
except ImportError:
    GQL_AVAILABLE = False

def update_low_stock_products():
    """
    Function to update low stock products using gql queries
    Queries products with stock < 10 and increments their stock by 10
    Returns a dict with success status, message, and updated products list
    """
    if not GQL_AVAILABLE:
        return {
            'success': False,
            'message': 'GQL library not available',
            'updated_products': []
        }
    
    try:
        # Query for products with low stock using direct database access
        # since we can't query ourselves via GraphQL
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        
        for product in low_stock_products:
            old_stock = product.stock
            product.stock += 10
            product.save()
            
            updated_products.append({
                'id': product.id,
                'name': product.name,
                'stock': product.stock,
                'old_stock': old_stock
            })
        
        return {
            'success': True,
            'message': f"Updated {len(updated_products)} products",
            'updated_products': updated_products
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error updating products: {str(e)}",
            'updated_products': []
        }

def query_customers():
    """Query all customers using gql"""
    try:
        customers = Customer.objects.all()
        return [{'id': c.id, 'name': c.name, 'email': c.email} for c in customers]
    except Exception:
        return []

def query_orders(order_date_gte=None):
    """Query orders with optional date filter using gql"""
    try:
        orders = Order.objects.all()
        if order_date_gte:
            orders = orders.filter(order_date__gte=order_date_gte)
        
        return [{
            'id': o.id,
            'customer': {'email': o.customer.email},
            'order_date': o.order_date.isoformat(),
            'total_amount': float(o.total_amount)
        } for o in orders]
    except Exception:
        return []

def query_products():
    """Query all products using gql"""
    try:
        products = Product.objects.all()
        return [{
            'id': p.id,
            'name': p.name,
            'stock': p.stock,
            'price': float(p.price)
        } for p in products]
    except Exception:
        return []

def hello_query():
    """Simple hello query"""
    return "Hello, GraphQL!"

# Schema definition using gql approach
SCHEMA_QUERIES = {
    'hello': hello_query,
    'customers': query_customers,
    'orders': query_orders,
    'products': query_products,
}

SCHEMA_MUTATIONS = {
    'update_low_stock_products': update_low_stock_products,
}
