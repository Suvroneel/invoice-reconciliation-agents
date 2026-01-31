from langgraph.graph import StateGraph, END
from orchestration.state import AgentState
from agents.document_intelligence_agent import DocumentIntelligenceAgent
from agents.matching_agent import MatchingAgent
from agents.discrepancy_detection_agent import DiscrepancyDetectionAgent
from agents.resolution_recommendation_agent import ResolutionRecommendationAgent
import time
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InvoiceReconciliationGraph:
    def __init__(self):
        self.doc_agent = DocumentIntelligenceAgent()
        self.matching_agent = MatchingAgent()
        self.discrepancy_agent = DiscrepancyDetectionAgent()
        self.resolution_agent = ResolutionRecommendationAgent()
        
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("document_intelligence", self._document_intelligence_node)
        workflow.add_node("matching", self._matching_node)
        workflow.add_node("discrepancy_detection", self._discrepancy_node)
        workflow.add_node("resolution", self._resolution_node)
        
        # Define edges (linear flow for now)
        workflow.set_entry_point("document_intelligence")
        workflow.add_edge("document_intelligence", "matching")
        workflow.add_edge("matching", "discrepancy_detection")
        workflow.add_edge("discrepancy_detection", "resolution")
        workflow.add_edge("resolution", END)
        
        return workflow.compile()
    
    def _document_intelligence_node(self, state: AgentState) -> AgentState:
        """Document Intelligence Agent node"""
        print("📄 Running Document Intelligence Agent...")
        return self.doc_agent.process(state)
    
    def _matching_node(self, state: AgentState) -> AgentState:
        """Matching Agent node"""
        print("🔍 Running Matching Agent...")
        return self.matching_agent.process(state)
    
    def _discrepancy_node(self, state: AgentState) -> AgentState:
        """Discrepancy Detection Agent node"""
        print("⚠️  Running Discrepancy Detection Agent...")
        return self.discrepancy_agent.process(state)
    
    def _resolution_node(self, state: AgentState) -> AgentState:
        """Resolution Recommendation Agent node"""
        print("✅ Running Resolution Recommendation Agent...")
        return self.resolution_agent.process(state)
    
    def process_invoice(self, invoice_path: str, invoice_filename: str) -> dict:
        """Process a single invoice through the workflow"""
        start_time = time.time()
        
        # Initialize state
        initial_state: AgentState = {
            "invoice_path": invoice_path,
            "invoice_filename": invoice_filename,
            "extraction_confidence": 0.0,
            "document_quality": "",
            "extracted_data": None,
            "extraction_reasoning": "",
            "matching_results": None,
            "matching_reasoning": "",
            "discrepancies": [],
            "total_variance_amount": 0.0,
            "total_variance_percentage": 0.0,
            "discrepancy_reasoning": "",
            "recommended_action": "",
            "risk_level": "",
            "recommendation_confidence": 0.0,
            "resolution_reasoning": "",
            "processing_timestamp": datetime.utcnow().isoformat() + "Z",
            "processing_duration_seconds": 0.0,
            "agent_execution_trace": {},
            "errors": []
        }
        
        # Run the graph
        print(f"\n{'='*60}")
        print(f"Processing: {invoice_filename}")
        print(f"{'='*60}")
        
        final_state = self.graph.invoke(initial_state)
        
        # Calculate duration
        duration = time.time() - start_time
        final_state["processing_duration_seconds"] = duration
        
        print(f"\n✓ Processing complete in {duration:.2f}s")
        print(f"Action: {final_state['recommended_action']}")
        print(f"Risk: {final_state['risk_level']}")
        
        return self._format_output(final_state)
    
    def _format_output(self, state: AgentState) -> dict:
        """Format final output JSON"""
        extracted = state.get("extracted_data", {})
        matching = state.get("matching_results", {})
        
        return {
            "invoice_id": extracted.get("invoice_number", "UNKNOWN") if extracted else "UNKNOWN",
            "processing_timestamp": state["processing_timestamp"],
            "processing_duration_seconds": state["processing_duration_seconds"],
            "document_info": {
                "filename": state["invoice_filename"],
                "document_quality": state["document_quality"]
            },
            "processing_results": {
                "extraction_confidence": state["extraction_confidence"],
                "document_quality": state["document_quality"],
                "extracted_data": extracted,
                "matching_results": matching,
                "discrepancies": state["discrepancies"],
                "total_variance": {
                    "amount": state["total_variance_amount"],
                    "percentage": state["total_variance_percentage"],
                    "within_tolerance": state["total_variance_amount"] <= 5.0 and state["total_variance_percentage"] <= 0.01
                },
                "recommended_action": state["recommended_action"],
                "risk_level": state["risk_level"],
                "confidence": state["recommendation_confidence"],
                "agent_reasoning": self._build_full_reasoning(state)
            },
            "agent_execution_trace": state["agent_execution_trace"],
            "errors": state["errors"]
        }
    
    def _build_full_reasoning(self, state: AgentState) -> str:
        """Build complete reasoning chain"""
        parts = []
        
        if state["extraction_reasoning"]:
            parts.append(f"EXTRACTION: {state['extraction_reasoning']}")
        
        if state["matching_reasoning"]:
            parts.append(f"MATCHING: {state['matching_reasoning']}")
        
        if state["discrepancy_reasoning"]:
            parts.append(f"DISCREPANCIES: {state['discrepancy_reasoning']}")
        
        if state["resolution_reasoning"]:
            parts.append(f"RESOLUTION: {state['resolution_reasoning']}")
        
        return " | ".join(parts)
