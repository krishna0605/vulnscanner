"""
Report generation tasks for scan results.
Handles PDF, CSV, and JSON report generation and storage.
"""

import json
import csv
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from io import StringIO, BytesIO
from celery import shared_task

from services.scan_service import ScanService
import os

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_report_task(self, scan_id: int, format: str = "json", user_id: int = None):
    """
    Generate a report for scan results.
    
    Args:
        scan_id: ID of the scan
        format: Report format (json, csv, pdf)
        user_id: ID of the user requesting the report
        
    Returns:
        Report generation result
    """
    try:
        scan_service = ScanService()
        
        # Get scan details
        scan = scan_service.get_scan_by_id(scan_id)
        if not scan:
            raise ValueError("Scan not found")
        
        # Get scan results
        urls = scan_service.get_scan_urls(scan_id)
        forms = scan_service.get_scan_forms(scan_id)
        technologies = scan_service.get_scan_technologies(scan_id)
        
        # Generate report based on format
        if format.lower() == "json":
            report_data = generate_json_report(scan, urls, forms, technologies)
            file_content = json.dumps(report_data, indent=2, default=str)
            content_type = "application/json"
            file_extension = "json"
            
        elif format.lower() == "csv":
            file_content = generate_csv_report(scan, urls, forms, technologies)
            content_type = "text/csv"
            file_extension = "csv"
            
        elif format.lower() == "pdf":
            file_content = generate_pdf_report(scan, urls, forms, technologies)
            content_type = "application/pdf"
            file_extension = "pdf"
            
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Generate filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"scan_report_{scan_id}_{timestamp}.{file_extension}"
        
        # Store report file (streaming-friendly writes to minimize memory)
        base_dir = os.path.join(".", "storage", "reports")
        os.makedirs(base_dir, exist_ok=True)
        file_path = os.path.join(base_dir, filename)

        if file_extension == "json":
            # Stream JSON content to file without holding entire string in memory
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('{"scan_info": ')
                json.dump(report_data["scan_info"], f, default=str)
                f.write(', "discovered_urls": [')
                first = True
                for url in urls:
                    item = {
                        "id": url.id,
                        "url": url.url,
                        "parent_url": url.parent_url,
                        "method": url.method,
                        "status_code": url.status_code,
                        "content_type": url.content_type,
                        "content_length": url.content_length,
                        "response_time": url.response_time,
                        "page_title": url.page_title,
                        "discovered_at": url.discovered_at.isoformat() if url.discovered_at else None,
                    }
                    if not first:
                        f.write(",")
                    json.dump(item, f, default=str)
                    first = False
                f.write('], "extracted_forms": [')
                first = True
                for form in forms:
                    item = {
                        "id": form.id,
                        "url_id": form.url_id,
                        "form_action": form.form_action,
                        "form_method": form.form_method,
                        "form_fields": form.form_fields,
                        "csrf_tokens": form.csrf_tokens,
                        "authentication_required": form.authentication_required,
                    }
                    if not first:
                        f.write(",")
                    json.dump(item, f, default=str)
                    first = False
                f.write('], "technology_fingerprints": [')
                first = True
                for tech in technologies:
                    item = {
                        "id": tech.id,
                        "url_id": tech.url_id,
                        "server_software": tech.server_software,
                        "programming_language": tech.programming_language,
                        "framework": tech.framework,
                        "cms": tech.cms,
                        "javascript_libraries": tech.javascript_libraries,
                        "security_headers": tech.security_headers,
                        "detected_at": tech.detected_at.isoformat() if tech.detected_at else None,
                    }
                    if not first:
                        f.write(",")
                    json.dump(item, f, default=str)
                    first = False
                f.write('], "summary": ')
                json.dump(report_data["summary"], f, default=str)
                f.write(', "generated_at": ')
                json.dump(report_data["generated_at"], f, default=str)
                f.write("}")
        elif file_extension == "csv":
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                # Summary
                f.write("SCAN SUMMARY\n")
                writer.writerow(["Scan ID", scan.id])
                writer.writerow(["Project ID", scan.project_id])
                writer.writerow(["Status", scan.status])
                writer.writerow(["Created At", scan.created_at])
                writer.writerow(["Total URLs", len(urls)])
                writer.writerow(["Total Forms", len(forms)])
                writer.writerow(["Total Technologies", len(technologies)])
                f.write("\n")
                # URLs
                f.write("DISCOVERED URLS\n")
                writer.writerow(["ID", "URL", "Parent URL", "Method", "Status Code", "Content Type", "Content Length", "Response Time", "Page Title", "Discovered At"])
                for url in urls:
                    writer.writerow([
                        url.id, url.url, url.parent_url, url.method, url.status_code,
                        url.content_type, url.content_length, url.response_time,
                        url.page_title, url.discovered_at
                    ])
                f.write("\n")
                # Forms
                f.write("EXTRACTED FORMS\n")
                writer.writerow(["ID", "URL ID", "Form Action", "Form Method", "Field Count", "CSRF Tokens", "Auth Required"])
                for form in forms:
                    writer.writerow([
                        form.id, form.url_id, form.form_action, form.form_method,
                        len(form.form_fields) if form.form_fields else 0,
                        len(form.csrf_tokens) if form.csrf_tokens else 0,
                        form.authentication_required
                    ])
                f.write("\n")
                # Technologies
                f.write("TECHNOLOGY FINGERPRINTS\n")
                writer.writerow(["ID", "URL ID", "Server Software", "Programming Language", "Framework", "CMS", "JS Libraries", "Security Headers", "Detected At"])
                for tech in technologies:
                    writer.writerow([
                        tech.id, tech.url_id, tech.server_software, tech.programming_language,
                        tech.framework, tech.cms,
                        len(tech.javascript_libraries) if tech.javascript_libraries else 0,
                        len(tech.security_headers) if tech.security_headers else 0,
                        tech.detected_at
                    ])
        else:
            # PDF already generated in memory; write bytes
            with open(file_path, "wb") as f:
                if isinstance(file_content, str):
                    f.write(file_content.encode("utf-8"))
                else:
                    f.write(file_content)
        
        logger.info(f"Report generated for scan {scan_id}: {filename}")
        return {
            "scan_id": scan_id,
            "format": format,
            "filename": filename,
            "file_url": file_path,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(file_content) if isinstance(file_content, str) else len(file_content)
        }

    except Exception as exc:
        logger.error(f"Error generating report for scan {scan_id}: {exc}", exc_info=True)
        # Let Celery handle retries if configured at task level
        raise


