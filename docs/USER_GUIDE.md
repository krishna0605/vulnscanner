# 🛡️ VulnScanner User Guide

**Complete Guide to Using VulnScanner - AI-Powered Vulnerability Analysis Platform**

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard Overview](#2-dashboard-overview)
3. [Projects](#3-projects)
4. [Scanning](#4-scanning)
5. [Scan Results & Findings](#5-scan-results--findings)
6. [Reports](#6-reports)
7. [Security Academy](#7-security-academy)
8. [Settings & Profile](#8-settings--profile)
9. [Known Issues & Limitations](#9-known-issues--limitations)
10. [Troubleshooting](#10-troubleshooting)
11. [FAQ](#11-faq)

---

## 1. Getting Started

### 1.1 Creating an Account

1. Navigate to the VulnScanner website
2. Click **"Get Started"** or **"Sign Up"**
3. Choose your sign-up method:
   - **Email/Password**: Enter your email and create a strong password
   - **Google OAuth**: Click "Sign in with Google" for quick registration
4. Verify your email address by clicking the link sent to your inbox
5. Complete your profile setup

### 1.2 Logging In

1. Go to the login page
2. Enter your credentials or use Google OAuth
3. If you have **Two-Factor Authentication (2FA)** enabled:
   - Enter the 6-digit code from your authenticator app, OR
   - Request an Email OTP as a fallback option
4. You'll be redirected to your Dashboard

### 1.3 Setting Up 2FA (Recommended)

For enhanced security, enable Multi-Factor Authentication:

1. Go to **Settings → Security**
2. Click **"Enable Two-Factor Authentication"**
3. Scan the QR code with Google Authenticator or similar app
4. Enter the 6-digit verification code
5. **Save your backup codes** in a secure location

> ⚠️ **Important**: Store backup codes safely! They are the only way to recover your account if you lose access to your authenticator app.

---

## 2. Dashboard Overview

The Dashboard is your central hub for monitoring security across all projects.

### 2.1 Dashboard Sections

| Section | Description |
|---------|-------------|
| **Quick Stats** | Total projects, active scans, critical vulnerabilities, and security score |
| **Recent Scans** | List of your 5 most recent scans with status |
| **Vulnerability Trend** | Graph showing vulnerability discoveries over time |
| **Top Vulnerabilities** | Most common vulnerability types across all projects |
| **Quick Actions** | Buttons for "New Scan" and "New Project" |

### 2.2 Understanding Security Score

Your **Security Score** (0-100) reflects the overall security health:

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90-100 | Excellent | Few or no vulnerabilities found |
| 70-89 | Good | Minor issues to address |
| 50-69 | Fair | Moderate vulnerabilities present |
| 30-49 | Poor | Significant security issues |
| 0-29 | Critical | Immediate attention required |

The score is calculated based on:
- Number and severity of open vulnerabilities
- Ratio of resolved vs. open issues
- Time since last scan

### 2.3 Navigation Bar

The top navigation provides quick access to:

- **Dashboard**: Home view with overview stats
- **Projects**: Manage your projects
- **Scans**: View all scans and start new ones
- **Reports**: Generate and download reports
- **Academy**: Security learning resources
- **Settings**: Account and application settings
- **Profile Icon**: Quick access to profile and logout

---

## 3. Projects

Projects are containers for organizing your scans by website or application.

### 3.1 Creating a New Project

1. Click **"New Project"** button (found on Dashboard or Projects page)
2. Enter project details:
   - **Project Name**: A descriptive name (e.g., "Company Website")
   - **Description**: Optional details about the project
   - **Base URL**: The primary URL for this project (e.g., `https://example.com`)
3. Click **"Create Project"**

### 3.2 Project Dashboard

Each project has its own dashboard showing:

- **Project Overview**: Name, description, creation date
- **Scan Summary**: Total scans, last scan date, findings count
- **Vulnerability Distribution**: Chart showing severity breakdown
- **Recent Activity**: Timeline of recent scans and findings
- **Quick Actions**: Start new scan, view reports, edit settings

### 3.3 Managing Projects

| Action | How To |
|--------|--------|
| **Edit Project** | Click the gear icon or "Edit" button |
| **Delete Project** | Go to Project Settings → Delete Project |
| **View All Scans** | Click "View Scans" or navigate to Scans tab |
| **Archive Project** | Currently not available (planned feature) |

> ⚠️ **Warning**: Deleting a project removes ALL associated scans and findings permanently.

### 3.4 Project Status Indicators

- 🟢 **Active**: Receiving regular scans
- 🟡 **Idle**: No scans in the last 30 days
- 🔴 **Critical**: Has unresolved critical vulnerabilities

---

## 4. Scanning

### 4.1 Starting a New Scan

1. Navigate to a project or click **"New Scan"**
2. Configure scan settings:

| Setting | Options | Description |
|---------|---------|-------------|
| **Target URL** | Any valid URL | The starting point for the scan |
| **Scan Depth** | Quick / Standard / Deep | How many pages to analyze |
| **Include Subdomains** | Yes / No | Whether to scan subdomains |

3. Click **"Start Scan"**
4. You'll be redirected to the scan details page

### 4.2 Scan Depth Options

| Depth | Pages Analyzed | Best For |
|-------|----------------|----------|
| **Quick** | Up to 25 pages | Fast overview, CI/CD pipelines |
| **Standard** | Up to 100 pages | Regular security checks |
| **Deep** | Up to 500 pages | Comprehensive audits |

### 4.3 Live Scan Monitoring

While a scan is running, the scan details page shows:

- **Progress Bar**: Percentage of pages analyzed
- **Pages Crawled**: Count of analyzed pages
- **Findings Counter**: Real-time count of discovered issues
- **Live Console**: Streaming log of scan activity
- **Control Buttons**: Pause, Resume, or Cancel the scan

### 4.4 Scan Controls

| Button | Action |
|--------|--------|
| **Pause** | Temporarily stops the scan (can resume later) |
| **Resume** | Continues a paused scan |
| **Cancel** | Stops the scan permanently |

### 4.5 Scan Status Reference

| Status | Meaning |
|--------|---------|
| `queued` | Scan is waiting to start |
| `running` | Scan is actively analyzing pages |
| `paused` | Scan is temporarily stopped |
| `completed` | Scan finished successfully |
| `failed` | Scan encountered an error |
| `cancelled` | Scan was stopped by user |

---

## 5. Scan Results & Findings

### 5.1 Viewing Scan Results

After a scan completes:

1. Go to **Scans → [Your Scan]**
2. View the results summary:
   - Total findings by severity
   - Pages analyzed
   - Scan duration
   - Security score

### 5.2 Understanding Severity Levels

| Severity | Color | Description | Action Required |
|----------|-------|-------------|-----------------|
| **Critical** | 🔴 Red | Severe vulnerabilities requiring immediate fix | Fix within 24 hours |
| **High** | 🟠 Orange | Significant security risks | Fix within 1 week |
| **Medium** | 🟡 Yellow | Moderate issues | Fix within 1 month |
| **Low** | 🔵 Blue | Minor issues or best practice suggestions | Fix when possible |
| **Info** | ⚪ Gray | Informational findings | Review and note |

### 5.3 Vulnerability Types Detected

VulnScanner detects these vulnerability categories:

**Security Headers**
- Missing Content-Security-Policy (CSP)
- Missing HTTP Strict-Transport-Security (HSTS)
- Missing X-Frame-Options
- Server version disclosure
- Insecure cookie settings

**Content Issues**
- Mixed content (HTTP resources on HTTPS pages)
- Cross-Site Scripting (XSS) patterns
- Open redirect vulnerabilities
- Sensitive information in HTML comments

**Configuration Issues**
- Directory listing enabled
- Exposed admin/debug paths
- Insecure CORS configuration
- Missing security.txt

### 5.4 Finding Details

Click on any finding to see:

| Field | Description |
|-------|-------------|
| **Title** | Name of the vulnerability |
| **Severity** | Criticality level |
| **Location** | Affected URL(s) |
| **Description** | What the issue is |
| **Evidence** | Proof of the vulnerability |
| **Remediation** | How to fix the issue |
| **References** | Links to learn more |

### 5.5 Managing Findings

| Action | Description |
|--------|-------------|
| **Mark as Resolved** | Indicates the issue has been fixed |
| **Mark as False Positive** | Flags incorrect detection |
| **Add Comment** | Leave notes for team members |
| **Export** | Download finding details |

---

## 6. Reports

### 6.1 Accessing Reports

1. Navigate to **Reports** in the main menu
2. Select the scope:
   - **All Projects**: Aggregate report
   - **Specific Project**: Project-focused report
   - **Single Scan**: Detailed scan report

### 6.2 Report Types

| Report | Contents |
|--------|----------|
| **Executive Summary** | High-level overview for management |
| **Technical Report** | Detailed findings for developers |
| **Compliance Report** | Mapped to security standards |

### 6.3 Report Contents

Reports include:
- Vulnerability summary by severity
- Trend analysis over time
- Top vulnerability types
- Affected pages list
- Remediation recommendations
- Comparison with previous scans

### 6.4 Exporting Reports

Available formats:
- **PDF**: For sharing and printing
- **CSV**: For spreadsheet analysis
- **JSON**: For integration with other tools

---

## 7. Security Academy

The Security Academy provides learning resources to improve your security knowledge.

### 7.1 Available Sections

| Section | Description |
|---------|-------------|
| **CTF Practice** | Capture The Flag challenges to practice skills |
| **Resources** | Security tools, cheat sheets, and references |
| **News** | Latest cybersecurity news and updates |
| **Community** | Forums and community discussions |

### 7.2 Learning Resources

Each vulnerability type has associated learning materials:
- What the vulnerability is
- How attackers exploit it
- Real-world examples
- Step-by-step remediation guides
- Prevention best practices

---

## 8. Settings & Profile

### 8.1 Profile Settings

Access via **Settings → Profile** or click your avatar:

| Setting | Description |
|---------|-------------|
| **Display Name** | Your name shown in the app |
| **Avatar** | Profile picture (upload supported) |
| **Bio** | Short description about yourself |
| **Email** | Your account email (read-only) |

### 8.2 Security Settings

Access via **Settings → Security**:

| Setting | Description |
|---------|-------------|
| **Two-Factor Authentication** | Enable/disable 2FA |
| **Active Sessions** | View and manage logged-in sessions |
| **Password Change** | Update your password |
| **Account Activity** | View recent account actions |

### 8.3 Notification Settings

Access via **Settings → Notifications**:

| Notification | Options |
|--------------|---------|
| **Email Alerts** | Receive scan completion emails |
| **Critical Findings** | Immediate alerts for critical issues |
| **Weekly Digest** | Summary of security status |

### 8.4 Account Management

| Action | Location |
|--------|----------|
| **Export Data** | Settings → Account → Export Data |
| **Delete Account** | Settings → Account → Delete Account |

> ⚠️ **Warning**: Account deletion is permanent and removes all projects, scans, and findings.

---

## 9. Known Issues & Limitations

### 9.1 Current Known Issues

| Issue | Description | Workaround |
|-------|-------------|------------|
| **Assets Page Not Implemented** | The Assets feature shows placeholder content | Feature coming in future release |
| **Scan Score Display** | Some scan scores may show 0% incorrectly | Scores are calculated from findings |
| **Long Scan Times** | Deep scans on large sites can take 10+ minutes | Use Quick scan for faster results |
| **JavaScript-Heavy SPAs** | Some SPA content may not be fully analyzed | Enable JavaScript rendering option |

### 9.2 Browser Compatibility

| Browser | Support Level |
|---------|---------------|
| Chrome (latest) | ✅ Fully Supported |
| Firefox (latest) | ✅ Fully Supported |
| Safari (latest) | ✅ Fully Supported |
| Edge (latest) | ✅ Fully Supported |
| Internet Explorer | ❌ Not Supported |

### 9.3 Scan Limitations

| Limitation | Details |
|------------|---------|
| **Max Pages per Scan** | 500 pages (Deep scan) |
| **Scan Timeout** | 30 minutes per scan |
| **Concurrent Scans** | 2 scans simultaneously |
| **Rate Limiting** | Respectful crawling to avoid blocking |
| **Authentication** | Logged-in areas cannot be scanned (planned feature) |

### 9.4 Content Not Scanned

- Pages requiring authentication/login
- Content behind CAPTCHAs
- PDF, Word, and other document files
- Mobile app APIs (web only)
- Internal network addresses (security restriction)

---

## 10. Troubleshooting

### 10.1 Common Issues

#### "Scan Stuck at 0%"
**Cause**: Target URL may be unreachable or blocking the scanner.
**Solution**:
1. Verify the URL is accessible in your browser
2. Check if the site has aggressive bot protection
3. Try scanning a different URL on the same domain

#### "No Vulnerabilities Found"
**Cause**: Site may have excellent security, or scan depth was too shallow.
**Solution**:
1. Try a deeper scan (Standard or Deep)
2. Ensure correct target URL
3. Check scan logs for any errors

#### "Scan Failed"
**Cause**: Connection issues or server errors.
**Solution**:
1. Wait a few minutes and retry
2. Check your internet connection
3. View scan logs for specific error messages
4. Contact support if issue persists

#### "Cannot Login After 2FA Setup"
**Cause**: Authenticator app time may be out of sync.
**Solution**:
1. Ensure your phone's time is set to automatic
2. Use a backup code if available
3. Request Email OTP as alternative
4. Contact support for account recovery

#### "Dashboard Shows Wrong Data"
**Cause**: Data may be cached.
**Solution**:
1. Refresh the page
2. Clear browser cache
3. Log out and log back in

### 10.2 Getting Help

If you encounter issues not covered here:

1. Check the **FAQ** section below
2. Search **Security Academy** resources
3. Contact support at `support@vulnscanner.tech`
4. Include: Browser info, steps to reproduce, screenshots

---

## 11. FAQ

### General Questions

**Q: Is VulnScanner free?**
A: VulnScanner offers a free tier with limited scans. Premium plans provide additional features.

**Q: How long does a scan take?**
A: Quick scans: 1-3 minutes. Standard: 5-10 minutes. Deep: 15-30 minutes. Time varies based on site size.

**Q: Can I scan any website?**
A: You should only scan websites you own or have permission to test. Unauthorized scanning may be illegal.

**Q: Does scanning affect my website?**
A: VulnScanner uses passive scanning techniques. It reads pages like a regular visitor and doesn't attempt exploitation.

### Security Questions

**Q: Is my data secure?**
A: Yes. All data is encrypted in transit (HTTPS) and at rest. We follow security best practices.

**Q: Who can see my scan results?**
A: Only you can see your results. Data isolation is enforced at the database level.

**Q: Can I delete my data?**
A: Yes. You can delete individual scans, projects, or your entire account in Settings.

### Scan Questions

**Q: Why are some vulnerabilities not detected?**
A: VulnScanner focuses on common web vulnerabilities. Some issues require deeper analysis or login access.

**Q: Can I scan password-protected pages?**
A: Not currently. Authenticated scanning is a planned feature.

**Q: How often should I scan?**
A: We recommend weekly scans for active projects, or after each major deployment.

### Technical Questions

**Q: What browsers are supported?**
A: Chrome, Firefox, Safari, and Edge (latest versions). IE is not supported.

**Q: Can I use VulnScanner in CI/CD?**
A: API access for CI/CD integration is planned for a future release.

**Q: Is there a mobile app?**
A: Not currently. The web app is mobile-responsive.

---

## Quick Reference Card

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + N` | New Scan |
| `Ctrl/Cmd + P` | New Project |
| `Ctrl/Cmd + K` | Quick Search |
| `Esc` | Close modal/dialog |

### Severity Quick Guide

| Icon | Severity | Priority |
|------|----------|----------|
| 🔴 | Critical | Immediate |
| 🟠 | High | This week |
| 🟡 | Medium | This month |
| 🔵 | Low | When possible |
| ⚪ | Info | Review only |

### Status Icons

| Icon | Status |
|------|--------|
| ⏳ | Queued |
| ▶️ | Running |
| ⏸️ | Paused |
| ✅ | Completed |
| ❌ | Failed |
| 🚫 | Cancelled |

---

**Need more help?** Contact support at `support@vulnscanner.tech`

**Document Version:** 1.0.0  
**Last Updated:** February 7, 2026
