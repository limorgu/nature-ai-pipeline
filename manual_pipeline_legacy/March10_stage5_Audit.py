import json
import csv
from pathlib import Path
from openai import OpenAI
from datetime import datetime
from pipeline_config import GOLD_LIBRARY, CURRENT_TOPIC, CURRENT_MODEL, get_audit_run_path

def run_comparative_audit():
    client = OpenAI()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Use the helper from config to create a timestamped run folder
    run_dir = get_audit_run_path(timestamp)
    
    # Audit specifically the current topic and model's output
    model_gold_dir = GOLD_LIBRARY / CURRENT_TOPIC / CURRENT_MODEL
    
    if not model_gold_dir.exists():
        print(f"❌ Error: No results found for {CURRENT_MODEL} in {CURRENT_TOPIC}")
        return

    detailed_log = []
    summary_stats = []

    print(f"⚖️ Starting Comparative Audit for Model: {CURRENT_MODEL}")

    # Iterate through each book folder in the model's gold directory
    for book_folder in [d for d in model_gold_dir.iterdir() if d.is_dir()]:
        # FIXED: Safer file finding logic
        final_files = list(book_folder.glob("*_FINAL.json"))
        if not final_files:
            print(f"  ⏭️ Skipping {book_folder.name}: No _FINAL.json found.")
            continue
            
        final_file = final_files[0]
        
        try:
            data = json.loads(final_file.read_text())
            total_words = data.get("total_words", 0)
            quotes = data.get("quotes", [])
            
            if not quotes:
                print(f"  ⏭️ Skipping {book_folder.name}: Quotes list is empty.")
                continue

            pass_count = 0
            print(f"  🔍 Auditing {book_folder.name} ({len(quotes)} quotes)...")

            for q in quotes:
                # Judge logic
                audit_prompt = f"Is this a literal {CURRENT_TOPIC} quote? '{q['quote']}'. Return JSON: {{'status': 'PASS/FAIL', 'reason': 'str'}}"
                res = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "user", "content": audit_prompt}], 
                    response_format={"type": "json_object"}
                )
                audit_res = json.loads(res.choices[0].message.content)
                
                status = audit_res.get("status", "FAIL")
                if status == "PASS": pass_count += 1
                
                detailed_log.append({
                    "book": book_folder.name,
                    "model": CURRENT_MODEL,
                    "quote": q.get('quote'),
                    "page": q.get('page_id'),
                    "status": status,
                    "reason": audit_res.get("reason"),
                    "relevancy": q.get("relevancy"),
                    "confidence": q.get("confidence")
                })

            # Calculate Density & Accuracy
            density = (len(quotes) / total_words * 1000) if total_words > 0 else 0
            accuracy_pct = (pass_count / len(quotes) * 100)
            
            summary_stats.append({
                "model": CURRENT_MODEL,
                "book": book_folder.name,
                "total_words": total_words,
                "quotes_found": len(quotes),
                "density_per_1k_words": round(density, 2),
                "audit_accuracy": f"{accuracy_pct:.1f}%"
            })

        except Exception as e:
            print(f"  ❌ Error processing {book_folder.name}: {e}")

    # --- SAVE OUTPUTS ---
    if detailed_log:
        # Save Detailed CSV
        csv_path = run_dir / f"detailed_audit_{CURRENT_MODEL}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=detailed_log[0].keys())
            writer.writeheader()
            writer.writerows(detailed_log)
        
        # Save Summary JSON
        summary_path = run_dir / f"summary_analytics_{CURRENT_MODEL}.json"
        summary_path.write_text(json.dumps(summary_stats, indent=4))
        
        print(f"\n📊 Audit complete. Results saved in: {run_dir}")
    else:
        print("⚠️ No data was audited.")

if __name__ == "__main__":
    run_comparative_audit()