#!/usr/bin/env python3

import requests
from datetime import datetime, timedelta
import json

def send_order_reminders():
    query = """
    query GetPendingOrders {
        orders(orderDate_Gte: "%s") {
            id
            customer {
                email
            }
            orderDate
        }
    }
    """ % (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', {}).get('orders', [])
            
            with open('/tmp/order_reminders_log.txt', 'a') as log_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for order in orders:
                    log_entry = f"{timestamp}: Order ID {order['id']}, Customer Email: {order['customer']['email']}\n"
                    log_file.write(log_entry)
            
            print("Order reminders processed!")
        else:
            print(f"GraphQL request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Error processing order reminders: {e}")

if __name__ == "__main__":
    send_order_reminders()
