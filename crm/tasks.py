from datetime import datetime

try:
    from celery import shared_task
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport
    
    @shared_task
    def generate_crm_report():
        query = gql("""
        query GetCRMStats {
            customers {
                id
            }
            orders {
                id
                totalAmount
            }
        }
        """)
        
        try:
            transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
            client = Client(transport=transport)
            
            result = client.execute(query)
            
            customers = result.get('customers', [])
            orders = result.get('orders', [])
            
            total_customers = len(customers)
            total_orders = len(orders)
            total_revenue = sum(float(order.get('totalAmount', 0)) for order in orders)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"
            
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(report + '\n')
            
            print(f"CRM Report generated: {report}")
            return report
            
        except Exception as e:
            error_msg = f"Error generating CRM report: {e}"
            print(error_msg)
            return error_msg

except ImportError:
    # Celery not available, define a regular function
    def generate_crm_report():
        print("Celery not available - this would be a Celery task")
        return "Celery not installed"
