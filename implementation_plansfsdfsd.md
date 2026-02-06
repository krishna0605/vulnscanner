# Security Knowledge Base Exploration

Make the "Core Principles" and "Essential Precautions" section fully interactive, allowing users to click on each item to learn more.

## Architecture Overview

```mermaid
flowchart TB
    subgraph KnowledgeBase["Security Knowledge Base Section"]
        CP["Core Principles Card"]
        EP["Essential Precautions Card"]
    end
    
    subgraph CorePrinciples["Core Principles (4 items)"]
        P1["Principle of Least Privilege"]
        P2["Secure Coding Practices"]
        P3["Continuous Patch Management"]
        P4["Multi-Factor Authentication"]
    end
    
    subgraph Precautions["Essential Precautions (4 items)"]
        E1["Phishing & Social Engineering"]
        E2["Secrets Management"]
        E3["Reliable Data Backups"]
        E4["Comprehensive Logging"]
    end
    
    subgraph Modal["KnowledgeItemModal"]
        Title["Title + Icon"]
        Desc["Description"]
        Tips["Key Tips"]
        Link["Learn More Link"]
    end
    
    CP --> P1 & P2 & P3 & P4
    EP --> E1 & E2 & E3 & E4
    
    P1 & P2 & P3 & P4 --> Modal
    E1 & E2 & E3 & E4 --> Modal
```

---

## Proposed Changes

### Data Layer

#### [MODIFY] [securityConcepts.ts](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/data/securityConcepts.ts)

Add `knowledgeItems` array with 8 items:

| ID | Category | Title |
|----|----------|-------|
| least-privilege | principle | Principle of Least Privilege |
| secure-coding | principle | Secure Coding Practices |
| patch-management | principle | Continuous Patch Management |
| mfa | principle | Multi-Factor Authentication |
| phishing | precaution | Phishing & Social Engineering |
| secrets | precaution | Secrets Management & Hygiene |
| backups | precaution | Reliable Data Backups |
| logging | precaution | Comprehensive Logging |

---

### Component

#### [NEW] [KnowledgeItemModal.tsx](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/components/landing/KnowledgeItemModal.tsx)

Reuse similar structure to [ConceptModal](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/components/landing/ConceptModal.tsx#13-108):
- Title with icon
- Description paragraph
- 3-4 actionable tips
- "Learn More" button → `/learn#[item-id]`

---

### Landing Page

#### [MODIFY] [page.tsx](file:///c:/Users/Admin/Desktop/vulscanner/frontend/src/app/(marketing)/page.tsx)

- Add `selectedKnowledgeItem` state
- Convert `<li>` elements to clickable `<button>` elements
- Add hover effects for visual feedback
- Wire up modal open/close

---

## User Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant KB as Knowledge Base Section
    participant M as KnowledgeItemModal
    
    U->>KB: Views Security Knowledge Base
    U->>KB: Clicks "Principle of Least Privilege"
    KB->>M: Opens modal with item details
    M->>U: Shows description + tips
    
    alt User wants more
        U->>M: Clicks "Learn More"
        M-->>U: Navigates to /learn#least-privilege
    else User closes
        U->>M: Clicks X or backdrop
        M->>KB: Modal closes
    end
```

---

## Verification Plan

- Click each of the 8 items → modal opens with correct content
- Close modal via X button, backdrop, or ESC key
- Verify responsive layout on mobile
