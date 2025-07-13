#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

def send_order_reminders():
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    query = gql("""
    query GetPendingOrders($orderDateGte: Date) {
        orders(orderDateGte: $orderDateGte) {
            id
            customer {
                email
            }
            orderDate
        }
    }
    """)
    
    try:
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        result = client.execute(query, variable_values={"orderDateGte": seven_days_ago})
        
        orders = result.get('orders', [])
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for order in orders:
                log_entry = f"{timestamp}: Order ID {order['id']}, Customer Email: {order['customer']['email']}\n"
                log_file.write(log_entry)
        
        print("Order reminders processed!")
            
    except Exception as e:
        print(f"Error processing order reminders: {e}")

if __name__ == "__main__":
    send_order_reminders()
