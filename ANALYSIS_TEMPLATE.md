# Written Analysis Template (500 words max)

## 1. Where does OCR/extraction fail? How do your agents compensate?

**OCR Failure Scenarios:**
- Low-resolution scans (<150 DPI)
- Heavily rotated images (>10 degrees)
- Handwritten notes or signatures
- Poor lighting/shadows in photos
- Mixed text and image invoices

**Agent Compensation Strategies:**

Our Document Intelligence Agent implements several fallback mechanisms:

1. **Image Preprocessing**: Before OCR, we apply deskewing (rotation correction), grayscale conversion, and adaptive thresholding to improve text recognition quality.

2. **Confidence Scoring**: Every extracted field has a confidence score. When OCR confidence is low (<70%), we:
   - Flag the document for human review
   - Use LLM-based extraction as secondary validation
   - Apply fuzzy matching more liberally in subsequent agents

3. **LLM Structured Extraction**: After OCR, we pass raw text through Llama 3.2 to structure the data. The LLM can infer missing fields and correct OCR errors by understanding context.

4. **Multi-level Fallbacks**: 
   - Primary: Clean OCR extraction
   - Secondary: LLM-assisted extraction
   - Tertiary: Basic regex parsing for critical fields (invoice number, total)

**Current Limitations:**
- Cannot handle purely handwritten invoices
- Struggles with invoices containing logos/graphics that obscure text
- Multi-page invoices may have ordering issues

---

## 2. How would you improve accuracy from 70% to 95%?

**Technical Improvements:**

1. **Better OCR Engine** (15% improvement)
   - Replace Tesseract with EasyOCR or PaddleOCR for better multilingual support
   - Implement ensemble OCR (run multiple engines, use voting)
   - Fine-tune OCR models on pharma/chemical invoice datasets

2. **Specialized LLM** (5% improvement)
   - Fine-tune Llama on invoice extraction tasks with thousands of examples
   - Use larger model (7B or 13B parameters) for better reasoning
   - Implement prompt engineering with few-shot examples

3. **Template Learning** (3% improvement)
   - Build template detection system to identify invoice formats
   - Create format-specific extraction rules for common suppliers
   - Cache successful extractions as templates for future invoices

4. **Validation Layer** (2% improvement)
   - Cross-validate extracted totals against line item sums
   - Check VAT calculations (20% rule)
   - Verify date formats and reasonableness

**Process Improvements:**

5. **Human-in-the-Loop Training** (5% improvement)
   - Collect human corrections from review cases
   - Retrain extraction models on corrected examples
   - Build supplier-specific knowledge base

6. **Quality Gates** (5% improvement)
   - Reject extremely low-quality inputs immediately
   - Request re-scans for poor quality documents
   - Implement image quality scoring before processing

**Expected Impact:**
- OCR improvements: 70% → 85%
- LLM + validation: 85% → 92%
- Process + training: 92% → 95%

---

## 3. How would you validate this system at 10,000 invoices/day scale?

**Architecture Changes:**

1. **Distributed Processing**
   - Deploy on Kubernetes cluster with auto-scaling
   - Use message queue (RabbitMQ/Kafka) for invoice ingestion
   - Parallel processing across multiple workers
   - Estimated capacity: 50-100 invoices/minute (7,200-14,400/day per cluster)

2. **Performance Optimization**
   - Cache PO lookups in Redis
   - Batch similar invoices for processing
   - Use GPU-accelerated OCR for scanned images
   - Target: <10 seconds per invoice (vs current ~12-15s)

**Validation Strategy:**

3. **Automated Testing**
   - Golden dataset: 1,000 manually verified invoices covering all edge cases
   - Continuous integration: Run full test suite on every code change
   - Regression testing: Track accuracy metrics over time
   - A/B testing: Compare new model versions against production

4. **Production Monitoring**
   - Real-time dashboards: Track processing rates, error rates, confidence distributions
   - Alert on: Processing time >30s, confidence <60%, error rate >5%
   - Sample validation: Human review 1% of auto-approved invoices daily
   - Feedback loop: Flag cases where human overrides agent decision

5. **Quality Metrics**
   - Precision: % of auto-approved invoices that are actually correct
   - Recall: % of correct invoices that are auto-approved
   - F1 Score: Harmonic mean of precision/recall
   - Target SLA: 95% precision, 90% recall

6. **Phased Rollout**
   - Week 1-2: Shadow mode (process but don't act, compare to human)
   - Week 3-4: Low-risk only (auto-approve only exact PO matches)
   - Week 5+: Full deployment with human oversight
   - Monthly audits of random samples

**Cost Estimation:**
- 10,000 invoices/day = ~2-3 hours GPU processing time
- LLM API costs: ~$50-100/day (using Llama via HF Inference)
- Human review (5% flagged): ~500 invoices/day = 2 FTE reviewers

**Risk Mitigation:**
- Financial caps: Never auto-approve >£50k invoices
- Supplier whitelist: Higher thresholds for trusted suppliers
- Manual review queue with prioritization by risk level
