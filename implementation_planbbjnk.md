# Explorable Services Section

Make the "Learn More" buttons on the Services page open detailed modals with comprehensive service information.

## Architecture Overview

```mermaid
flowchart TB
    subgraph ServicesPage["Services Page"]
        S1["MDR Card"]
        S2["Security Audits Card"]
        S3["Incident Response Card"]
        S4["Pen Testing Card"]
        S5["Cloud Security Card"]
        S6["vCISO Card"]
    end
    
    subgraph Modal["ServiceModal"]
        Title["Service Title + Icon"]
        Desc["Detailed Description"]
        Features["Key Features List"]
        Benefits["Benefits"]
        CTA["Contact/Get Started"]
    end
    
    S1 & S2 & S3 & S4 & S5 & S6 -->|"Learn More"| Modal
```

---

## Proposed Changes

### Data Layer

#### [NEW] [servicesData.ts](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/data/servicesData.ts)

| Service ID | Title |
|------------|-------|
| mdr | Managed Detection & Response |
| audits | Security Audits & Compliance |
| incident | Incident Response |
| pentest | Penetration Testing |
| cloud | Cloud Security Architecture |
| vciso | Virtual CISO (vCISO) |

Each service includes: [id](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/components/landing/VideoModal.tsx#11-92), `title`, `icon`, `shortDescription`, `fullDescription`, `features[]`, `benefits[]`, `ctaText`

---

### Component

#### [NEW] [ServiceModal.tsx](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/components/services/ServiceModal.tsx)

Modal with:
- Service icon and title
- Full description
- Key features checklist
- Benefits section
- CTA button → Contact page or pricing

---

### Services Page

#### [MODIFY] [page.tsx](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/app/(marketing)/services/page.tsx)

- Add `'use client'` directive
- Add `selectedService` state
- Convert `<a href="#">` to `<button onClick={...}>`
- Import and render `ServiceModal`

---

## User Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as Service Card
    participant M as ServiceModal
    
    U->>C: Clicks "Learn More"
    C->>M: Opens modal with service details
    M->>U: Shows features, benefits, CTA
    
    alt User wants to proceed
        U->>M: Clicks "Get Started"
        M-->>U: Navigates to /pricing or /contact
    else User closes
        U->>M: Clicks X or backdrop
        M->>C: Modal closes
    end
```

---

## Verification Plan

- Click each of the 6 "Learn More" buttons → modal opens with correct content
- Close modal via X button, backdrop, or ESC key
- Verify CTA button navigates correctly
