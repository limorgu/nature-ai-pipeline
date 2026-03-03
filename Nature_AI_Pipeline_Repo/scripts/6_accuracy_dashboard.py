import json
import csv
from pathlib import Path
from datetime import datetime

# ---------------------------
# 1. Configuration
# ---------------------------
# Ensure this matches your exact path (corrected from previous typo)
AUDIT_INPUT_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results/openai_audits")

def run_performance_summary():
    # 🔍 Find all the latest "WISE_AUDIT" files
    audit_files = list(AUDIT_INPUT_ROOT.glob("*_WISE_AUDIT_*.json"))
    
    if not audit_files:
        print(f"⚠️ No audit files found in {AUDIT_INPUT_ROOT}")
        return

    # 🕒 Generate timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    csv_filename = f"accuracy_check_openai_results_{timestamp}.csv"
    csv_path = AUDIT_INPUT_ROOT / csv_filename

    # Prepare data for console and CSV
    rows = []
    overall_total = 0
    overall_errors = 0

    print(f"\n{'Book Name':<40} | {'Total':<6} | {'Errors':<6} | {'Accuracy':<8}")
    print("-" * 70)

    for f in audit_files:
        try:
            data = json.loads(f.read_text())
            # Extract book name or fallback to filename
            book_name = data.get("book_name") or f.stem.split('_WISE_AUDIT')[0]
            results = data.get("results", [])
            
            total = len(results)
            errors = sum(1 for item in results if item.get("is_nature_error"))
            accuracy = ((total - errors) / total * 100) if total > 0 else 0
            
            overall_total += total
            overall_errors += errors

            # Console Print
            print(f"{book_name[:40]:<40} | {total:<6} | {errors:<6} | {accuracy:>7.1f}%")

            # Store for CSV
            rows.append({
                "Book Name": book_name,
                "Total Quotes": total,
                "Errors Found": errors,
                "Accuracy (%)": round(accuracy, 2)
            })

        except Exception as e:
            print(f"  ⚠️ Error reading {f.name}: {e}")

    # 💾 Save to CSV
    if rows:
        fieldnames = ["Book Name", "Total Quotes", "Errors Found", "Accuracy (%)"]
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
            # Add a total row at the end of CSV
            global_acc = ((overall_total - overall_errors) / overall_total * 100) if overall_total > 0 else 0
            writer.writerow({
                "Book Name": "TOTAL OVERALL",
                "Total Quotes": overall_total,
                "Errors Found": overall_errors,
                "Accuracy (%)": round(global_acc, 2)
            })

        print("-" * 70)
        print(f"✅ CSV Report Created!")
        print(f"📍 Location: {csv_path}\n")
    else:
        print("No valid data found to export.")

if __name__ == "__main__":
    run_performance_summary()
    