import os
import json
import csv
from pathlib import Path
from datetime import datetime

# ---------------------------
# 1. Configuration
# ---------------------------
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
# This is the root where the timestamped book folders live
AUDIT_INPUT_ROOT = RESULTS_BASE / "openai_audits"

TOPIC = "nature"
AUDIT_VERSION = "V1"

def run_performance_summary():
    # 🔍 Recursive search to find audits deep in the new hierarchy
    audit_files = list(AUDIT_INPUT_ROOT.rglob("*_WISE_AUDIT_*.json"))
    
    if not audit_files:
        print(f"⚠️ No audit files found in hierarchy: {AUDIT_INPUT_ROOT}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # We will save a global CSV summary in the root for easy access
    global_csv_path = AUDIT_INPUT_ROOT / f"global_accuracy_{TOPIC}_{timestamp}.csv"

    rows = []
    overall_total = 0
    overall_errors = 0

    print(f"\n{'Book Run Folder':<45} | {'Total':<5} | {'Clean':<5} | {'Accuracy':<8}")
    print("-" * 75)

    for f in audit_files:
        try:
            data = json.loads(f.read_text())
            book_name = data.get("book_name") or "Unknown"
            results = data.get("results", [])
            
            # 🧹 PURIFICATION: Filter out metaphors and errors
            clean_quotes = [item for item in results if not item.get("is_nature_error")]
            
            total = len(results)
            errors = total - len(clean_quotes)
            accuracy = (len(clean_quotes) / total * 100) if total > 0 else 0
            
            overall_total += total
            overall_errors += errors

            # 📂 LOCAL SAVE: Save the "Gold" results inside the book's run folder
            # Path: .../openai_audits/[Book_Timestamp]/S6_Gold/
            parent_run_dir = f.parent.parent
            gold_dir = parent_run_dir / "S6_Gold"
            gold_dir.mkdir(parents=True, exist_ok=True)
            
            gold_data = {
                "purification_metadata": {
                    "source_audit_file": f.name,
                    "date_purified": timestamp,
                    "version": AUDIT_VERSION
                },
                "verified_quotes": clean_quotes
            }
            
            gold_file = gold_dir / f"{book_name}_GOLD_STANDARD.json"
            gold_file.write_text(json.dumps(gold_data, indent=4))

            print(f"{parent_run_dir.name[:45]:<45} | {total:<5} | {len(clean_quotes):<5} | {accuracy:>7.1f}%")

            rows.append({
                "Book Run": parent_run_dir.name,
                "Total Quotes": total,
                "Clean Quotes": len(clean_quotes),
                "Accuracy (%)": round(accuracy, 2)
            })

        except Exception as e:
            print(f"  ⚠️ Error processing {f.name}: {e}")

    # 💾 GLOBAL REPORT: Save the overall CSV
    if rows:
        fieldnames = ["Book Run", "Total Quotes", "Clean Quotes", "Accuracy (%)"]
        with open(global_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
            global_acc = ((overall_total - overall_errors) / overall_total * 100) if overall_total > 0 else 0
            writer.writerow({
                "Book Run": "TOTAL OVERALL PROJECT",
                "Total Quotes": overall_total,
                "Clean Quotes": overall_total - overall_errors,
                "Accuracy (%)": round(global_acc, 2)
            })

        print("-" * 75)
        print(f"✅ Purification Complete & Global Report Created!")
        print(f"📍 Global CSV: {global_csv_path.name}\n")

if __name__ == "__main__":
    run_performance_summary()