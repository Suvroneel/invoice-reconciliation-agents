from fuzzywuzzy import fuzz
from typing import List, Tuple

class FuzzyMatcher:
    @staticmethod
    def match_string(str1: str, str2: str, threshold: int = 80) -> Tuple[bool, int]:
        """Match two strings with fuzzy logic"""
        if not str1 or not str2:
            return False, 0
        
        score = fuzz.ratio(str1.lower(), str2.lower())
        return score >= threshold, score
    
    @staticmethod
    def match_supplier(invoice_supplier: str, po_supplier: str) -> Tuple[bool, int]:
        """Match supplier names (more lenient)"""
        # Remove common variations
        inv_clean = invoice_supplier.lower().replace("ltd", "").replace("limited", "").replace(".", "").strip()
        po_clean = po_supplier.lower().replace("ltd", "").replace("limited", "").replace(".", "").strip()
        
        score = fuzz.ratio(inv_clean, po_clean)
        return score >= 70, score
    
    @staticmethod
    def match_product(invoice_desc: str, po_desc: str) -> Tuple[bool, int]:
        """Match product descriptions"""
        score = fuzz.token_sort_ratio(invoice_desc.lower(), po_desc.lower())
        return score >= 75, score
    
    @staticmethod
    def best_match(query: str, candidates: List[str], threshold: int = 80) -> Tuple[str, int]:
        """Find best match from list of candidates"""
        if not candidates:
            return "", 0
        
        best = ""
        best_score = 0
        
        for candidate in candidates:
            score = fuzz.ratio(query.lower(), candidate.lower())
            if score > best_score:
                best_score = score
                best = candidate
        
        if best_score >= threshold:
            return best, best_score
        return "", 0
