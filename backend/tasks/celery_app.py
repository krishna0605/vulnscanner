"""
Celery application configuration for background task processing.
Handles scan execution, report generation, and other async operations.
"""

import os
from celery import Celery
from kombu import Queue

# Import settings
from backend.core.config import settings

# Create Celery instance
celery_app = Celery(
    "vulnerability_scanner",
    broker=os.getenv("CELERY_BROKER_URL", settings.redis_url),
    backend=os.getenv("CELERY_RESULT_BACKEND", settings.redis_url),
    include=[
        "tasks.crawler_tasks",
        "tasks.report_tasks",
        "tasks.notification_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "tasks.crawler_tasks.*": {"queue": "crawler"},
        "tasks.report_tasks.*": {"queue": "reports"},
        "tasks.notification_tasks.*": {"queue": "notifications"},
    },
    
    # Queue definitions
    task_queues=(
        Queue("crawler", routing_key="crawler"),
        Queue("reports", routing_key="reports"),
        Queue("notifications", routing_key="notifications"),
        Queue("default", routing_key="default"),
    ),
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # Result settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security
    worker_hijack_root_logger=False,
    worker_log_color=False,
)

# Task annotations for specific configurations
celery_app.conf.task_annotations = {
    "tasks.crawler_tasks.start_crawl_task": {
        "rate_limit": "10/m",  # Max 10 crawls per minute
        "time_limit": 3600,    # 1 hour timeout
        "soft_time_limit": 3300,  # 55 minutes soft timeout
    },
    "tasks.report_tasks.generate_report_task": {
        "rate_limit": "20/m",  # Max 20 reports per minute
        "time_limit": 600,     # 10 minutes timeout
    },
    "tasks.notification_tasks.send_notification_task": {
        "rate_limit": "100/m",  # Max 100 notifications per minute
        "time_limit": 30,       # 30 seconds timeout
    },
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-scans": {
        "task": "tasks.crawler_tasks.cleanup_expired_scans",
        "schedule": 3600.0,  # Every hour
    },
    "health-check": {
        "task": "tasks.system_tasks.health_check",
        "schedule": 300.0,  # Every 5 minutes
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks()


@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    """Legacy email task - kept for compatibility"""
    # Placeholder: integrate real email provider later
    return {"to": to_email, "subject": subject}


if __name__ == "__main__":
    celery_app.start()