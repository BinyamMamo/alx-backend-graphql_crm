#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ -f "$PROJECT_DIR/manage.py" ]; then
    cd "$PROJECT_DIR"
    cwd=$(pwd)
    
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
else
    echo "$(date): Error - manage.py not found in $PROJECT_DIR" >> /tmp/customer_cleanup_log.txt
fi
