# AuthEvidence AI

### Evidence-Grounded Prior Authorization Intelligence

AuthEvidence AI is a healthcare decision-support application for reviewing prior authorization requests against clinical evidence and procedure-specific coverage criteria.

The platform accepts structured patient information or FHIR R4-style clinical resources, extracts relevant evidence, selects an applicable authorization policy, maps patient evidence to individual policy criteria, identifies documentation gaps, and generates readiness and confidence scores for human review.

> **Important:** AuthEvidence AI is a decision-support prototype. It does not make final clinical or coverage decisions. Final authorization decisions require qualified human review.

---

## Business Problem

Prior authorization workflows often require reviewers to manually compare clinical documentation against coverage requirements.

This creates several challenges:

- Relevant clinical evidence may be spread across multiple records.
- Required documentation may be incomplete.
- Reviewers must manually verify whether each policy criterion is satisfied.
- Missing evidence can cause avoidable delays and repeated documentation requests.
- Coverage reviews must remain explainable and traceable.

AuthEvidence AI addresses this by converting clinical information into a structured, evidence-grounded review.

---

## What AuthEvidence AI Does

Given patient clinical information and a requested procedure, the system:

1. Extracts structured clinical evidence.
2. Identifies the applicable prior-authorization policy.
3. Evaluates each policy criterion against available evidence.
4. Classifies criteria as:
   - `MET`
   - `NOT_MET`
   - `INSUFFICIENT`
5. Assigns criterion-level confidence scores.
6. Detects missing supporting documentation.
7. Generates actionable documentation requests.
8. Calculates authorization readiness.
9. Produces an overall evidence-confidence score.
10. Returns a human-readable review summary.

---

# Example Workflow

```text
Patient / FHIR Clinical Data
            |
            v
Clinical Evidence Extraction
            |
            v
Procedure-Based Policy Selection
            |
            v
Policy Criteria
            |
            v
Evidence-to-Criteria Matching
            |
            +------> MET
            +------> NOT_MET
            +------> INSUFFICIENT
            |
            v
Criterion Confidence Scoring
            |
            v
Missing Evidence Detection
            |
            v
Authorization Readiness
            |
            v
Human Review Dashboard
```

---

# Key Features

## Clinical Evidence Extraction

AuthEvidence AI converts patient information into normalized evidence categories including:

- Diagnoses
- Medications
- Procedures
- Observations
- Encounters
- Supporting evidence summaries

Example:

```json
{
  "diagnoses": [
    {
      "code": "M54.16",
      "description": "Lumbar radiculopathy"
    }
  ],
  "medications": [
    {
      "name": "Ibuprofen",
      "duration_weeks": 8
    }
  ],
  "procedures": [
    {
      "code": "97110",
      "description": "Physical therapy"
    }
  ]
}
```

---

## FHIR R4-Style Input Support

The backend includes a FHIR parsing layer capable of translating commonly used healthcare resources into the internal AuthEvidence evidence model.

Supported resource types currently include:

- `Patient`
- `Condition`
- `MedicationRequest`
- `Procedure`
- `Observation`
- `Encounter`

FHIR resources are normalized before entering the evidence-matching pipeline.

---

## Automatic Policy Selection

AuthEvidence AI can select a policy using the requested procedure code.

Current demonstration policies include:

| Procedure | CPT | Policy |
|---|---:|---|
| Lumbar Spine MRI Without Contrast | `72148` | Lumbar Spine MRI Prior Authorization Policy |
| Knee MRI / Lower Extremity Joint Without Contrast | `73721` | Knee MRI Prior Authorization Policy |

The policy-selection layer is designed so additional procedure policies can be added without rewriting the main review workflow.

---

## Evidence-to-Policy Matching

Each authorization policy contains independently evaluated coverage criteria.

Example:

```text
C1  Persistent symptoms
C2  Conservative medication therapy
C3  Physical therapy / conservative treatment
C4  Relevant clinical diagnosis
```

Clinical evidence is normalized and compared against each policy criterion.

The resulting assessment contains:

```json
{
  "criterion": "Physical therapy or another conservative treatment has been attempted",
  "status": "MET",
  "confidence": 98,
  "evidence": [
    "procedure physical therapy"
  ],
  "source": "SAMPLE-LUMBAR-MRI-001"
}
```

---

## Missing-Evidence Detection

When evidence does not sufficiently support a policy criterion, AuthEvidence AI identifies the documentation gap.

Example:

