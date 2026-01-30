# Sentry Alerting Configuration Guide

## Overview

This document provides instructions for configuring alerting rules in the Sentry dashboard to complete the 100/100 Logging & Monitoring implementation.

## Required Alert Rules

### 1. High Error Volume Alert

**Purpose**: Notify when error rate exceeds normal levels.

**Configuration**:

- **Name**: `High Error Volume`
- **Trigger**: When number of errors is `>= 5` in `1 hour`
- **Filter**: `event.type:error`
- **Action**: Send notification to Slack/Email
- **Priority**: High

### 2. Critical Error Alert

**Purpose**: Immediate notification for critical/fatal errors.

**Configuration**:

- **Name**: `Critical Error Alert`
- **Trigger**: When an event matches `level:fatal OR level:critical`
- **Action**: Send notification immediately
- **Priority**: Critical

### 3. Performance Degradation Alert

**Purpose**: Notify when API response times exceed thresholds.

**Configuration**:

- **Name**: `Slow API Response`
- **Trigger**: When P95 latency `> 2000ms` for any transaction
- **Filter**: `transaction.op:http.server`
- **Action**: Send notification to Slack/Email
- **Priority**: Medium

### 4. Error Rate Spike Alert

**Purpose**: Detect sudden increases in error rate.

**Configuration**:

- **Name**: `Error Rate Spike`
- **Trigger**: When error rate increases by `> 50%` compared to previous period
- **Comparison Period**: Last 24 hours
- **Action**: Send notification to Slack/Email
- **Priority**: High

### 5. New Issue Alert

**Purpose**: Get notified about new, unseen errors.

**Configuration**:

- **Name**: `New Issue Detected`
- **Trigger**: When a new issue is first seen
- **Action**: Send notification to Slack/Email
- **Priority**: Medium

---

## Setup Instructions

### Step 1: Access Sentry Dashboard

1. Log in to [sentry.io](https://sentry.io)
2. Navigate to your project (vulnscanner)
3. Go to **Settings** → **Alerts**

### Step 2: Create Alert Rules

1. Click **Create Alert**
2. Select **Issues** or **Metrics** based on alert type
3. Configure triggers as specified above
4. Add notification channels (Slack, Email, PagerDuty, etc.)
5. Save the alert rule

### Step 3: Configure Notification Channels

1. Go to **Settings** → **Integrations**
2. Connect Slack workspace (for instant notifications)
3. Add team email addresses
4. Optionally configure PagerDuty for on-call rotations

### Step 4: Test Alerts

1. Trigger a test error in the application
2. Verify notification is received
3. Adjust thresholds if needed

---

## Recommended Thresholds

| Metric            | Warning  | Critical |
| ----------------- | -------- | -------- |
| Error Count (1hr) | > 5      | > 20     |
| P95 Latency       | > 1000ms | > 2000ms |
| Error Rate        | > 1%     | > 5%     |
| Apdex Score       | < 0.9    | < 0.7    |

---

## Integration with Incident Management

For production environments, consider integrating with:

- **PagerDuty**: For on-call rotations and escalations
- **Opsgenie**: For alert management
- **Slack**: For team-wide visibility
- **Jira**: For automatic ticket creation

---

## Environment Variables

Ensure these are set in your deployment:

```env
SENTRY_DSN=https://your-dsn@sentry.io/project-id
NEXT_PUBLIC_SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=1.0.0
```
