from orchestration.state import AgentState, Discrepancy
from matching.po_lookup import PODatabase
from config import Config
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DiscrepancyDetectionAgent:
    def __init__(self):
        self.po_db = PODatabase()
    
    def process(self, state: AgentState) -> AgentState:
        """Detect discrepancies between invoice and PO"""
        start_time = time.time()
        
        try:
            extracted = state.get("extracted_data")
            matching = state.get("matching_results")
            
            if not extracted or not matching:
                state["errors"].append("Missing data for discrepancy detection")
                return state
            
            discrepancies = []
            
            # If no PO matched
            if not matching["matched_po"]:
                discrepancies.append({
                    "type": "missing_po_reference",
                    "severity": "high" if not extracted.get("po_reference") else "medium",
                    "field": "po_reference",
                    "details": "Invoice does not match any PO in database.",
                    "invoice_value": None,
                    "po_value": None,
                    "variance_percentage": None,
                    "confidence": 0.95
                })
            else:
                # Get PO data
                po = self.po_db.get_po_by_number(matching["matched_po"])
                if po:
                    # Check line item discrepancies
                    discrepancies.extend(self._check_line_items(extracted, po))
                    
                    # Check total variance
                    total_disc = self._check_total_variance(extracted, po)
                    if total_disc:
                        discrepancies.append(total_disc)
            
            # Calculate total variance
            total_variance_amount = 0.0
            total_variance_pct = 0.0
            
            if matching["matched_po"]:
                po = self.po_db.get_po_by_number(matching["matched_po"])
                if po:
                    po_total = po.get("total", 0)
                    inv_total = extracted.get("total", 0)
                    total_variance_amount = abs(inv_total - po_total)
                    if po_total > 0:
                        total_variance_pct = total_variance_amount / po_total
            
            state["discrepancies"] = discrepancies
            state["total_variance_amount"] = total_variance_amount
            state["total_variance_percentage"] = total_variance_pct
            state["discrepancy_reasoning"] = self._build_reasoning(discrepancies)
            
            # Update trace
            duration = time.time() - start_time
            state["agent_execution_trace"]["discrepancy_detection_agent"] = {
                "duration_ms": int(duration * 1000),
                "confidence": 0.95,
                "status": "success"
            }
            
        except Exception as e:
            state["errors"].append(f"Discrepancy Detection error: {str(e)}")
        
        return state
    
    def _check_line_items(self, invoice, po) -> list:
        """Check line item discrepancies"""
        discrepancies = []
        po_items = {item["item_id"]: item for item in po.get("line_items", [])}
        
        for idx, inv_item in enumerate(invoice["line_items"]):
            item_code = inv_item["item_code"]
            
            if item_code not in po_items:
                continue  # Skip unmatched items
            
            po_item = po_items[item_code]
            
            # Check price variance
            inv_price = inv_item["unit_price"]
            po_price = po_item["unit_price"]
            
            if po_price > 0:
                variance = abs(inv_price - po_price) / po_price
                
                if variance > Config.SIGNIFICANT_PRICE_VARIANCE:
                    discrepancies.append({
                        "type": "price_mismatch",
                        "severity": "high",
                        "field": f"line_items[{idx}].unit_price",
                        "details": f"Line item '{inv_item['description']}': Invoice price £{inv_price:.2f} vs PO price £{po_price:.2f} ({variance*100:.1f}% variance)",
                        "invoice_value": inv_price,
                        "po_value": po_price,
                        "variance_percentage": variance,
                        "confidence": 0.99
                    })
                elif variance > Config.PRICE_TOLERANCE:
                    discrepancies.append({
                        "type": "price_variance",
                        "severity": "medium",
                        "field": f"line_items[{idx}].unit_price",
                        "details": f"Line item '{inv_item['description']}': Price variance of {variance*100:.1f}% (within review threshold)",
                        "invoice_value": inv_price,
                        "po_value": po_price,
                        "variance_percentage": variance,
                        "confidence": 0.98
                    })
            
            # Check quantity variance
            if inv_item["quantity"] != po_item["quantity"]:
                discrepancies.append({
                    "type": "quantity_mismatch",
                    "severity": "medium",
                    "field": f"line_items[{idx}].quantity",
                    "details": f"Line item '{inv_item['description']}': Invoice quantity {inv_item['quantity']} vs PO quantity {po_item['quantity']}",
                    "invoice_value": inv_item["quantity"],
                    "po_value": po_item["quantity"],
                    "variance_percentage": None,
                    "confidence": 0.99
                })
        
        return discrepancies
    
    def _check_total_variance(self, invoice, po) -> dict:
        """Check total amount variance"""
        inv_total = invoice.get("total", 0)
        po_total = po.get("total", 0)
        
        variance_amount = abs(inv_total - po_total)
        variance_pct = variance_amount / po_total if po_total > 0 else 0
        
        # Check if within tolerance
        if variance_amount <= Config.TOTAL_VARIANCE_AMOUNT:
            return None
        
        if variance_pct <= Config.TOTAL_VARIANCE_PERCENT:
            return None
        
        # Significant variance
        severity = "high" if variance_pct > 0.10 else "medium"
        
        return {
            "type": "total_variance",
            "severity": severity,
            "field": "total",
            "details": f"Invoice total £{inv_total:.2f} vs PO total £{po_total:.2f} (£{variance_amount:.2f} difference, {variance_pct*100:.1f}% variance)",
            "invoice_value": inv_total,
            "po_value": po_total,
            "variance_percentage": variance_pct,
            "confidence": 0.99
        }
    
    def _build_reasoning(self, discrepancies: list) -> str:
        """Build reasoning text"""
        if not discrepancies:
            return "No discrepancies detected. All line items and totals match PO within acceptable tolerance."
        
        high = sum(1 for d in discrepancies if d["severity"] == "high")
        medium = sum(1 for d in discrepancies if d["severity"] == "medium")
        
        return f"Found {len(discrepancies)} discrepancies: {high} high severity, {medium} medium severity. Review required."