```json
{
  "criterion": "Physical therapy or another conservative treatment has been attempted",
  "status": "INSUFFICIENT",
  "request": "Please provide documentation of physical therapy or another conservative treatment attempt."
}
```

This allows the system to explain **why a request is incomplete**, instead of only returning a score.

---

## Authorization Readiness Scoring

The system calculates how many policy criteria are satisfied.

Example:

```json
{
  "readiness_score": 75,
  "criteria_met": 3,
  "criteria_total": 4,
  "status": "NEARLY_READY"
}
```

Current readiness states include:

```text
READY_FOR_REVIEW
NEARLY_READY
ADDITIONAL_DOCUMENTATION_REQUIRED
NOT_READY
INSUFFICIENT_DATA
```

---

## Evidence Confidence

Each policy criterion receives a confidence score based on the available supporting evidence.

Criterion-level confidence scores are aggregated into an overall evidence-confidence score.

Example:

```json
{
  "evidence_confidence": 79.75,
  "confidence_level": "MEDIUM"
}
```

Confidence levels:

```text
HIGH
MEDIUM
LOW
```

---

# Demonstrated Review Scenarios

## Scenario 1 — Complete Lumbar MRI Evidence

Clinical evidence includes:

- Lumbar radiculopathy
- Eight weeks of conservative medication therapy
- Physical therapy
- Persistent lower-back pain

Result:

```text
Criteria Met:        4 / 4
Readiness:           100%
Status:              READY_FOR_REVIEW
Missing Evidence:    None
```

---

## Scenario 2 — Missing Conservative Treatment Evidence

The same lumbar MRI request is submitted without physical-therapy documentation.

Result:

```text
Criteria Met:        3 / 4
Readiness:           75%
Status:              NEARLY_READY
Missing Evidence:    Physical therapy documentation
```

The system generates an actionable documentation request rather than silently failing the criterion.

---

## Scenario 3 — Knee MRI

Clinical evidence includes:

- Right-knee osteoarthritis
- Naproxen therapy
- Physical therapy
- Persistent right-knee pain

Requested procedure:

```text
73721
```

AuthEvidence AI automatically selects:

```text
SAMPLE-KNEE-MRI-001
Knee MRI Prior Authorization Policy
```

and evaluates the knee-specific criteria independently.

---

# Architecture

```text
                         AuthEvidence AI

                    ┌──────────────────────┐
                    │   Next.js Frontend   │
                    │   Review Dashboard   │
                    └──────────┬───────────┘
                               │
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │ /api/authevidence/   │
                    │       review         │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │ FHIR R4 Parser   │        │ Standard JSON    │
       └────────┬─────────┘        └────────┬─────────┘
                │                           │
                └────────────┬──────────────┘
                             ▼
                 ┌────────────────────────┐
                 │ Clinical Evidence      │
                 │ Extraction             │
                 └────────────┬───────────┘
                              ▼
                 ┌────────────────────────┐
                 │ Policy Selection       │
                 │ Procedure Code → Policy│
                 └────────────┬───────────┘
                              ▼
                 ┌────────────────────────┐
                 │ Evidence / Criterion   │
                 │ Matching               │
                 └────────────┬───────────┘
                              ▼
                 ┌────────────────────────┐
                 │ Confidence + Readiness │
                 │ Missing Evidence       │
                 └────────────┬───────────┘
                              ▼
                 ┌────────────────────────┐
                 │ Structured Review      │
                 │ + Human Summary        │
                 └────────────────────────┘
```

---

# Optional Coverage Enrichment

The repository also retains the upstream hosted Coverage Assessment Agent infrastructure.

AuthEvidence exposes an optional:

```json
"use_coverage_agent": true
```

path that can enrich a local review with coverage-agent results when the configured hosted environment is available.

The enrichment interface can return:

- Provider verification
- Coverage policies
- Policy references
- Coverage limitations
- Documentation gaps
- Tool execution results

If the external coverage service is unavailable, the local AuthEvidence workflow continues without crashing.

---

# API

## Endpoint

```http
POST /api/authevidence/review
```

---

## Example Request

```json
{
  "patient_data": {
    "patient_id": "PAT-1002",
    "age": 61,
    "gender": "male",
    "conditions": [
      {
        "code": "M54.16",
        "description": "Lumbar radiculopathy",
        "status": "active"
      }
    ],
    "medications": [
      {
        "name": "Ibuprofen",
        "status": "completed",
        "duration_weeks": 8
      }
    ],
    "procedures": [
      {
        "code": "97110",
        "description": "Physical therapy"
      }
    ],
    "observations": [],
    "encounters": [
      {
        "type": "outpatient",
        "reason": "Persistent lower-back pain"
      }
    ]
  },
  "procedure_code": "72148",
  "provider_npi": null,
  "use_coverage_agent": false
}
```

