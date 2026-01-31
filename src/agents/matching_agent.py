from orchestration.state import AgentState, MatchingResult
from matching.po_lookup import PODatabase
from matching.fuzzy_matching import FuzzyMatcher
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MatchingAgent:
    def __init__(self):
        self.po_db = PODatabase()
        self.fuzzy = FuzzyMatcher()
    
    def process(self, state: AgentState) -> AgentState:
        """Match invoice to PO database"""
        start_time = time.time()
        
        try:
            extracted = state.get("extracted_data")
            if not extracted:
                state["errors"].append("No extracted data to match")
                return state
            
            # Try primary matching (exact PO reference)
            matched_po = None
            match_method = "none"
            confidence = 0.0
            
            po_ref = extracted.get("po_reference")
            if po_ref:
                matched_po = self.po_db.get_po_by_number(po_ref)
                if matched_po:
                    match_method = "exact_po_reference"
                    confidence = 0.99
            
            # Fallback: match by supplier
            if not matched_po:
                supplier_matches = self.po_db.search_by_supplier(extracted["supplier_name"])
                if supplier_matches:
                    matched_po = supplier_matches[0]
                    match_method = "supplier_match"
                    confidence = 0.75
            
            # Fallback: match by products
            if not matched_po and extracted["line_items"]:
                product_codes = [item["item_code"] for item in extracted["line_items"] if item["item_code"]]
                product_matches = self.po_db.search_by_products(product_codes)
                if product_matches:
                    best = product_matches[0]
                    matched_po = best["po"]
                    match_method = "product_fuzzy_match"
                    confidence = best["match_rate"] * 0.8
            
            # Build matching results
            if matched_po:
                matching_result = self._build_matching_result(
                    extracted, matched_po, match_method, confidence
                )
            else:
                matching_result = self._build_no_match_result()
            
            state["matching_results"] = matching_result
            state["matching_reasoning"] = self._build_reasoning(matching_result, extracted)
            
            # Update trace
            duration = time.time() - start_time
            state["agent_execution_trace"]["matching_agent"] = {
                "duration_ms": int(duration * 1000),
                "confidence": confidence,
                "status": "success"
            }
            
        except Exception as e:
            state["errors"].append(f"Matching Agent error: {str(e)}")
        
        return state
    
    def _build_matching_result(self, invoice, po, method, confidence) -> MatchingResult:
        """Build matching result"""
        # Count matched line items
        matched_items = 0
        total_items = len(invoice["line_items"])
        
        if po:
            po_items = po.get("line_items", [])
            invoice_codes = [item["item_code"] for item in invoice["line_items"]]
            po_codes = [item["item_id"] for item in po_items]
            
            for code in invoice_codes:
                if code in po_codes:
                    matched_items += 1
        
        match_rate = matched_items / total_items if total_items > 0 else 0.0
        
        # Check supplier match
        supplier_match = False
        if po:
            inv_supplier = invoice["supplier_name"].lower().replace("ltd", "").replace("limited", "").strip()
            po_supplier = po.get("supplier", "").lower().replace("ltd", "").replace("limited", "").strip()
            supplier_match = inv_supplier in po_supplier or po_supplier in inv_supplier
        
        return {
            "po_match_confidence": confidence,
            "matched_po": po.get("po_number") if po else None,
            "match_method": method,
            "supplier_match": supplier_match,
            "line_items_matched": matched_items,
            "line_items_total": total_items,
            "match_rate": match_rate,
            "alternative_matches": []
        }
    
    def _build_no_match_result(self) -> MatchingResult:
        """Build result when no PO found"""
        return {
            "po_match_confidence": 0.0,
            "matched_po": None,
            "match_method": "no_match",
            "supplier_match": False,
            "line_items_matched": 0,
            "line_items_total": 0,
            "match_rate": 0.0,
            "alternative_matches": []
        }
    
    def _build_reasoning(self, result: MatchingResult, invoice) -> str:
        """Build reasoning text"""
        if result["matched_po"]:
            return f"Matched to PO {result['matched_po']} using {result['match_method']} with {result['po_match_confidence']:.0%} confidence. {result['line_items_matched']}/{result['line_items_total']} line items matched."
        else:
            return f"No PO match found for invoice {invoice.get('invoice_number', 'UNKNOWN')}. No matching supplier or products in database."
