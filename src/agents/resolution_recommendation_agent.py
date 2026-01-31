from orchestration.state import AgentState
from config import Config
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ResolutionRecommendationAgent:
    def process(self, state: AgentState) -> AgentState:
        """Recommend action based on all findings"""
        start_time = time.time()
        
        try:
            extraction_conf = state.get("extraction_confidence", 0)
            matching = state.get("matching_results")
            discrepancies = state.get("discrepancies", [])
            
            # Determine action
            action, risk, confidence, reasoning = self._determine_action(
                extraction_conf, matching, discrepancies
            )
            
            state["recommended_action"] = action
            state["risk_level"] = risk
            state["recommendation_confidence"] = confidence
            state["resolution_reasoning"] = reasoning
            
            # Update trace
            duration = time.time() - start_time
            state["agent_execution_trace"]["resolution_recommendation_agent"] = {
                "duration_ms": int(duration * 1000),
                "confidence": confidence,
                "status": "success"
            }
            
        except Exception as e:
            state["errors"].append(f"Resolution Agent error: {str(e)}")
        
        return state
    
    def _determine_action(self, extraction_conf, matching, discrepancies):
        """Determine recommended action"""
        
        # Check for auto-reject scenarios
        if extraction_conf < Config.LOW_CONFIDENCE:
            return (
                "escalate_to_human",
                "high",
                0.95,
                "Very low extraction confidence (<50%). Document quality too poor for automated processing. Human review required."
            )
        
        if not matching or not matching.get("matched_po"):
            return (
                "escalate_to_human",
                "high",
                0.90,
                "No matching PO found in database. Cannot validate invoice without PO reference. Human review required."
            )
        
        # Count high severity discrepancies
        high_severity = sum(1 for d in discrepancies if d.get("severity") == "high")
        medium_severity = sum(1 for d in discrepancies if d.get("severity") == "medium")
        
        # Escalate if multiple high severity issues
        if high_severity >= 2:
            return (
                "escalate_to_human",
                "high",
                0.95,
                f"Multiple high-severity discrepancies detected ({high_severity}). Requires immediate human review."
            )
        
        # Escalate if significant price variance
        for disc in discrepancies:
            if disc.get("type") == "price_mismatch" and disc.get("severity") == "high":
                variance_pct = disc.get("variance_percentage", 0) * 100
                return (
                    "escalate_to_human",
                    "high",
                    0.98,
                    f"Significant price variance detected ({variance_pct:.1f}%). Exceeds auto-approval threshold. Human review required."
                )
        
        # Flag for review if medium issues
        if high_severity == 1 or medium_severity > 0:
            return (
                "flag_for_review",
                "medium",
                0.85,
                f"Found {high_severity} high and {medium_severity} medium severity discrepancies. Recommend human review before approval."
            )
        
        # Check extraction confidence for auto-approve
        if extraction_conf < Config.MEDIUM_CONFIDENCE:
            return (
                "flag_for_review",
                "medium",
                0.80,
                f"Extraction confidence ({extraction_conf:.0%}) below auto-approve threshold. Recommend review."
            )
        
        # Check matching confidence
        if matching.get("po_match_confidence", 0) < 0.85:
            return (
                "flag_for_review",
                "medium",
                0.80,
                f"PO match confidence ({matching['po_match_confidence']:.0%}) below auto-approve threshold. Recommend review."
            )
        
        # Auto-approve
        if len(discrepancies) == 0 and extraction_conf >= Config.HIGH_CONFIDENCE:
            return (
                "auto_approve",
                "none",
                0.98,
                f"All criteria met for auto-approval. High extraction confidence ({extraction_conf:.0%}), exact PO match, zero discrepancies detected. Safe to approve."
            )
        
        # Default: flag for review
        return (
            "flag_for_review",
            "low",
            0.75,
            "General caution: recommend human review to verify all details."
        )
