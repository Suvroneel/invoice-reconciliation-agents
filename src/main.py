import os
import json
import sys

# Add src directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from config import Config
from orchestration.graph import InvoiceReconciliationGraph


def main():
    """Main execution function"""
    print("🚀 Invoice Reconciliation Agent System")
    print("=" * 60)

    # Ensure directories exist
    Config.ensure_directories()

    # Initialize the graph
    graph = InvoiceReconciliationGraph()

    # Get all invoice files
    invoice_files = []
    if os.path.exists(Config.INVOICES_DIR):
        for file in os.listdir(Config.INVOICES_DIR):
            if file.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt')):
                invoice_files.append(file)

    if not invoice_files:
        print("❌ No invoice files found in data/invoices/")
        print(f"Please add invoices to: {Config.INVOICES_DIR}")
        return

    print(f"\nFound {len(invoice_files)} invoice(s) to process\n")

    # Process each invoice
    results = []
    for idx, filename in enumerate(invoice_files, 1):
        invoice_path = os.path.join(Config.INVOICES_DIR, filename)

        try:
            result = graph.process_invoice(invoice_path, filename)
            results.append(result)

            # Save individual output
            output_filename = f"invoice_{idx}_output.json"
            output_path = os.path.join(Config.OUTPUT_DIR, output_filename)

            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"💾 Saved output to: {output_path}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'=' * 60}")
    print("📊 PROCESSING SUMMARY")
    print(f"{'=' * 60}")

    auto_approve = sum(1 for r in results if r['processing_results']['recommended_action'] == 'auto_approve')
    flag_review = sum(1 for r in results if r['processing_results']['recommended_action'] == 'flag_for_review')
    escalate = sum(1 for r in results if r['processing_results']['recommended_action'] == 'escalate_to_human')

    print(f"Total Processed: {len(results)}")
    print(f"Auto-Approve: {auto_approve}")
    print(f"Flag for Review: {flag_review}")
    print(f"Escalate to Human: {escalate}")
    print(f"\n✅ All outputs saved to: {Config.OUTPUT_DIR}")

    # Total time
    total_time = sum(r['processing_duration_seconds'] for r in results)
    print(f"⏱️  Total processing time: {total_time:.2f}s")

    if total_time < 300:  # 5 minutes
        print("✅ Performance target met (<5 minutes)")
    else:
        print("⚠️  Performance target exceeded (>5 minutes)")


if __name__ == "__main__":
    main()