import json
import pandas as pd
from pathlib import Path
from pipeline_config import AUDIT_REPORTS, CURRENT_TOPIC

def run_stage_6_comparison():
    print(f"--- 📊 Stage 6: Multi-Model Comparison ({CURRENT_TOPIC.upper()}) ---")
    
    all_summaries = list(AUDIT_REPORTS.rglob("summary_analytics_*.json"))
    
    if not all_summaries:
        print("❌ No audit summaries found. Run Stage 5 for at least one model first.")
        return

    master_data = []

    for summary_path in all_summaries:
        try:
            data = json.loads(summary_path.read_text())
            for book_stat in data:
                master_data.append({
                    "Model": book_stat.get("model"),
                    "Book": book_stat.get("book"),
                    "Accuracy": float(book_stat.get("audit_accuracy", "0%").strip('%')),
                    "Quotes Found": book_stat.get("quotes_found"),
                    "Density (per 1k)": book_stat.get("density_per_1k_words")
                })
        except Exception as e:
            print(f"  ⚠️ Error reading {summary_path.name}: {e}")

    if not master_data:
        print("⚠️ No valid data found to compare.")
        return

    # Create DataFrame for easy manipulation
    df = pd.DataFrame(master_data)

    # 1. Generate Pivot Table: Model Comparison per Book
    comparison_table = df.pivot(index="Book", columns="Model", values=["Accuracy", "Quotes Found"])
    
    # 2. Generate Global Model Rankings
    rankings = df.groupby("Model").agg({
        "Accuracy": "mean",
        "Quotes Found": "sum",
        "Density (per 1k)": "mean"
    }).sort_values(by="Accuracy", ascending=False)

    # --- SAVE RESULTS ---
    report_path = AUDIT_REPORTS / f"GLOBAL_COMPARISON_{CURRENT_TOPIC}.csv"
    comparison_table.to_csv(report_path)
    
    print("\n🏆 --- MODEL LEADERBOARD ---")
    print(rankings)
    print(f"\n✅ Comparative Dashboard saved to: {report_path}")

if __name__ == "__main__":
    run_stage_6_comparison()