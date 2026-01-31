import os
from dotenv import load_dotenv
import tempfile

load_dotenv()


class Config:
    # Hugging Face - Try Streamlit secrets first, then .env
    try:
        import streamlit as st
        HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN", ""))
    except:
        HF_TOKEN = os.getenv("HF_TOKEN", "")

    HF_MODEL = "meta-llama/Llama-3.2-3B-Instruct"

    # Paths - use temp directory for cloud deployment
    DATA_DIR = "data"
    INVOICES_DIR = os.path.join(DATA_DIR, "invoices")
    PO_FILE = os.path.join(DATA_DIR, "purchase_orders", "purchase_orders.json")

    # Output directory - use temp for cloud, local for CLI
    if os.getenv("STREAMLIT_RUNTIME_ENV") or os.getenv("HOME") == "/home/appuser":
        # Running on Streamlit Cloud
        OUTPUT_DIR = tempfile.mkdtemp()
    else:
        # Running locally
        OUTPUT_DIR = "src/outputs"

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.90
    MEDIUM_CONFIDENCE = 0.70
    LOW_CONFIDENCE = 0.50

    # Matching thresholds
    PRICE_TOLERANCE = 0.02  # 2%
    SIGNIFICANT_PRICE_VARIANCE = 0.15  # 15%
    TOTAL_VARIANCE_AMOUNT = 5.0  # £5
    TOTAL_VARIANCE_PERCENT = 0.01  # 1%

    # OCR settings
    TESSERACT_CONFIG = '--oem 3 --psm 6'

    @staticmethod
    def ensure_directories():
        os.makedirs(Config.INVOICES_DIR, exist_ok=True)
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        if not os.path.exists(os.path.dirname(Config.PO_FILE)):
            os.makedirs(os.path.dirname(Config.PO_FILE), exist_ok=True)