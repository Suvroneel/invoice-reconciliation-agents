import json
from typing import List, Dict, Optional
from config import Config
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PODatabase:
    def __init__(self):
        self.pos = self._load_pos()
    
    def _load_pos(self) -> List[Dict]:
        """Load purchase orders from JSON"""
        try:
            with open(Config.PO_FILE, 'r') as f:
                data = json.load(f)
                return data.get("purchase_orders", [])
        except Exception as e:
            print(f"Error loading POs: {e}")
            return []
    
    def get_po_by_number(self, po_number: str) -> Optional[Dict]:
        """Get PO by exact number match"""
        for po in self.pos:
            if po.get("po_number", "").upper() == po_number.upper():
                return po
        return None
    
    def search_by_supplier(self, supplier_name: str) -> List[Dict]:
        """Search POs by supplier name (fuzzy)"""
        results = []
        supplier_lower = supplier_name.lower()
        
        for po in self.pos:
            po_supplier = po.get("supplier", "").lower()
            if supplier_lower in po_supplier or po_supplier in supplier_lower:
                results.append(po)
        
        return results
    
    def search_by_products(self, product_codes: List[str]) -> List[Dict]:
        """Search POs by product codes"""
        results = []
        product_codes_upper = [p.upper() for p in product_codes]
        
        for po in self.pos:
            po_items = po.get("line_items", [])
            po_codes = [item.get("item_id", "").upper() for item in po_items]
            
            # Check overlap
            matching = set(product_codes_upper) & set(po_codes)
            if matching:
                results.append({
                    "po": po,
                    "match_count": len(matching),
                    "match_rate": len(matching) / max(len(product_codes_upper), len(po_codes))
                })
        
        # Sort by match rate
        results.sort(key=lambda x: x["match_rate"], reverse=True)
        return results
    
    def get_all(self) -> List[Dict]:
        """Get all POs"""
        return self.pos
