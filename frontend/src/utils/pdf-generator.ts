import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { getFindingComments, FindingComment } from '@/app/actions';
import { format } from 'date-fns';
import { logger } from './logger';

export const generateFindingPDF = async (finding: any) => {
  // 1. Fetch Comments
  let comments: FindingComment[] = [];
  try {
    comments = await getFindingComments(finding.id);
  } catch (e) {
    logger.error('Failed to fetch comments for PDF', { error: e });
  }

  // 2. Create a hidden container for the report
  // We place it off-screen but visible to the browser engine for rendering
  const reportContainer = document.createElement('div');
  reportContainer.id = 'pdf-report-generator';
  reportContainer.style.position = 'absolute';
  reportContainer.style.top = '-10000px';
  reportContainer.style.left = '-10000px';
  reportContainer.style.width = '210mm'; // A4 width
  reportContainer.style.minHeight = '297mm'; // A4 height
  reportContainer.style.backgroundColor = '#ffffff';
  reportContainer.style.color = '#1f2937'; // Gray-800
  reportContainer.style.fontFamily = 'ui-sans-serif, system-ui, sans-serif';
  reportContainer.style.padding = '40px';
  reportContainer.style.boxSizing = 'border-box';

  // Helper for Severity Color in Print
  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'critical':
        return '#e11d48'; // Rose-600
      case 'high':
        return '#ea580c'; // Orange-600
      case 'medium':
        return '#ca8a04'; // Yellow-600
      case 'low':
        return '#2563eb'; // Blue-600
      default:
        return '#64748b'; // Slate-500
    }
  };
  const severityColor = getSeverityColor(finding.severity);

  // 3. Construct HTML Content
  // Standard professional layout
  const htmlContent = `
    <div style="border-bottom: 2px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: start;">
        <div>
            <h1 style="font-size: 24px; font-weight: 800; color: #111827; margin: 0;">VULNSCANNER REPORT</h1>
            <p style="color: #6b7280; font-size: 12px; margin-top: 5px;">Generated on ${format(new Date(), 'PPP p')}</p>
        </div>
        <div style="text-align: right;">
            <div style="background-color: ${severityColor}; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; text-transform: uppercase; font-size: 14px; display: inline-block;">
                ${finding.severity}
            </div>
        </div>
    </div>

    <!-- Meta Data Table -->
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px;">
        <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 10px 0; color: #6b7280; font-weight: 600; width: 150px;">Project Name:</td>
            <td style="padding: 10px 0; color: #111827; font-weight: 600;">${finding.project_name || 'N/A'}</td>
            <td style="padding: 10px 0; color: #6b7280; font-weight: 600; width: 150px;">Project ID:</td>
            <td style="padding: 10px 0; color: #6b7280; font-family: monospace;">${finding.project_id}</td>
        </tr>
        <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 10px 0; color: #6b7280; font-weight: 600;">Vulnerability Title:</td>
            <td style="padding: 10px 0; color: #111827; font-weight: 700;" colspan="3">${finding.title}</td>
        </tr>
        <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 10px 0; color: #6b7280; font-weight: 600;">Status:</td>
            <td style="padding: 10px 0; color: #111827;">${finding.status}</td>
            <td style="padding: 10px 0; color: #6b7280; font-weight: 600;">Scan Date:</td>
            <td style="padding: 10px 0; color: #111827;">${finding.scan_created_at ? format(new Date(finding.scan_created_at), 'PPP') : 'N/A'}</td>
        </tr>
         <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 10px 0; color: #6b7280; font-weight: 600;">Identifiers:</td>
            <td style="padding: 10px 0; color: #111827; font-family: monospace;" colspan="3">
                CVE: ${finding.cve_id || 'N/A'} | CWE: ${finding.cwe_id || 'N/A'} | CVSS: ${finding.cvss_score || 'N/A'}
            </td>
        </tr>
    </table>

    <!-- Description -->
    <div style="margin-bottom: 30px;">
        <h3 style="font-size: 16px; font-weight: 700; color: #111827; border-bottom: 2px solid #f3f4f6; padding-bottom: 8px; margin-bottom: 12px;">Description</h3>
        <p style="color: #374151; line-height: 1.6; font-size: 14px;">${finding.description}</p>
        ${finding.location ? `<p style="margin-top: 10px; font-size: 13px; color: #4b5563;"><strong>Location:</strong> <span style="font-family: monospace; background: #f3f4f6; padding: 2px 4px; border-radius: 4px;">${finding.location}</span></p>` : ''}
    </div>

    <!-- Evidence -->
    ${
      finding.evidence
        ? `
    <div style="margin-bottom: 30px;">
        <h3 style="font-size: 16px; font-weight: 700; color: #111827; border-bottom: 2px solid #f3f4f6; padding-bottom: 8px; margin-bottom: 12px;">Evidence</h3>
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; font-family: monospace; font-size: 12px; color: #334155; white-space: pre-wrap; overflow-wrap: break-word;">${finding.evidence}</div>
    </div>
    `
        : ''
    }

    <!-- Remediation -->
    <div style="margin-bottom: 30px;">
        <h3 style="font-size: 16px; font-weight: 700; color: #111827; border-bottom: 2px solid #f3f4f6; padding-bottom: 8px; margin-bottom: 12px;">Remediation</h3>
        <div style="color: #374151; line-height: 1.6; font-size: 14px;">
            ${finding.remediation ? `<div style="white-space: pre-line;">${finding.remediation}</div>` : 'Follow standard security best practices for Input Validation and Output Encoding.'}
        </div>
    </div>

    <!-- Discussion / Comments -->
    <div style="margin-bottom: 30px; page-break-inside: avoid;">
        <h3 style="font-size: 16px; font-weight: 700; color: #111827; border-bottom: 2px solid #f3f4f6; padding-bottom: 8px; margin-bottom: 12px;">Discussion & Notes</h3>
        ${
          comments.length > 0
            ? `
            <div style="display: flex; flex-direction: column; gap: 15px;">
                ${comments
                  .map(
                    (c) => `
                    <div style="background: #f9fafb; padding: 12px; border-radius: 6px; border: 1px solid #f3f4f6;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px;">
                            <span style="font-weight: 700; color: #111827;">${c.user_email}</span>
                            <span style="color: #9ca3af;">${format(new Date(c.created_at), 'PP p')}</span>
                        </div>
                        <div style="font-size: 13px; color: #4b5563; line-height: 1.4;">${c.content}</div>
                    </div>
                `
                  )
                  .join('')}
            </div>
        `
            : `
            <p style="font-style: italic; color: #9ca3af; font-size: 14px;">No comments recorded for this finding.</p>
        `
        }
    </div>

    <!-- Footer -->
    <div style="margin-top: 50px; border-top: 1px solid #e5e7eb; padding-top: 20px; text-align: center; color: #9ca3af; font-size: 12px;">
        CONFIDENTIAL - Generated by VulnScanner System
    </div>
  `;

  reportContainer.innerHTML = htmlContent;
  document.body.appendChild(reportContainer);

  try {
    // Wait a brief moment for DOM to settle
    await new Promise((resolve) => setTimeout(resolve, 100));

    const canvas = await html2canvas(reportContainer, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
    });

    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const imgWidth = 210;
    const pageHeight = 297;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save(`VulnReport_${finding.cve_id || finding.id.slice(0, 8)}.pdf`);
  } catch (err) {
    logger.error('PDF Generation failed:', { err });
    alert('Failed to generate PDF. Please try again.');
  } finally {
    // Clean up
    if (document.body.contains(reportContainer)) {
      document.body.removeChild(reportContainer);
    }
  }
};
