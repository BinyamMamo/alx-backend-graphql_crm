from datetime import datetime
import requests

def log_crm_heartbeat():
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive\n"
    
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(message)
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': '{ hello }'},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            print("GraphQL endpoint is responsive")
    except Exception as e:
        print(f"GraphQL endpoint check failed: {e}")

def update_low_stock():
    mutation = """
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
    """
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('data', {}).get('updateLowStockProducts', {})
            
            if result.get('success'):
                updated_products = result.get('updatedProducts', [])
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                    for product in updated_products:
                        log_entry = f"{timestamp}: Updated {product['name']} - New stock: {product['stock']}\n"
                        log_file.write(log_entry)
                
                print(f"Updated {len(updated_products)} low stock products")
            else:
                print("Failed to update low stock products")
        else:
            print(f"GraphQL request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Error updating low stock products: {e}")
