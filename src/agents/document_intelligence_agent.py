from orchestration.state import AgentState, ExtractedInvoice, LineItem
from extraction.ocr import DocumentExtractor
from llm.client import LLMClient
import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DocumentIntelligenceAgent:
    def __init__(self):
        self.extractor = DocumentExtractor()
        self.llm = LLMClient()
    
    def process(self, state: AgentState) -> AgentState:
        """Extract structured data from invoice"""
        start_time = time.time()
        
        try:
            # Extract raw text
            raw_text, quality = self.extractor.extract_text(state["invoice_path"])
            
            if not raw_text or len(raw_text.strip()) < 50:
                state["errors"].append("Failed to extract text from document")
                state["extraction_confidence"] = 0.0
                state["document_quality"] = "poor"
                return state
            
            # Use LLM to structure the data
            prompt = self._build_extraction_prompt(raw_text)
            structured_data = self.llm.generate_structured(prompt, max_tokens=2000)
            
            if not structured_data:
                # Fallback to basic parsing
                structured_data = self._basic_parse(raw_text)
            
            # Build extracted invoice
            extracted_invoice = self._build_extracted_invoice(structured_data)
            
            # Calculate confidence
            confidence = self._calculate_confidence(extracted_invoice, quality)
            
            # Update state
            state["extracted_data"] = extracted_invoice
            state["extraction_confidence"] = confidence
            state["document_quality"] = quality
            state["extraction_reasoning"] = self._build_reasoning(extracted_invoice, quality, confidence)
            
            # Update trace
            duration = time.time() - start_time
            state["agent_execution_trace"]["document_intelligence_agent"] = {
                "duration_ms": int(duration * 1000),
                "confidence": confidence,
                "status": "success"
            }
            
        except Exception as e:
            state["errors"].append(f"Document Intelligence Agent error: {str(e)}")
            state["extraction_confidence"] = 0.0
            
        return state
    
    def _build_extraction_prompt(self, raw_text: str) -> str:
        return f"""Extract invoice data from the following text and return ONLY a JSON object.

Text:
{raw_text}

Return a JSON object with this structure:
{{
  "invoice_number": "extracted number",
  "invoice_date": "YYYY-MM-DD format",
  "supplier_name": "company name",
  "po_reference": "PO number or null",
  "currency": "GBP/USD/EUR",
  "line_items": [
    {{
      "item_code": "code",
      "description": "product description",
      "quantity": number,
      "unit": "kg/L/units",
      "unit_price": number,
      "line_total": number
    }}
  ],
  "subtotal": number,
  "vat_amount": number,
  "vat_rate": number (as decimal, e.g., 0.20 for 20%),
  "total": number
}}

Return ONLY the JSON, no other text."""
    
    def _basic_parse(self, text: str) -> dict:
        """Fallback basic parsing if LLM fails"""
        import re
        
        result = {
            "invoice_number": "",
            "invoice_date": "",
            "supplier_name": "",
            "po_reference": None,
            "currency": "GBP",
            "line_items": [],
            "subtotal": 0.0,
            "vat_amount": 0.0,
            "vat_rate": 0.20,
            "total": 0.0
        }
        
        # Extract invoice number
        inv_match = re.search(r'(?:Invoice|INV)[:\s#-]*([A-Z0-9-]+)', text, re.IGNORECASE)
        if inv_match:
            result["invoice_number"] = inv_match.group(1)
        
        # Extract PO reference
        po_match = re.search(r'PO[:\s#-]*([A-Z0-9-]+)', text, re.IGNORECASE)
        if po_match:
            result["po_reference"] = po_match.group(1)
        
        # Extract total
        total_match = re.search(r'Total[:\s]*[£$€]?([0-9,]+\.?[0-9]*)', text, re.IGNORECASE)
        if total_match:
            result["total"] = float(total_match.group(1).replace(',', ''))
        
        return result
    
    def _build_extracted_invoice(self, data: dict) -> ExtractedInvoice:
        """Build ExtractedInvoice from parsed data"""
        return {
            "invoice_number": data.get("invoice_number", ""),
            "invoice_date": data.get("invoice_date", ""),
            "supplier_name": data.get("supplier_name", ""),
            "supplier_address": data.get("supplier_address"),
            "supplier_vat": data.get("supplier_vat"),
            "po_reference": data.get("po_reference"),
            "payment_terms": data.get("payment_terms"),
            "currency": data.get("currency", "GBP"),
            "line_items": [
                {
                    "item_code": item.get("item_code", ""),
                    "description": item.get("description", ""),
                    "quantity": float(item.get("quantity", 0)),
                    "unit": item.get("unit", ""),
                    "unit_price": float(item.get("unit_price", 0)),
                    "line_total": float(item.get("line_total", 0)),
                    "extraction_confidence": 0.95
                }
                for item in data.get("line_items", [])
            ],
            "subtotal": float(data.get("subtotal", 0)),
            "vat_amount": float(data.get("vat_amount", 0)),
            "vat_rate": float(data.get("vat_rate", 0.20)),
            "total": float(data.get("total", 0))
        }
    
    def _calculate_confidence(self, invoice: ExtractedInvoice, quality: str) -> float:
        """Calculate extraction confidence score"""
        score = 0.5  # Base score
        
        # Quality bonus
        if quality == "excellent":
            score += 0.3
        elif quality == "acceptable":
            score += 0.2
        
        # Check critical fields
        if invoice["invoice_number"]:
            score += 0.05
        if invoice["invoice_date"]:
            score += 0.05
        if invoice["supplier_name"]:
            score += 0.05
        if invoice["total"] > 0:
            score += 0.05
        if len(invoice["line_items"]) > 0:
            score += 0.1
        
        return min(score, 0.99)
    
    def _build_reasoning(self, invoice: ExtractedInvoice, quality: str, confidence: float) -> str:
        """Build human-readable reasoning"""
        return f"Extracted invoice {invoice['invoice_number']} with {quality} quality. Found {len(invoice['line_items'])} line items. Extraction confidence: {confidence:.2%}."
