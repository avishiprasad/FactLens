# FactLens

### Fact Knowledge Layer for Financial Documents

FactLens is a document intelligence prototype that extracts meaningful numerical and semantic facts from PDFs, grounds every fact in source evidence, and identifies relationships between facts across documents.

The system is designed around one core principle:

> **Use the LLM for interpretation, and deterministic code for verification and reconciliation.**

---

## Demo

### Video Demo

**Demo video:** [Watch the FactLens Demo](https://drive.google.com/file/d/1XI2OmbcF4szuWFJ5eCVEGO9Y3BKSHw5v/view?usp=sharing)

The demo demonstrates:

1. Uploading a selected page from a Delhivery Annual Report.
2. Extracting structured financial facts with source evidence.
3. Uploading a second Delhivery document containing the same metric in a different unit.
4. Normalizing and corroborating the fact across documents.
5. Uploading RBI and IMF macroeconomic reports.
6. Identifying a likely disagreement between independent GDP growth forecasts.
7. Handling LLM extraction failures using a deterministic fallback.

---

## What is FactLens?

Financial and business documents often contain the same information expressed differently across annual reports, earnings presentations, regulatory documents, and research reports.

For example:

- One document may report revenue in **₹ million**.
- Another may report the same revenue in **₹ crore**.
- Two institutions may provide slightly different forecasts for the same economic metric.
- Two apparently different numbers may actually describe different scopes or time periods.

A simple document extraction system would treat these as independent numbers.

FactLens instead builds a **fact knowledge layer** where every extracted fact contains:

- What the fact represents
- Its value
- Its unit
- Its time period
- Its scope or context
- The source document
- The source page
- The exact evidence supporting it
- Its confidence
- Relationships with facts from other documents

The system then compares facts across documents and attempts to determine whether they:

- `CORROBORATES`
- `RECONCILED`
- `CONTEXTUAL_DIFFERENCE`
- `LIKELY_DISAGREEMENT`
- `CONTRADICTS`
- `UNRESOLVED`

---

# Key Capabilities

## 1. Structured Fact Extraction

PDF pages are parsed into text and passed to the LLM extraction layer.

The LLM identifies meaningful numerical and semantic facts and converts them into a structured representation.

A fact contains fields such as:

```text
Subject
Predicate
Value
Value Type
Unit
Period
Scope
Confidence
Evidence
```

For example:

```text
Subject: Delhivery
Predicate: Revenue from services
Value: 81415
Value Type: number
Unit: INR million
Period: FY24
Scope: Consolidated
Confidence: 1.0
Evidence: exact source text from the PDF
```

---

## 2. Evidence Grounding

Every extracted fact is linked to its source document and page.

The system also stores the evidence text returned by the extraction model.

Before a fact is marked as trusted, FactLens performs deterministic evidence verification against the original page text.

This reduces the risk of accepting an LLM-generated fact that cannot actually be found in the source document.

The principle is:

> **Extraction is generative. Grounding is deterministic.**

---

## 3. Unit Normalization

Financial documents frequently use different units for the same metric.

For example:

```text
₹81,415 million
```

and:

```text
₹8,142 crore
```

represent approximately the same underlying value.

FactLens normalizes supported units before comparison, including:

- INR
- INR thousand
- INR million
- INR billion
- INR crore
- INR lakh
- People
- Employees
- Agents
- Percent / %
- Per cent

This allows the reconciliation engine to compare facts based on their normalized numerical values rather than their original textual representation.

---

## 4. Semantic Fact Matching

Facts are not compared using numerical values alone.

The system first attempts to determine whether two facts describe the same underlying metric.

It normalizes:

- Subjects
- Predicates
- Financial periods
- Common wording variations
- Metric terminology

For example:

```text
"projected real GDP growth"
```

and:

```text
"real GDP growth under baseline scenario"
```

can be recognized as referring to the same underlying metric.

This helps prevent unrelated facts from being compared simply because they contain numbers with the same unit.

---

## 5. Relationship Detection

After candidate facts are identified, the reconciliation engine classifies their relationship.

### Corroboration

Two documents describe the same fact and their normalized values are effectively equal.

Example:

```text
Annual Report:
₹81,415 million

Earnings Presentation:
₹8,142 crore
```

After unit normalization, the values are approximately equal.

Result:

```text
CORROBORATES
```

---

### Contextual Reconciliation

Two numbers initially appear different, but one can be explained using the scope or components of the other.

Example:

```text
Team Size:
63,713

Partner Agents:
34,422

Total Workforce:
98,135
```

Since:

```text
63,713 + 34,422 = 98,135
```

the apparent difference can be explained by the definitions used in the source documents.

Result:

```text
RECONCILED
```

---

### Likely Disagreement

Two independent sources provide different values for the same metric and period.

Example:

```text
RBI:
6.5% GDP growth forecast

IMF:
6.6% GDP growth forecast
```

These values are close but not identical.

FactLens identifies the shared metric and period while preserving the fact that the sources provide different forecasts.

Result:

```text
LIKELY_DISAGREEMENT
```

rather than treating the values as identical.

---

### Contradiction

If two facts appear to describe the same metric, period, and scope but have materially different values without an obvious contextual explanation, the system can classify the relationship as:

```text
CONTRADICTS
```

---

### Unresolved

If the system does not have enough information to safely determine the relationship, it does not force a conclusion.

Instead, it returns:

```text
UNRESOLVED
```

This is intentional: ambiguous relationships should not be presented as certain.

---

# Architecture

```text
                         ┌─────────────────────┐
                         │       Next.js       │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                                    │ REST API
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │       Backend       │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐      ┌──────────────┐      ┌───────────────┐
       │ PDF Parser  │      │ LLM Extractor│      │ Reconciliation│
       │  PyMuPDF    │      │    Gemini    │      │    Engine     │
       └──────┬──────┘      └──────┬───────┘      └───────┬───────┘
              │                    │                      │
              └────────────────────┼──────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │       SQLite        │
                         │ Facts + Evidence    │
                         │   Relationships     │
                         └─────────────────────┘
```

---

# Processing Pipeline

```text
PDF Upload
    │
    ▼
Page Selection
    │
    ▼
PDF Text Extraction
    │
    ▼
Page-level Fact Extraction
    │
    ▼
Structured LLM Output
    │
    ▼
Evidence Verification
    │
    ▼
Unit + Period Normalization
    │
    ▼
Semantic Fact Matching
    │
    ▼
Relationship Classification
    │
    ▼
SQLite Knowledge Layer
    │
    ▼
FastAPI
    │
    ▼
Next.js UI
```

---

# Approach

FactLens separates the problem into two major responsibilities.

## LLM Responsibilities

The LLM is used where interpretation and semantic understanding are useful:

- Identifying meaningful facts
- Understanding natural language descriptions
- Extracting subjects and predicates
- Determining units
- Identifying periods
- Capturing scope and context
- Producing structured fact objects
- Handling different ways of expressing the same metric

The LLM is **not trusted blindly**.

---

## Deterministic Responsibilities

Traditional code handles operations where deterministic behavior is more reliable:

- PDF text extraction
- Evidence verification
- Unit normalization
- Numerical comparison
- Period normalization
- Semantic candidate filtering
- Duplicate detection
- Relationship persistence
- Database operations

This hybrid approach reduces hallucination risk while still allowing semantic interpretation.

---

# Fact Data Model

Each fact is represented approximately as:

```text
Fact
├── Subject
├── Predicate
├── Value
├── Value Type
├── Unit
├── Period
├── Scope
├── Confidence
├── Extraction Method
└── Evidence
    ├── Document
    ├── Page
    ├── Text
    └── Verification Status
```

Relationships are stored separately from facts.

This allows a relationship to connect multiple facts rather than limiting the system to simple pairwise comparisons.

For example:

```text
Team Size ───────┐
                 ├── RECONCILED ──> Workforce
Partner Agents ──┘
```

---

# Database Design

FactLens currently uses SQLite with SQLAlchemy.

The main entities are:

## Documents

Stores:

- Document ID
- Filename
- File hash
- Upload timestamp

## Pages

Stores:

- Document reference
- Page number
- Printed page information
- Extracted text

## Facts

Stores:

- Subject
- Predicate
- Value
- Value type
- Unit
- Period
- Scope
- Confidence
- Extraction method
- Evidence text
- Evidence verification status
- Source page

## Fact Relationships

Stores:

- Relationship type
- Confidence
- Explanation

## Relationship Facts

Association table connecting multiple facts to a relationship.

This supports relationships involving more than two facts.

---

# Relationship Types

| Relationship | Meaning |
|---|---|
| `CORROBORATES` | Same underlying fact with equivalent normalized values |
| `RECONCILED` | Difference explained through components or contextual information |
| `CONTEXTUAL_DIFFERENCE` | Values differ because their scope or context differs |
| `LIKELY_DISAGREEMENT` | Same metric and period but different source estimates |
| `CONTRADICTS` | Materially different values with matching context |
| `UNRESOLVED` | Insufficient evidence to determine the relationship |

---

# Handling LLM Failures

LLM APIs can fail because of:

- Rate limits
- Temporary service errors
- Network failures
- Invalid model responses
- Malformed structured output

FactLens therefore does not make the entire ingestion pipeline dependent on a successful LLM request.

The extraction layer includes a deterministic fallback extractor for common numerical patterns such as:

- Revenue
- Income
- Sales
- Growth percentages
- Margins
- Inflation
- Rates

When the LLM cannot be used, the fallback attempts to extract simpler facts from the source text.

The fact also records the extraction method:

```text
extraction_method = "llm"
```

or:

```text
extraction_method = "fallback"
```

This makes the origin of a fact visible to downstream consumers.

---

# Efficient PDF Processing

The system supports page-level processing.

During upload, the user can specify:

```text
6
```

or:

```text
6,9
```

to process only selected pages.

Leaving the page selector empty processes the complete document.

This is useful because financial reports can contain many pages while only a small subset may be relevant to a particular question.

Page-level processing also:

- Reduces unnecessary LLM calls
- Reduces token usage
- Makes demos faster
- Improves traceability
- Allows targeted inspection of large documents

---

# Incremental Document Processing

Documents are hashed using SHA-256.

The hash allows the backend to recognize previously processed documents and avoid unnecessarily ingesting the same file again.

The system also stores facts independently from documents, allowing newly uploaded documents to be compared against facts already present in the knowledge layer.

This provides a foundation for incremental ingestion without requiring the complete knowledge layer to be rebuilt every time a document is added.

---

# Demonstrated Scenarios

The demo dataset contains two document groups:

- Delhivery
- India Macroeconomy

## Delhivery

The Delhivery documents demonstrate cross-document corroboration and contextual reconciliation.

### 1. Cross-document Corroboration

The Annual Report reports FY24 revenue from services in INR million.

The Q4 FY24 Earnings Presentation reports the same metric in INR crore.

FactLens normalizes the units and identifies the values as representing the same underlying metric.

Example:

```text
Annual Report:
₹81,415 million

Earnings Presentation:
₹8,142 crore
```

Result:

```text
CORROBORATES
```

---

### 2. Contextual Reconciliation

The earnings presentation reports:

```text
Team Size = 63,713
Partner Agents = 34,422
```

while the Annual Report reports:

```text
Workforce = 98,135
```

The system can reconcile the apparent difference because:

```text
63,713 + 34,422 = 98,135
```

The difference therefore comes from the scope and definition of workforce rather than conflicting measurements.

Result:

```text
RECONCILED
```

---

## India Macroeconomy

The macroeconomic documents demonstrate independent forecasts.

### RBI

The RBI Annual Report provides a real GDP growth forecast of:

```text
6.5%
```

for 2025-26.

### IMF

The IMF Article IV report provides a real GDP growth forecast of:

```text
6.6%
```

for FY2025/26.

FactLens identifies these as the same broad metric and period but preserves the difference between the two independent forecasts.

Result:

```text
LIKELY_DISAGREEMENT
```

rather than treating the values as identical.

---

# Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- PyMuPDF
- Pydantic
- Google Gemini API

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Development

- Git
- GitHub
- VS Code
- REST API
- Swagger / OpenAPI

---

# API

FactLens exposes a REST API through FastAPI.

Main endpoints include:

```text
GET  /
GET  /health

GET  /documents/
POST /documents/upload

GET  /facts/

GET  /relationships/
```

Interactive API documentation is available through Swagger/OpenAPI:

```text
http://127.0.0.1:8000/docs
```

---

# Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/avishiprasad/FactLens.git
cd FactLens
```

---

## 2. Create a Python virtual environment

### Windows

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\activate
```

---

## 3. Install backend dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

## 4. Configure the Gemini API Key

Create:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_api_key_here
```

Never commit the API key or `.env` file to GitHub.

---

## 5. Initialize the database

From the `backend` directory:

```powershell
python -m app.db.reset_db
```

---

## 6. Start the backend

From the `backend` directory:

```powershell
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

## 7. Start the frontend

Open another terminal.

From the project root:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# Environment Variables

The backend expects:

```env
GEMINI_API_KEY=your_api_key_here
```

The API key must never be committed to source control.

The repository includes `.gitignore` rules for sensitive and generated files.

---

# Project Structure

```text
FactLens/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── documents.py
│   │   │       ├── facts.py
│   │   │       └── relationships.py
│   │   │
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── reset_db.py
│   │   │
│   │   ├── extraction/
│   │   │   ├── llm_extractor.py
│   │   │   └── fallback_extractor.py
│   │   │
│   │   ├── models/
│   │   │   └── fact.py
│   │   │
│   │   ├── parsing/
│   │   │   └── pdf_parser.py
│   │   │
│   │   ├── reconciliation/
│   │   │   ├── normalizer.py
│   │   │   ├── canonicalizer.py
│   │   │   ├── matcher.py
│   │   │   └── reconciliation_engine.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── fact_repository.py
│   │   │   └── relationship_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── document_service.py
│   │   │   ├── fact_service.py
│   │   │   └── reconciliation_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── public/
│   ├── package.json
│   └── ...
│
├── data/
│   └── docs/
│       ├── delhivery/
│       └── india-macroeconomy/
│
├── README.md
└── .gitignore
```

---

# Design Decisions & Tradeoffs

## Why FastAPI?

FastAPI provides:

- Simple REST API development
- Automatic OpenAPI documentation
- Pydantic-based validation
- Lightweight Python backend development
- Good integration with the Python AI ecosystem

---

## Why SQLite?

SQLite keeps the prototype easy to run locally without requiring an external database server.

It is sufficient for demonstrating:

- Document metadata
- Page-level source data
- Extracted facts
- Evidence
- Relationships

For production-scale workloads, a database such as PostgreSQL would be a better choice.

---

## Why PyMuPDF?

PyMuPDF provides fast page-level PDF text extraction and makes it straightforward to associate extracted text with exact page numbers.

This is particularly useful for evidence grounding.

---

## Why an LLM?

Pure regex-based extraction is too brittle for financial documents because the same metric can be expressed in many different ways.

The LLM provides semantic interpretation while deterministic code handles verification and numerical reasoning.

---

## Why Not Use an LLM for Everything?

Using an LLM for unit conversion, numerical comparison, or evidence verification introduces unnecessary uncertainty.

For example:

```text
₹81,415 million
```

can be deterministically normalized to approximately:

```text
₹8,141.5 crore
```

There is no reason to ask an LLM to perform this calculation.

Therefore:

> **LLM for interpretation. Code for verification and computation.**

---

# Limitations

FactLens is currently a prototype and has several limitations.

### PDF Extraction

The current parser primarily relies on text extraction from PDFs.

Scanned or image-only PDFs may require OCR.

### Table Understanding

Complex tables may not always preserve their original visual structure after text extraction.

### Semantic Matching

The current semantic matcher uses deterministic canonicalization and metric matching rather than a full embedding-based retrieval system.

### Relationship Reasoning

Some complex relationships require deeper contextual reasoning than the current rules can safely infer.

### LLM Availability

LLM-based extraction depends on API availability, rate limits, and model output quality.

The deterministic fallback reduces the impact of some failures but cannot fully replace semantic extraction.

### Scale

SQLite is appropriate for the prototype but would not be the ideal storage layer for a large production deployment with many concurrent users.

---

# Future Improvements

The architecture is intentionally designed so additional capabilities can be added without changing the core fact model.

## 1. OCR Support

Add OCR for scanned documents and image-only PDFs.

## 2. Structure-Aware PDF Parsing

Preserve:

- Tables
- Headings
- Sections
- Columns
- Bounding boxes

to improve evidence quality.

## 3. Embedding-Based Retrieval

Use embeddings to retrieve semantically similar facts from large collections of documents.

This would make cross-document matching more robust as the knowledge base grows.

## 4. Background Processing

Move large document processing to background workers so uploads do not block HTTP requests.

Potential architecture:

```text
Upload
   │
   ▼
Job Queue
   │
   ▼
Document Worker
   │
   ├── Parse
   ├── Extract
   ├── Verify
   └── Reconcile
```

## 5. Production Database

Move from SQLite to PostgreSQL for:

- Concurrent access
- Larger datasets
- Better indexing
- Production deployment

## 6. Better Evaluation

Create an evaluation dataset containing:

- Ground-truth facts
- Expected evidence spans
- Expected relationships
- Hard negative pairs
- Ambiguous cases

Then measure:

```text
Fact Extraction Precision
Fact Extraction Recall
Evidence Accuracy
Relationship Classification Accuracy
False Positive Rate
```

## 7. Human Review

Introduce a review workflow for low-confidence or unresolved relationships.

For example:

```text
High Confidence
      │
      ▼
Automatically Accepted

Medium Confidence
      │
      ▼
Human Review

Low Confidence
      │
      ▼
Flagged / Unresolved
```

---

# Security Considerations

- API keys are stored in environment variables.
- `.env` is excluded from Git.
- Uploaded documents should be treated as untrusted input.
- Production deployments should add authentication and authorization.
- File size and file type validation should be enforced.
- Sensitive financial documents should use encrypted storage in production.
- LLM providers should be evaluated for data retention and privacy requirements before processing confidential documents.

---

# AI Tools Used

The project uses AI selectively rather than delegating the entire pipeline to an LLM.

## Google Gemini

Used for:

- Semantic fact extraction
- Understanding financial language
- Producing structured fact representations
- Interpreting context such as periods and scopes

## Deterministic Python Logic

Used for:

- Evidence verification
- Unit normalization
- Numerical comparison
- Period normalization
- Fact matching
- Relationship classification
- Database persistence

This separation was intentional to make the system more reliable and explainable.

---

# Engineering Principles

## 1. Evidence First

A fact is only useful if the system can point back to where it came from.

## 2. Don't Hide Uncertainty

If the system cannot safely determine a relationship, it returns:

```text
UNRESOLVED
```

rather than inventing an explanation.

## 3. Deterministic Where Possible

Numerical operations and verification should not depend on probabilistic model output.

## 4. Schema Over Raw Text

Facts are represented as structured objects rather than simply storing extracted paragraphs.

## 5. Incremental Knowledge

New documents should be able to contribute new facts and relationships without rebuilding the entire knowledge layer.

---

# Example

Suppose two documents contain:

### Document A

```text
Revenue from services: ₹81,415 million
```

### Document B

```text
Revenue from services: ₹8,142 crore
```

FactLens converts them into structured facts:

```text
Fact A
Subject: Delhivery
Predicate: Revenue from services
Value: 81415
Unit: INR million
Period: FY24
```

```text
Fact B
Subject: Delhivery
Predicate: Revenue from services
Value: 8142
Unit: INR crore
Period: FY24
```

The reconciliation layer normalizes the units:

```text
81,415 million
        ≈
8,141.5 crore
```

The values fall within the configured comparison tolerance.

Therefore:

```text
CORROBORATES
```

The UI can then display:

```text
Revenue from services
        │
        ├── Annual Report
        │      Page 6
        │      ₹81,415 million
        │
        └── Earnings Presentation
               Page 9
               ₹8,142 crore

             CORROBORATES
```

This demonstrates the core purpose of the Fact Knowledge Layer:

> **Connecting facts, evidence, and meaning rather than merely extracting numbers.**

---

# Repository

[GitHub Repository](https://github.com/avishiprasad/FactLens)

---

