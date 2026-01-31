# 🚀 QUICK SETUP GUIDE

## Step 1: Install Tesseract OCR (REQUIRED)

### Windows:
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH: 
   - Search "Environment Variables" in Windows
   - Add `C:\Program Files\Tesseract-OCR` to PATH

### Test installation:
```bash
tesseract --version
```

## Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Set Up Hugging Face Token

1. Go to: https://huggingface.co/settings/tokens
2. Create a token (read access)
3. Create `.env` file:

```bash
# Copy .env.example to .env
copy .env.example .env

# Edit .env and add your token:
HF_TOKEN=hf_your_token_here
```

## Step 4: Add Your Invoices

The system already has sample invoice text files for testing. If you have the actual PDF files:

```bash
# Copy PDFs to:
data/invoices/
```

## Step 5: RUN!

```bash
python src/main.py
```

## Expected Output:

```
🚀 Invoice Reconciliation Agent System
============================================================

Found 5 invoice(s) to process

============================================================
Processing: Invoice_1_Baseline.txt
============================================================
📄 Running Document Intelligence Agent...
🔍 Running Matching Agent...
⚠️  Running Discrepancy Detection Agent...
✅ Running Resolution Recommendation Agent...

✓ Processing complete in 12.4s
Action: auto_approve
Risk: none
💾 Saved output to: src/outputs/invoice_1_output.json

... (continues for all 5 invoices)

============================================================
📊 PROCESSING SUMMARY
============================================================
Total Processed: 5
Auto-Approve: 2
Flag for Review: 1
Escalate to Human: 2

✅ All outputs saved to: src/outputs
⏱️  Total processing time: 62.4s
✅ Performance target met (<5 minutes)
```

## Outputs Location:

```
src/outputs/
├── invoice_1_output.json
├── invoice_2_output.json
├── invoice_3_output.json
├── invoice_4_output.json
└── invoice_5_output.json
```

## Troubleshooting:

### "Tesseract not found"
- Make sure Tesseract is installed
- Add to PATH (see Step 1)
- Restart terminal after adding to PATH

### "HF_TOKEN not set"
- Create `.env` file with your token
- Make sure `.env` is in project root directory

### "No module named 'langgraph'"
- Run: `pip install -r requirements.txt`

### Low extraction confidence
- The text files work well for testing
- For real PDFs, ensure good quality scans

## What's Next?

1. **Test locally first** - Make sure it runs
2. **Push to GitHub** - Create a repo
3. **Record demo video** - Show it working
4. **Deploy** (optional) - We can deploy to HuggingFace Spaces later

## Need Help?

Check the main README.md for detailed documentation!
