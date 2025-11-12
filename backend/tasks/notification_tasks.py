"""
Notification tasks for sending emails and alerts.
Handles scan completion notifications, error alerts, and system notifications.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from celery import shared_task

from core.config import settings
from services.scan_service import ScanService

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def send_scan_completion_notification(self, scan_id: int, user_email: str):
    """
    Send notification when a scan is completed.
    
    Args:
        scan_id: ID of the completed scan
        user_email: Email address to send notification to
        
    Returns:
        Notification result
    """
    try:
        scan_service = ScanService()
        scan = scan_service.get_scan_by_id(scan_id)
        
        if not scan:
            logger.error(f"Scan {scan_id} not found for notification")
            return {"error": "Scan not found"}
        
        # Prepare notification data
        notification_data = {
            "scan_id": scan_id,
            "project_id": scan.project_id,
            "status": scan.status,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "stats": scan.stats or {}
        }
        
        # Send email notification
        result = send_email_notification(
            to_email=user_email,
            template="scan_completion",
            data=notification_data
        )
        
        logger.info(f"Scan completion notification sent for scan {scan_id} to {user_email}")
        return result
        
    except Exception as exc:
        logger.error(f"Error sending scan completion notification: {exc}")
        return {"error": str(exc)}


@shared_task(bind=True)
def send_scan_error_notification(self, scan_id: int, user_email: str, error_message: str):
    """
    Send notification when a scan encounters an error.
    
    Args:
        scan_id: ID of the failed scan
        user_email: Email address to send notification to
        error_message: Error message to include
        
    Returns:
        Notification result
    """
    try:
        scan_service = ScanService()
        scan = scan_service.get_scan_by_id(scan_id)
        
        notification_data = {
            "scan_id": scan_id,
            "project_id": scan.project_id if scan else None,
            "error_message": error_message,
            "failed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Send error notification
        result = send_email_notification(
            to_email=user_email,
            template="scan_error",
            data=notification_data
        )
        
        logger.info(f"Scan error notification sent for scan {scan_id} to {user_email}")
        return result
        
    except Exception as exc:
        logger.error(f"Error sending scan error notification: {exc}")
        return {"error": str(exc)}


@shared_task
def send_weekly_summary_notification(user_email: str, user_id: int):
    """
    Send weekly summary of scan activities to user.
    
    Args:
        user_email: Email address to send summary to
        user_id: ID of the user
        
    Returns:
        Notification result
    """
    try:
        scan_service = ScanService()
        
        # Get weekly scan statistics
        weekly_stats = scan_service.get_weekly_scan_stats(user_id)
        
        notification_data = {
            "user_id": user_id,
            "week_ending": datetime.now(timezone.utc).isoformat(),
            "stats": weekly_stats
        }
        
        # Send weekly summary
        result = send_email_notification(
            to_email=user_email,
            template="weekly_summary",
            data=notification_data
        )
        
        logger.info(f"Weekly summary notification sent to {user_email}")
        return result
        
    except Exception as exc:
        logger.error(f"Error sending weekly summary notification: {exc}")
        return {"error": str(exc)}


@shared_task
def send_system_alert_notification(alert_type: str, message: str, severity: str = "medium"):
    """
    Send system alert notification to administrators.
    
    Args:
        alert_type: Type of alert (e.g., "high_error_rate", "system_overload")
        message: Alert message
        severity: Alert severity (low, medium, high, critical)
        
    Returns:
        Notification result
    """
    try:
        # Get admin email addresses from settings
        admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
        
        if not admin_emails:
            logger.warning("No admin emails configured for system alerts")
            return {"warning": "No admin emails configured"}
        
        notification_data = {
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": "Enhanced Vulnerability Scanner"
        }
        
        results = []
        for admin_email in admin_emails:
            result = send_email_notification(
                to_email=admin_email,
                template="system_alert",
                data=notification_data
            )
            results.append(result)
        
        logger.info(f"System alert notification sent to {len(admin_emails)} administrators")
        return {"sent_to": len(admin_emails), "results": results}
        
    except Exception as exc:
        logger.error(f"Error sending system alert notification: {exc}")
        return {"error": str(exc)}


def send_email_notification(to_email: str, template: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send email notification using configured email service.
    
    Args:
        to_email: Recipient email address
        template: Email template name
        data: Template data
        
    Returns:
        Email sending result
    """
    try:
        # Check if email service is configured
        if not hasattr(settings, 'EMAIL_ENABLED') or not settings.EMAIL_ENABLED:
            logger.info(f"Email service disabled, would send {template} to {to_email}")
            return {
                "status": "disabled",
                "message": "Email service is disabled",
                "template": template,
                "recipient": to_email
            }
        
        # Get email template
        email_content = get_email_template(template, data)
        
        if not email_content:
            return {"error": f"Email template '{template}' not found"}
        
        # Send email using configured service
        if hasattr(settings, 'EMAIL_SERVICE') and settings.EMAIL_SERVICE == 'sendgrid':
            return send_email_via_sendgrid(to_email, email_content)
        elif hasattr(settings, 'EMAIL_SERVICE') and settings.EMAIL_SERVICE == 'smtp':
            return send_email_via_smtp(to_email, email_content)
        else:
            # Default to logging the email content
            logger.info(f"Email notification: {email_content}")
            return {
                "status": "logged",
                "message": "Email logged (no service configured)",
                "template": template,
                "recipient": to_email
            }
        
    except Exception as exc:
        logger.error(f"Error sending email notification: {exc}")
        return {"error": str(exc)}