---

## Example Response

```json
{
  "patient_id": "PAT-1002",

  "policy": {
    "policy_id": "SAMPLE-LUMBAR-MRI-001",
    "title": "Lumbar Spine MRI Prior Authorization Policy",
    "procedure_code": "72148"
  },

  "authorization_readiness": {
    "readiness_score": 100,
    "criteria_met": 4,
    "criteria_total": 4,
    "status": "READY_FOR_REVIEW"
  }
}
```

---

# Frontend

The AuthEvidence UI is built with Next.js and provides:

- Prior authorization submission form
- Clinical evidence entry
- Procedure selection
- Optional CMS/NPI coverage enrichment
- Authorization readiness display
- Evidence confidence display
- Policy information
- Criterion-level evidence mapping
- Missing-documentation alerts
- Clinical evidence summary
- Human-readable review summary

---

# Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- Pytest
- REST APIs

### Healthcare

- FHIR R4-style resource parsing
- CPT procedure codes
- ICD-10 clinical context
- Prior authorization criteria
- Evidence-grounded review

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Radix UI / shadcn-style components
- Lucide React

### Infrastructure retained from upstream accelerator

- Docker
- Azure deployment configuration
- Microsoft Foundry hosted-agent structure
- Microsoft Agent Framework integration
- Application Insights / OpenTelemetry support
- MCP coverage/NPI integration hooks

---

# Project Structure

```text
authevidence-ai/
│
├── agents/
│   ├── clinical/
│   ├── compliance/
│   ├── coverage/
│   └── synthesis/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── evidence/
│   │   │   ├── extractor.py
│   │   │   ├── fhir_parser.py
│   │   │   ├── matcher.py
│   │   │   └── readiness.py
│   │   │
│   │   ├── retrieval/
│   │   │   └── policy_loader.py
│   │   │
│   │   ├── routers/
│   │   │   └── authevidence.py
│   │   │
│   │   └── services/
│   │       ├── authevidence_review.py
│   │       └── coverage_enrichment.py
│   │
│   └── tests/
│       ├── test_authevidence_review.py
│       ├── test_evidence_extractor.py
│       ├── test_fhir_parser.py
│       ├── test_policy_loader.py
│       ├── test_policy_matching.py
│       └── test_readiness.py
│
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
│
├── policies/
│   └── sample/
│       ├── lumbar_mri_policy.json
│       └── knee_mri_policy.json
│
├── docs/
├── infra/
├── scripts/
│
└── README.md
```

---

# Running Locally

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd authevidence-ai
```

---

## 2. Start the backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 3. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# Running Tests

From the backend directory:

```bash
python -m pytest tests -v
```

Individual custom tests include:

```bash
python -m pytest tests/test_evidence_extractor.py -v
python -m pytest tests/test_policy_loader.py -v
python -m pytest tests/test_policy_matching.py -v
python -m pytest tests/test_readiness.py -v
python -m pytest tests/test_fhir_parser.py -v
python -m pytest tests/test_authevidence_review.py -v
```

Frontend production build:

```bash
npm run build
```

---
# Safety and Limitations

AuthEvidence AI is an educational and portfolio-oriented healthcare decision-support prototype.

It is **not** intended to:

- Replace clinical judgment.
- Make autonomous utilization-management decisions.
- Determine medical necessity without human review.
- Serve as authoritative payer policy guidance.
- Replace CMS or payer coverage documentation.
- Process real protected health information without an appropriate compliant environment.

The sample authorization policies included in this project are demonstration policies and should not be interpreted as official Medicare or commercial-payer coverage rules.

---

## Attribution

AuthEvidence AI builds on the Microsoft Prior Authorization Multi-Agent Solution Accelerator and adds custom FHIR evidence processing, policy matching, readiness/confidence scoring, documentation-gap detection, and a redesigned review workflow.

See `LICENSE` for licensing information.

---

# Responsible Use

This application provides AI-assisted and rule-assisted decision support only.

All prior-authorization outputs should be independently reviewed by qualified healthcare, clinical, compliance, or utilization-management professionals before being used operationally.

No output from this project should be interpreted as medical, legal, insurance, or financial advice.

---

## AuthEvidence AI

**FHIR-aware clinical evidence extraction.  
Policy-grounded authorization review.  
Explainable readiness and documentation-gap detection.**
