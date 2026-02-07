# Live Scan Feature Implementation Plan

## Overview

The Live Scan feature enables users to monitor active vulnerability scans in real-time, with the ability to control scans (pause/resume/stop) while scans continue running in the background even if users navigate away or close their browser tab.

---

## Current State Analysis

### What Already Exists ✅

| Component | Location | Status |
|-----------|----------|--------|
| **Real-time Subscriptions** | [active-scans.tsx](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/components/scans/active-scans.tsx) | ✅ Working - Uses Supabase Realtime |
| **Progress Updates** | `crawler.ts:updateProgress()` | ✅ Working - Updates `progress` and `current_action` |
| **Scan Columns** | Database | ✅ Has `progress`, `current_action`, `node`, `started_at` |
| **Live Console** | `scans/[id]/page.tsx` | ✅ Shows real-time logs and findings |
| **Stop Scan (Basic)** | Scan Detail Page | ⚠️ Partial - Only sets status to 'failed' |

### What Needs to Be Fixed/Added ❌

| Issue | Impact |
|-------|--------|
| **Pause/Stop buttons non-functional** | Users cannot control scans from the Active Scans table |
| **No pause state in crawler** | Crawler doesn't check for paused state |
| **No 'paused' status** | Database only has queued/scanning/completed/failed |
| **Limited action feedback** | Pause/Stop actions have no visual confirmation |

---

## Architecture Diagram

```mermaid
flowchart TB
    subgraph Frontend["Frontend (Next.js)"]
        AS["Active Scans Table<br/>active-scans.tsx"]
        SD["Scan Details Page<br/>scans/[id]/page.tsx"]
        API["API Client<br/>api-client.ts"]
    end

    subgraph Supabase["Supabase"]
        RT["Realtime<br/>postgres_changes"]
        DB[("Database<br/>scans table")]
    end

    subgraph Backend["Backend (Fastify)"]
        SR["Scan Routes<br/>scans.ts"]
        CS["Crawler Service<br/>crawler.ts"]
    end

    AS -->|"Subscribe"| RT
    SD -->|"Subscribe"| RT
    RT -->|"Live Updates"| AS
    RT -->|"Live Updates"| SD
    
    AS -->|"Pause/Resume/Stop"| SR
    SD -->|"Stop Scan"| DB
    
    SR -->|"Update Status"| DB
    CS -->|"Check Status Loop"| DB
    CS -->|"updateProgress()"| DB
    DB -->|"Trigger"| RT

    style RT fill:#3b82f6,color:white
    style CS fill:#10b981,color:white
    style DB fill:#f59e0b,color:white
```

---

## Data Flow: Live Scan Updates

```mermaid
sequenceDiagram
    participant U as User Browser
    participant FE as Frontend
    participant SB as Supabase Realtime
    participant DB as Database
    participant CS as Crawler Service

    Note over U,CS: Scan Started
    
    CS->>DB: INSERT scan (status: 'queued')
    DB->>SB: Trigger postgres_changes
    SB->>FE: New scan event
    FE->>U: Display in Active Scans
    
    loop Every Page Scanned
        CS->>DB: UPDATE progress, current_action
        DB->>SB: Trigger UPDATE event
        SB->>FE: Push update
        FE->>U: Animate progress bar
    end
    
    Note over U,CS: User Clicks Pause
    
    U->>FE: Click Pause button
    FE->>DB: UPDATE status = 'paused'
    DB->>SB: Trigger UPDATE event
    SB->>FE: Status changed
    FE->>U: Show Paused state
    
    CS->>DB: Check status
    Note over CS: Crawler enters wait loop
    
    Note over U,CS: User Clicks Resume
    
    U->>FE: Click Resume button
    FE->>DB: UPDATE status = 'scanning'
    DB->>SB: Trigger UPDATE event
    SB->>FE: Status changed
    FE->>U: Show Running state
    
    CS->>DB: Check status
    Note over CS: Crawler resumes work
```