def generate_json_report(scan, urls, forms, technologies) -> Dict[str, Any]:
    """
    Generate JSON format report.
    
    Args:
        scan: Scan object
        urls: List of discovered URLs
        forms: List of extracted forms
        technologies: List of detected technologies
        
    Returns:
        Report data dictionary
    """
    return {
        "scan_info": {
            "id": scan.id,
            "project_id": scan.project_id,
            "status": scan.status,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "configuration": scan.configuration,
            "statistics": scan.stats
        },
        "discovered_urls": [
            {
                "id": url.id,
                "url": url.url,
                "parent_url": url.parent_url,
                "method": url.method,
                "status_code": url.status_code,
                "content_type": url.content_type,
                "content_length": url.content_length,
                "response_time": url.response_time,
                "page_title": url.page_title,
                "discovered_at": url.discovered_at.isoformat() if url.discovered_at else None
            }
            for url in urls
        ],
        "extracted_forms": [
            {
                "id": form.id,
                "url_id": form.url_id,
                "form_action": form.form_action,
                "form_method": form.form_method,
                "form_fields": form.form_fields,
                "csrf_tokens": form.csrf_tokens,
                "authentication_required": form.authentication_required
            }
            for form in forms
        ],
        "technology_fingerprints": [
            {
                "id": tech.id,
                "url_id": tech.url_id,
                "server_software": tech.server_software,
                "programming_language": tech.programming_language,
                "framework": tech.framework,
                "cms": tech.cms,
                "javascript_libraries": tech.javascript_libraries,
                "security_headers": tech.security_headers,
                "detected_at": tech.detected_at.isoformat() if tech.detected_at else None
            }
            for tech in technologies
        ],
        "summary": {
            "total_urls": len(urls),
            "total_forms": len(forms),
            "total_technologies": len(technologies),
            "unique_domains": len(set(url.url.split('/')[2] for url in urls if url.url)),
            "status_code_distribution": get_status_code_distribution(urls),
            "content_type_distribution": get_content_type_distribution(urls)
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


def generate_csv_report(scan, urls, forms, technologies) -> str:
    """
    Generate CSV format report.
    
    Args:
        scan: Scan object
        urls: List of discovered URLs
        forms: List of extracted forms
        technologies: List of detected technologies
        
    Returns:
        CSV content as string
    """
    output = StringIO()
    
    # Write scan summary
    output.write("SCAN SUMMARY\n")
    output.write(f"Scan ID,{scan.id}\n")
    output.write(f"Project ID,{scan.project_id}\n")
    output.write(f"Status,{scan.status}\n")
    output.write(f"Created At,{scan.created_at}\n")
    output.write(f"Total URLs,{len(urls)}\n")
    output.write(f"Total Forms,{len(forms)}\n")
    output.write(f"Total Technologies,{len(technologies)}\n")
    output.write("\n")
    
    # Write URLs section
    output.write("DISCOVERED URLS\n")
    url_writer = csv.writer(output)
    url_writer.writerow([
        "ID", "URL", "Parent URL", "Method", "Status Code", 
        "Content Type", "Content Length", "Response Time", "Page Title", "Discovered At"
    ])
    
    for url in urls:
        url_writer.writerow([
            url.id, url.url, url.parent_url, url.method, url.status_code,
            url.content_type, url.content_length, url.response_time, 
            url.page_title, url.discovered_at
        ])
    
    output.write("\n")
    
    # Write Forms section
    output.write("EXTRACTED FORMS\n")
    form_writer = csv.writer(output)
    form_writer.writerow([
        "ID", "URL ID", "Form Action", "Form Method", "Field Count", 
        "CSRF Tokens", "Auth Required"
    ])
    
    for form in forms:
        form_writer.writerow([
            form.id, form.url_id, form.form_action, form.form_method,
            len(form.form_fields) if form.form_fields else 0,
            len(form.csrf_tokens) if form.csrf_tokens else 0,
            form.authentication_required
        ])
    
    output.write("\n")
    
    # Write Technologies section
    output.write("TECHNOLOGY FINGERPRINTS\n")
    tech_writer = csv.writer(output)
    tech_writer.writerow([
        "ID", "URL ID", "Server Software", "Programming Language", 
        "Framework", "CMS", "JS Libraries", "Security Headers", "Detected At"
    ])
    
    for tech in technologies:
        tech_writer.writerow([
            tech.id, tech.url_id, tech.server_software, tech.programming_language,
            tech.framework, tech.cms,
            len(tech.javascript_libraries) if tech.javascript_libraries else 0,
            len(tech.security_headers) if tech.security_headers else 0,
            tech.detected_at
        ])
    
    return output.getvalue()


def generate_pdf_report(scan, urls, forms, technologies) -> bytes:
    """
    Generate PDF format report.
    
    Args:
        scan: Scan object
        urls: List of discovered URLs
        forms: List of extracted forms
        technologies: List of detected technologies
        
    Returns:
        PDF content as bytes
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Vulnerability Scan Report", title_style))
        story.append(Spacer(1, 20))
        
        # Scan Information
        story.append(Paragraph("Scan Information", styles['Heading2']))
        scan_data = [
            ["Scan ID", str(scan.id)],
            ["Project ID", str(scan.project_id)],
            ["Status", scan.status],
            ["Created At", str(scan.created_at)],
            ["Total URLs", str(len(urls))],
            ["Total Forms", str(len(forms))],
            ["Total Technologies", str(len(technologies))]
        ]
        
        scan_table = Table(scan_data, colWidths=[2*inch, 3*inch])
        scan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(scan_table)
        story.append(Spacer(1, 20))
        
        # URL Summary
        story.append(Paragraph("URL Discovery Summary", styles['Heading2']))
        status_dist = get_status_code_distribution(urls)
        
        if status_dist:
            status_data = [["Status Code", "Count"]]
            for status, count in status_dist.items():
                status_data.append([str(status), str(count)])
            
            status_table = Table(status_data, colWidths=[2*inch, 1*inch])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(status_table)
        
        story.append(Spacer(1, 20))
        
        # Technology Summary
        story.append(Paragraph("Technology Detection Summary", styles['Heading2']))
        
        tech_summary = {}
        for tech in technologies:
            if tech.server_software:
                tech_summary["Server"] = tech.server_software
            if tech.programming_language:
                tech_summary["Language"] = tech.programming_language
            if tech.framework:
                tech_summary["Framework"] = tech.framework
            if tech.cms:
                tech_summary["CMS"] = tech.cms
        
        if tech_summary:
            tech_data = [["Technology Type", "Detected"]]
            for tech_type, tech_name in tech_summary.items():
                tech_data.append([tech_type, tech_name])
            
            tech_table = Table(tech_data, colWidths=[2*inch, 3*inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tech_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        # Fallback to simple text-based PDF if reportlab is not available
        logger.warning("ReportLab not available, generating simple text report")
        return generate_simple_pdf_report(scan, urls, forms, technologies)


def generate_simple_pdf_report(scan, urls, forms, technologies) -> bytes:
    """
    Generate a simple text-based PDF report as fallback.
    
    Args:
        scan: Scan object
        urls: List of discovered URLs
        forms: List of extracted forms
        technologies: List of detected technologies
        
    Returns:
        Simple PDF content as bytes
    """
    # Create a simple text report
    report_text = f"""
VULNERABILITY SCAN REPORT

Scan Information:
- Scan ID: {scan.id}
- Project ID: {scan.project_id}
- Status: {scan.status}
- Created At: {scan.created_at}

Summary:
- Total URLs Discovered: {len(urls)}
- Total Forms Found: {len(forms)}
- Total Technologies Detected: {len(technologies)}

Status Code Distribution:
{get_status_code_summary(urls)}

Technology Summary:
{get_technology_summary(technologies)}

Generated At: {datetime.now(timezone.utc).isoformat()}
"""
    
    return report_text.encode('utf-8')


def get_status_code_distribution(urls) -> Dict[int, int]:
    """Get distribution of HTTP status codes."""
    distribution = {}
    for url in urls:
        if url.status_code:
            distribution[url.status_code] = distribution.get(url.status_code, 0) + 1
    return distribution


def get_content_type_distribution(urls) -> Dict[str, int]:
    """Get distribution of content types."""
    distribution = {}
    for url in urls:
        if url.content_type:
            content_type = url.content_type.split(';')[0]  # Remove charset info
            distribution[content_type] = distribution.get(content_type, 0) + 1
    return distribution


def get_status_code_summary(urls) -> str:
    """Get a text summary of status codes."""
    distribution = get_status_code_distribution(urls)
    if not distribution:
        return "No status codes recorded"
    
    summary_lines = []
    for status, count in sorted(distribution.items()):
        summary_lines.append(f"  {status}: {count}")
    
    return "\n".join(summary_lines)


def get_technology_summary(technologies) -> str:
    """Get a text summary of detected technologies."""
    if not technologies:
        return "No technologies detected"
    
    summary_lines = []
    for tech in technologies:
        if tech.server_software:
            summary_lines.append(f"  Server: {tech.server_software}")
        if tech.programming_language:
            summary_lines.append(f"  Language: {tech.programming_language}")
        if tech.framework:
            summary_lines.append(f"  Framework: {tech.framework}")
        if tech.cms:
            summary_lines.append(f"  CMS: {tech.cms}")
    
    return "\n".join(summary_lines) if summary_lines else "No specific technologies identified"


# Removed legacy duplicate task implementations that referenced undefined helpers.


@shared_task
def cleanup_old_reports():
    """
    Clean up old report files to save storage space.
    
    Returns:
        Cleanup summary
    """
    try:
        storage_service = StorageService()
        
        # Delete reports older than 30 days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        deleted_count = storage_service.cleanup_old_reports(cutoff_date)
        
        logger.info(f"Cleaned up {deleted_count} old reports")
        return {
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error cleaning up old reports: {exc}")
        return {"error": str(exc)}