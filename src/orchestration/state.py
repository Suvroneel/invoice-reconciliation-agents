from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class LineItem(TypedDict):
    item_code: str
    description: str
    quantity: float
    unit: str
    unit_price: float
    line_total: float
    extraction_confidence: float


class ExtractedInvoice(TypedDict):
    invoice_number: str
    invoice_date: str
    supplier_name: str
    supplier_address: Optional[str]
    supplier_vat: Optional[str]
    po_reference: Optional[str]
    payment_terms: Optional[str]
    currency: str
    line_items: List[LineItem]
    subtotal: float
    vat_amount: float
    vat_rate: float
    total: float


class MatchingResult(TypedDict):
    po_match_confidence: float
    matched_po: Optional[str]
    match_method: str
    supplier_match: bool
    line_items_matched: int
    line_items_total: int
    match_rate: float
    alternative_matches: List[Dict[str, Any]]


class Discrepancy(TypedDict):
    type: str
    severity: str
    field: str
    details: str
    invoice_value: Optional[float]
    po_value: Optional[float]
    variance_percentage: Optional[float]
    confidence: float


class AgentState(TypedDict):
    # Input
    invoice_path: str
    invoice_filename: str

    # Document Intelligence Agent outputs
    extraction_confidence: float
    document_quality: str
    extracted_data: Optional[ExtractedInvoice]
    extraction_reasoning: str

    # Matching Agent outputs
    matching_results: Optional[MatchingResult]
    matching_reasoning: str

    # Discrepancy Detection Agent outputs
    discrepancies: List[Discrepancy]
    total_variance_amount: float
    total_variance_percentage: float
    discrepancy_reasoning: str

    # Resolution Recommendation Agent outputs
    recommended_action: str
    risk_level: str
    recommendation_confidence: float
    resolution_reasoning: str

    # Metadata
    processing_timestamp: str
    processing_duration_seconds: float
    agent_execution_trace: Dict[str, Any]
    errors: List[str]