---

## Proposed Changes

### Database

#### [MODIFY] Scans Table Schema

Add new status values and ensure realtime is enabled:

```sql
-- Add 'paused' and 'cancelled' to valid scan statuses
-- Current: queued, scanning, processing, completed, failed
-- New: queued, scanning, processing, paused, completed, failed, cancelled
```

---

### Backend

#### [MODIFY] [crawler.ts](file:///c:/Users/Admin/Desktop/vulscanner/backend/src/lib/crawler.ts)

**Changes:**
1. Add pause/resume loop in the main scan loop
2. Check for 'paused' status and wait instead of continuing
3. Add graceful cancellation handler

```diff
+ // Inside the main while loop (around line 277-290)
+ const { data: currentScan } = await supabase
+   .from('scans')
+   .select('status')
+   .eq('id', this.scanId)
+   .single();
+ 
+ if (currentScan?.status === 'paused') {
+   await this.log('⏸️ Scan paused by user. Waiting...', 'info');
+   await this.updateProgress(this.lastProgress, 'Paused by user');
+   // Wait and re-check every 2 seconds
+   while (true) {
+     await new Promise(r => setTimeout(r, 2000));
+     const { data: check } = await supabase...
+     if (check?.status !== 'paused') break;
+   }
+   await this.log('▶️ Scan resumed!', 'success');
+ }
+ 
  if (currentScan?.status === 'cancelled') {
    await this.log('🛑 Scan cancelled.', 'warn');
    break;
  }
```

---

#### [MODIFY] [scans.ts](file:///c:/Users/Admin/Desktop/vulscanner/backend/src/routes/scans.ts)

**Changes:**
1. Add `PATCH /scans/:id/pause` endpoint
2. Add `PATCH /scans/:id/resume` endpoint  
3. Add `PATCH /scans/:id/cancel` endpoint

```typescript
// New endpoints to add:

// Pause scan
fastify.patch('/scans/:id/pause', async (request, reply) => {
  const { id } = request.params;
  await supabase.from('scans')
    .update({ status: 'paused', current_action: 'Paused' })
    .eq('id', id);
  return success({ status: 'paused' });
});

// Resume scan
fastify.patch('/scans/:id/resume', async (request, reply) => {
  const { id } = request.params;
  await supabase.from('scans')
    .update({ status: 'scanning', current_action: 'Resuming...' })
    .eq('id', id);
  return success({ status: 'scanning' });
});

// Cancel scan
fastify.patch('/scans/:id/cancel', async (request, reply) => {
  const { id } = request.params;
  await supabase.from('scans')
    .update({ status: 'cancelled', current_action: 'Cancelled by user' })
    .eq('id', id);
  return success({ status: 'cancelled' });
});
```

---

### Frontend

#### [MODIFY] [active-scans.tsx](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/components/scans/active-scans.tsx)

**Changes:**
1. Add functional Pause/Resume toggle button
2. Add functional Stop button
3. Add visual feedback for paused state
4. Add toast notifications for actions

```diff
  // Line 197-210: Replace non-functional buttons with working ones
  
- <button className="..." title="Pause Scan">
-   <Pause />
- </button>
+ <button 
+   onClick={() => handlePause(scan.id, scan.status)}
+   className="..."
+ >
+   {scan.status === 'PAUSED' ? <Play /> : <Pause />}
+ </button>

- <button className="..." title="Stop Scan">
-   <Square />
- </button>
+ <button onClick={() => handleCancel(scan.id)}>
+   <Square />
+ </button>
```

**New handler functions:**
```typescript
const handlePause = async (scanId: string, currentStatus: string) => {
  const endpoint = currentStatus === 'PAUSED' ? 'resume' : 'pause';
  await fetch(`${API_URL}/scans/${scanId}/${endpoint}`, { method: 'PATCH' });
};

const handleCancel = async (scanId: string) => {
  if (confirm('Are you sure?')) {
    await fetch(`${API_URL}/scans/${scanId}/cancel`, { method: 'PATCH' });
  }
};
```

