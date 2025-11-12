"""
Celery application configuration for background task processing.
Handles scan execution, report generation, and other async operations.
"""

import os
from celery import Celery
from kombu import Queue

# Import settings
from core.config import settings


def create_celery_app() -> Celery:
    """Celery app factory using project settings and helpers.

    - Broker: RabbitMQ by default (AMQP URL)
    - Result backend: Redis DB 1 by default
    - JSON-only serialization
    - Default queue: crawler
    """
    app = Celery(
        "vulnerability_scanner",
        broker=settings.get_broker_url(),
        backend=settings.get_result_backend_url(),
        include=[
            "tasks.crawler_tasks",
            "tasks.report_tasks",
            "tasks.notification_tasks",
        ],
    )

    app.conf.update(
        # Default queue
        task_default_queue=settings.celery_queue,

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

        # Serialization
        accept_content=["json"],
        task_serializer="json",
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,

        # Execution settings
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        worker_prefetch_multiplier=1,
        task_time_limit=300,
        task_soft_time_limit=240,

        # Results
        result_expires=3600,
        result_persistent=True,

        # Retry defaults
        task_default_retry_delay=60,
        task_max_retries=3,

        # Worker settings
        worker_max_tasks_per_child=1000,
        worker_disable_rate_limits=False,

        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,

        # Security/logging
        worker_hijack_root_logger=False,
        worker_log_color=False,
    )

    # Task annotations
    app.conf.task_annotations = {
        "tasks.crawler_tasks.start_crawl_task": {
            "rate_limit": "10/m",
            "time_limit": 300,
            "soft_time_limit": 240,
        },
        "tasks.report_tasks.generate_report_task": {
            "rate_limit": "20/m",
            "time_limit": 600,
        },
    }

    # Auto-discover tasks from the `tasks` package
    app.autodiscover_tasks(packages=["tasks"])
    return app


# Expose Celery app for worker invocation: `celery -A tasks.celery_app worker ...`
celery_app = create_celery_app()

# Celery configuration
# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-scans": {
        "task": "tasks.crawler_tasks.cleanup_expired_scans",
        "schedule": 3600.0,
    },
}


@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    """Legacy email task - kept for compatibility"""
    # Placeholder: integrate real email provider later
    return {"to": to_email, "subject": subject}


if __name__ == "__main__":
    celery_app.start()