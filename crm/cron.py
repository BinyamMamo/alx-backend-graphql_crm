from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive\n"
    
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(message)
    
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        query = gql('{ hello }')
        result = client.execute(query)
        
        if result.get('hello'):
            print("GraphQL endpoint is responsive")
    except Exception as e:
        print(f"GraphQL endpoint check failed: {e}")

def update_low_stock():
    mutation = gql("""
    mutation UpdateLowStockProducts {
        updateLowStockProducts {
            success
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """)
    
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        result = client.execute(mutation)
        
        if result.get('updateLowStockProducts', {}).get('success'):
            updated_products = result.get('updateLowStockProducts', {}).get('updatedProducts', [])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                for product in updated_products:
                    log_entry = f"{timestamp}: Updated {product['name']} - New stock: {product['stock']}\n"
                    log_file.write(log_entry)
            
            print(f"Updated {len(updated_products)} low stock products")
        else:
            print("Failed to update low stock products")
            
    except Exception as e:
        print(f"Error updating low stock products: {e}")