---

#### [MODIFY] [api-client.ts](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/lib/api-client.ts)

**Changes:**
1. Add scan control API functions
2. Update [ActiveScanItem](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/lib/api-client.ts#6-17) interface to include 'paused' status

```typescript
// New exports:
export async function pauseScan(scanId: string): Promise<void> { ... }
export async function resumeScan(scanId: string): Promise<void> { ... }
export async function cancelScan(scanId: string): Promise<void> { ... }
```

---

## UI State Diagram

```mermaid
stateDiagram-v2
    [*] --> Queued: Scan Created
    Queued --> Scanning: Worker picks up
    Scanning --> Paused: User clicks Pause
    Paused --> Scanning: User clicks Resume
    Scanning --> Completed: All pages done
    Scanning --> Cancelled: User clicks Stop
    Paused --> Cancelled: User clicks Stop
    Scanning --> Failed: Error occurs
    
    Completed --> [*]
    Cancelled --> [*]
    Failed --> [*]
```

---

## Visual States for Active Scans Table

| Status | Progress Bar Color | Status Text | Action Buttons |
|--------|-------------------|-------------|----------------|
| `scanning` | Blue (animated pulse) | `SCANNING...` | ⏸️ Pause, ⏹️ Stop |
| `paused` | Yellow (static) | `PAUSED` | ▶️ Resume, ⏹️ Stop |
| `queued` | Gray | `QUEUED` | ⏹️ Stop only |

---

## Verification Plan

### Automated Tests

**Backend Unit Tests** - Run with: `cd backend && npm test`

The existing test file [scans.test.ts](file:///c:/Users/Admin/Desktop/vulscanner/backend/tests/scans.test.ts) can be extended with:
- Test `PATCH /scans/:id/pause` returns 200 and updates status
- Test `PATCH /scans/:id/resume` returns 200 and updates status
- Test `PATCH /scans/:id/cancel` returns 200 and updates status

### Manual Verification

1. **Start a new scan** from `/scans/new`
2. Navigate to `/scans` page and observe the Active Scans table
3. **Test Pause:**
   - Click the Pause button on an active scan
   - Verify progress bar turns yellow and shows "PAUSED"
   - Verify the scan log shows "Scan paused by user"
4. **Test Resume:**
   - Click the Resume/Play button
   - Verify progress continues and status shows "SCANNING"
5. **Test Stop:**
   - Click the Stop button
   - Confirm the action in the dialog
   - Verify the scan disappears from Active Scans and appears in History as "Cancelled"
6. **Test Background Persistence:**
   - Start a scan
   - Navigate away from the Scans page (e.g., to Dashboard)
   - Wait 30 seconds
   - Return to Scans page
   - Verify the scan has progressed and shows current status

---

## Summary of Files to Modify

| File | Type | Changes |
|------|------|---------|
| [backend/src/lib/crawler.ts](file:///c:/Users/Admin/Desktop/vulscanner/backend/src/lib/crawler.ts) | Backend | Add pause/resume loop logic |
| [backend/src/routes/scans.ts](file:///c:/Users/Admin/Desktop/vulscanner/backend/src/routes/scans.ts) | Backend | Add 3 new API endpoints |
| [frontend/src/components/scans/active-scans.tsx](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/components/scans/active-scans.tsx) | Frontend | Wire up action buttons |
| [frontend/src/lib/api-client.ts](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/lib/api-client.ts) | Frontend | Add scan control functions |
| `backend/supabase/` | Migration | Optional: Add status constraint |

---

> [!IMPORTANT]
> **Background Execution**: The crawler already runs in a "fire and forget" mode on the server. Scans will continue even if users close their browser. This is the existing architecture and requires no changes.