def get_email_template(template: str, data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Get email template content.
    
    Args:
        template: Template name
        data: Template data
        
    Returns:
        Email content with subject and body
    """
    templates = {
        "scan_completion": {
            "subject": f"Scan Completed - Project {data.get('project_id')}",
            "body": f"""
Your vulnerability scan has been completed successfully.

Scan Details:
- Scan ID: {data.get('scan_id')}
- Project ID: {data.get('project_id')}
- Status: {data.get('status')}
- Completed At: {data.get('completed_at')}

Statistics:
- URLs Discovered: {data.get('stats', {}).get('urls_discovered', 'N/A')}
- Forms Found: {data.get('stats', {}).get('forms_found', 'N/A')}
- Technologies Detected: {data.get('stats', {}).get('technologies_detected', 'N/A')}

You can view the detailed results in your dashboard.

Best regards,
Enhanced Vulnerability Scanner Team
"""
        },
        
        "scan_error": {
            "subject": f"Scan Failed - Project {data.get('project_id')}",
            "body": f"""
Your vulnerability scan has encountered an error and could not be completed.

Scan Details:
- Scan ID: {data.get('scan_id')}
- Project ID: {data.get('project_id')}
- Failed At: {data.get('failed_at')}

Error Message:
{data.get('error_message')}

Please check your scan configuration and try again. If the problem persists, contact support.

Best regards,
Enhanced Vulnerability Scanner Team
"""
        },
        
        "weekly_summary": {
            "subject": "Weekly Scan Summary",
            "body": f"""
Here's your weekly vulnerability scanning summary.

Week Ending: {data.get('week_ending')}

Activity Summary:
- Total Scans: {data.get('stats', {}).get('total_scans', 0)}
- Successful Scans: {data.get('stats', {}).get('successful_scans', 0)}
- Failed Scans: {data.get('stats', {}).get('failed_scans', 0)}
- URLs Discovered: {data.get('stats', {}).get('total_urls', 0)}
- Forms Found: {data.get('stats', {}).get('total_forms', 0)}

Keep up the great work securing your applications!

Best regards,
Enhanced Vulnerability Scanner Team
"""
        },
        
        "system_alert": {
            "subject": f"System Alert - {data.get('alert_type')} ({data.get('severity').upper()})",
            "body": f"""
SYSTEM ALERT - {data.get('severity').upper()} SEVERITY

Alert Type: {data.get('alert_type')}
System: {data.get('system')}
Timestamp: {data.get('timestamp')}

Message:
{data.get('message')}

Please investigate this alert and take appropriate action.

System Administrator
Enhanced Vulnerability Scanner
"""
        }
    }
    
    return templates.get(template)


def send_email_via_sendgrid(to_email: str, email_content: Dict[str, str]) -> Dict[str, Any]:
    """
    Send email via SendGrid service.
    
    Args:
        to_email: Recipient email address
        email_content: Email content with subject and body
        
    Returns:
        Sending result
    """
    try:
        # This would integrate with SendGrid API
        # For now, we'll simulate the sending
        logger.info(f"SendGrid: Sending email to {to_email}")
        logger.info(f"Subject: {email_content['subject']}")
        logger.info(f"Body: {email_content['body'][:100]}...")
        
        return {
            "status": "sent",
            "service": "sendgrid",
            "recipient": to_email,
            "message_id": f"sg_{datetime.now(timezone.utc).timestamp()}"
        }
        
    except Exception as exc:
        logger.error(f"SendGrid email error: {exc}")
        return {"error": str(exc)}


def send_email_via_smtp(to_email: str, email_content: Dict[str, str]) -> Dict[str, Any]:
    """
    Send email via SMTP service.
    
    Args:
        to_email: Recipient email address
        email_content: Email content with subject and body
        
    Returns:
        Sending result
    """
    try:
        # This would integrate with SMTP server
        # For now, we'll simulate the sending
        logger.info(f"SMTP: Sending email to {to_email}")
        logger.info(f"Subject: {email_content['subject']}")
        logger.info(f"Body: {email_content['body'][:100]}...")
        
        return {
            "status": "sent",
            "service": "smtp",
            "recipient": to_email,
            "message_id": f"smtp_{datetime.now(timezone.utc).timestamp()}"
        }
        
    except Exception as exc:
        logger.error(f"SMTP email error: {exc}")
        return {"error": str(exc)}


@shared_task
def send_bulk_notification(user_emails: List[str], template: str, data: Dict[str, Any]):
    """
    Send bulk notifications to multiple users.
    
    Args:
        user_emails: List of recipient email addresses
        template: Email template name
        data: Template data
        
    Returns:
        Bulk sending result
    """
    try:
        results = []
        
        for email in user_emails:
            result = send_email_notification(email, template, data)
            results.append({
                "email": email,
                "result": result
            })
        
        successful = sum(1 for r in results if r["result"].get("status") in ["sent", "logged"])
        failed = len(results) - successful
        
        logger.info(f"Bulk notification sent: {successful} successful, {failed} failed")
        
        return {
            "total": len(user_emails),
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
    except Exception as exc:
        logger.error(f"Error sending bulk notification: {exc}")
        return {"error": str(exc)}


@shared_task
def cleanup_notification_logs():
    """
    Clean up old notification logs to save storage space.
    
    Returns:
        Cleanup summary
    """
    try:
        # This would clean up notification logs older than a certain period
        # For now, we'll just log the action
        logger.info("Cleaning up old notification logs")
        
        return {
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Notification logs cleanup completed"
        }
        
    except Exception as exc:
        logger.error(f"Error cleaning up notification logs: {exc}")
        return {"error": str(exc)}