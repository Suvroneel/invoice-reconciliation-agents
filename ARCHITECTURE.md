# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                               │
│  Invoice Files (PDF, JPG, PNG) + PO Database (JSON)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH ORCHESTRATOR                         │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              SHARED STATE MANAGEMENT                     │   │
│  │  • Extraction data  • Matching results                   │   │
│  │  • Discrepancies    • Recommendations                    │   │
│  │  • Confidence scores • Error tracking                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │   AGENT WORKFLOW      │
        └───────────┬───────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│         AGENT 1: DOCUMENT INTELLIGENCE AGENT                     │
│                                                                   │
│  ┌─────────────┐      ┌──────────────┐      ┌───────────────┐  │
│  │   OCR/PDF   │ ───► │ LLM Extract  │ ───► │  Structure    │  │
│  │  Extraction │      │  (Llama 3.2) │      │  to JSON      │  │
│  └─────────────┘      └──────────────┘      └───────────────┘  │
│                                                                   │
│  Output: Extracted invoice data + confidence score               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT 2: MATCHING AGENT                             │
│                                                                   │
│  ┌──────────────────┐      ┌──────────────────┐                 │
│  │ Primary Match:   │      │  Fallback 1:     │                 │
│  │ Exact PO Number  │ ───► │  Supplier +      │                 │
│  │                  │      │  Products        │                 │
│  └──────────────────┘      └──────────────────┘                 │
│           │                          │                           │
│           │                 ┌────────▼───────────┐              │
│           └────────────────►│   Fallback 2:      │              │
│                             │   Fuzzy Product    │              │
│                             │   Matching         │              │
│                             └────────────────────┘              │
│                                                                   │
│  Output: Matched PO + confidence + method                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          AGENT 3: DISCREPANCY DETECTION AGENT                    │
│                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐    │
│  │ Price Check:  │  │ Quantity      │  │ Total Variance   │    │
│  │ 2% tolerance  │  │ Check         │  │ Check            │    │
│  │ 5% flag       │  │               │  │                  │    │
│  │ 15% escalate  │  │               │  │                  │    │
│  └───────────────┘  └───────────────┘  └──────────────────┘    │
│                                                                   │
│  Output: List of discrepancies with severity + confidence        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│        AGENT 4: RESOLUTION RECOMMENDATION AGENT                  │
│                                                                   │
│  Decision Tree:                                                  │
│                                                                   │
│  High Confidence + No Discrepancies                              │
│         ───► AUTO-APPROVE                                        │
│                                                                   │
│  Medium Confidence + Minor Issues                                │
│         ───► FLAG FOR REVIEW                                     │
│                                                                   │
│  Low Confidence OR High Severity Issues                          │
│         ───► ESCALATE TO HUMAN                                   │
│                                                                   │
│  Output: Recommended action + risk level + reasoning             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  invoice_X_output.json                                   │   │
│  │  {                                                        │   │
│  │    "invoice_id": "INV-2024-XXXX",                        │   │
│  │    "extracted_data": { ... },                            │   │
│  │    "matching_results": { ... },                          │   │
│  │    "discrepancies": [ ... ],                             │   │
│  │    "recommended_action": "auto_approve",                 │   │
│  │    "confidence": 0.98,                                    │   │
│  │    "agent_reasoning": "...",                             │   │
│  │    "execution_trace": { ... }                            │   │
│  │  }                                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Invoice 4 (Price Trap)

```
INPUT: Invoice_4_Price_Trap.pdf
│
├─► AGENT 1: Document Intelligence
│   ├─ OCR: "Ibuprofen BP £88.00/kg"
│   ├─ LLM Extract: Structured JSON
│   └─ Confidence: 0.95
│
├─► AGENT 2: Matching
│   ├─ Found PO: PO-2024-004
│   ├─ Method: Exact PO reference
│   └─ Confidence: 0.99
│
├─► AGENT 3: Discrepancy Detection
│   ├─ Price Check: £88 vs £80 = 10% variance
│   ├─ Severity: HIGH (>5% threshold)
│   └─ Flag: price_mismatch
│
├─► AGENT 4: Resolution
│   ├─ Analysis: High severity discrepancy
│   ├─ Decision: ESCALATE TO HUMAN
│   └─ Reasoning: "10% price increase exceeds auto-approve threshold"
│
OUTPUT: invoice_4_output.json
  ├─ recommended_action: "escalate_to_human"
  ├─ risk_level: "high"
  └─ discrepancies: [
      {
        "type": "price_mismatch",
        "severity": "high",
        "variance_percentage": 0.10,
        "invoice_value": 88.00,
        "po_value": 80.00
      }
    ]
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRAMEWORK LAYER                             │
│                                                                   │
│  LangGraph          Agent orchestration & state management       │
│  LangChain          Agent utilities                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         LLM LAYER                                │
│                                                                   │
│  Hugging Face       Llama 3.2 3B Instruct                        │
│  Inference API      Free tier (no local GPU needed)              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER                              │
│                                                                   │
│  Tesseract OCR      Text extraction from images                  │
│  PyPDF2             PDF text extraction                          │
│  OpenCV             Image preprocessing (deskew, threshold)      │
│  Pillow             Image handling                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     MATCHING LAYER                               │
│                                                                   │
│  FuzzyWuzzy         String similarity matching                   │
│  Levenshtein        Edit distance calculations                   │
│  Custom Logic       PO lookup, product matching                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      UTILITY LAYER                               │
│                                                                   │
│  Pydantic           Type checking & validation                   │
│  Python-dotenv      Environment variable management              │
│  JSON               Output formatting                            │
└─────────────────────────────────────────────────────────────────┘
```

## Confidence Scoring System

```
Document Quality Assessment:
  Excellent (PDF, clear text)      → Base: 0.85-0.95
  Acceptable (scan, minor issues)  → Base: 0.70-0.85
  Poor (low res, rotation)         → Base: 0.50-0.70

Field-Level Confidence:
  + Critical field present          → +0.05 each
  + All line items extracted        → +0.10
  + Totals match calculations       → +0.05

Matching Confidence:
  Exact PO number match             → 0.95-0.99
  Supplier + product match          → 0.70-0.85
  Product-only fuzzy match          → 0.50-0.70
  No match                          → 0.00

Final Recommendation Confidence:
  High extraction + exact match + no issues → 0.95-0.99
  Medium quality + minor issues             → 0.75-0.90
  Low quality OR major issues               → 0.50-0.75
```

## Error Handling Flow

```
┌─────────────────┐
│  Agent Error?   │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Log    │
    │  Error  │
    └────┬────┘
         │
    ┌────▼─────────────┐
    │ Set Confidence   │
    │ to 0.0          │
    └────┬─────────────┘
         │
    ┌────▼──────────────┐
    │ Add to errors[]   │
    └────┬──────────────┘
         │
    ┌────▼───────────────────┐
    │ Continue to next agent │
    │ (don't crash!)         │
    └────┬───────────────────┘
         │
    ┌────▼────────────────────┐
    │ Final recommendation:   │
    │ "escalate_to_human"     │
    └─────────────────────────┘
```
