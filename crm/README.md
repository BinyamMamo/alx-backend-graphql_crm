# CRM Celery Setup Instructions

## Prerequisites

1. **Install Redis Server**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Start Redis service
   sudo systemctl start redis-server  # Ubuntu/Debian
   brew services start redis           # macOS
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Setup Steps

1. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

2. **Apply Celery Beat Migrations**
   ```bash
   python manage.py migrate django_celery_beat
   ```

3. **Start Redis Server** (if not already running)
   ```bash
   redis-server
   ```

4. **Start Celery Worker** (in a separate terminal)
   ```bash
   celery -A crm worker -l info
   ```

5. **Start Celery Beat Scheduler** (in another separate terminal)
   ```bash
   celery -A crm beat -l info
   ```

6. **Start Django Development Server** (in another terminal)
   ```bash
   python manage.py runserver
   ```

## Testing

1. **Manual Task Execution**
   ```bash
   python manage.py shell
   >>> from crm.tasks import generate_crm_report
   >>> generate_crm_report.delay()
   ```

2. **Check Logs**
   ```bash
   tail -f /tmp/crm_report_log.txt
   ```

3. **Verify Scheduled Task**
   The CRM report will be automatically generated every Monday at 6:00 AM.

## Celery Beat Schedule

- **Task**: `generate_crm_report`
- **Schedule**: Every Monday at 6:00 AM
- **Log File**: `/tmp/crm_report_log.txt`

## Report Format

The report logs contain:
- Timestamp (YYYY-MM-DD HH:MM:SS)
- Total number of customers
- Total number of orders  
- Total revenue (sum of all order amounts)

Example:
```
2025-07-13 06:00:00 - Report: 150 customers, 89 orders, 15420.50 revenue
```
