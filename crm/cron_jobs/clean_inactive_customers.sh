#!/bin/bash

cd /root/alx/alx-backend-graphql_crm

deleted_count=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True).filter(created_at__lt=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

echo "$(date): Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
