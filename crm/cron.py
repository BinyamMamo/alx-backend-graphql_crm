import requests
import datetime
import json

def update_low_stock():
    graphql_endpoint = 'http://localhost:8000/graphql/'  # Adjust if your GraphQL endpoint is different
    query = """
        mutation {
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
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(graphql_endpoint, headers=headers, json={'query': query})
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        log_file_path = '/tmp/low_stock_updates_log.txt'
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(log_file_path, 'a') as log_file:
            log_file.write(f"--- Logged on: {timestamp} ---\n")
            if data and 'data' in data and 'updateLowStockProducts' in data['data']:
                mutation_result = data['data']['updateLowStockProducts']
                log_file.write(f"Success: {mutation_result['success']}\n")
                log_file.write(f"Message: {mutation_result['message']}\n")

                if mutation_result['updatedProducts']:
                    log_file.write("Updated Products:\n")
                    for product in mutation_result['updatedProducts']:
                        log_file.write(f"  - Name: {product['name']}, New Stock: {product['stock']}\n")
                else:
                    log_file.write("No products updated.\n")
            else:
                log_file.write(f"Error or unexpected response from GraphQL: {json.dumps(data)}\n")
            log_file.write("\n")

    except requests.exceptions.RequestException as e:
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"--- Logged on: {timestamp} ---\n")
            log_file.write(f"Network or GraphQL request error: {e}\n\n")
    except Exception as e:
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"--- Logged on: {timestamp} ---\n")
            log_file.write(f"An unexpected error occurred: {e}\n\n")