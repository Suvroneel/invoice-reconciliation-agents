import os
import sys
import streamlit as st
import json
import tempfile

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.orchestration.graph import InvoiceReconciliationGraph
from src.config import Config

st.set_page_config(page_title="Invoice Reconciliation", page_icon="📄", layout="wide")

st.title("📄 Invoice Reconciliation Agent System")
st.markdown("*Multi-agent AI for automated invoice processing*")

# Initialize
Config.ensure_directories()
graph = InvoiceReconciliationGraph()

# File uploader
uploaded_file = st.file_uploader(
    "Upload Invoice (PDF, JPG, PNG)",
    type=["pdf", "jpg", "jpeg", "png"]
)

if uploaded_file:
    # Save to temp file (cloud-compatible)
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        temp_path = tmp_file.name

    # Process
    with st.spinner("🤖 Processing invoice..."):
        try:
            result = graph.process_invoice(temp_path, uploaded_file.name)

            # Display results
            st.success(f"✅ Action: {result['processing_results']['recommended_action'].replace('_', ' ').upper()}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence", f"{result['processing_results']['confidence']:.0%}")
            with col2:
                st.metric("Risk Level", result['processing_results']['risk_level'].upper())
            with col3:
                st.metric("Processing Time", f"{result['processing_duration_seconds']:.1f}s")

            # Show discrepancies if any
            if result['processing_results']['discrepancies']:
                st.warning("⚠️ Discrepancies Detected:")
                for disc in result['processing_results']['discrepancies']:
                    st.write(f"- **{disc['type']}** ({disc['severity']}): {disc['details']}")

            # Show reasoning
            with st.expander("🧠 Agent Reasoning"):
                st.write(result['processing_results']['agent_reasoning'])

            # Full JSON
            with st.expander("📋 Full Results (JSON)"):
                st.json(result)

            # Download button for JSON
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="💾 Download Results (JSON)",
                data=json_str,
                file_name=f"{uploaded_file.name}_results.json",
                mime="application/json"
            )

        except Exception as e:
            st.error(f"❌ Error processing invoice: {str(e)}")
            import traceback

            st.code(traceback.format_exc())

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
