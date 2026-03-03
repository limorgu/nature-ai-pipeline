import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ---------------------------
# 1. Configuration
# ---------------------------

# --- Configuration Updates ---
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
# READ from here (output of Stage 4)
NATURE_INPUT_ROOT = RESULTS_BASE / "Nature_Insights"

# SAVE to here (Isolating the Audit results)
AUDIT_OUTPUT_ROOT = RESULTS_BASE / "openai_audits"
MODEL = "gpt-4o"  # The "Wiser" Model

def run_stage_5_wise_audit():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return
    
    client = OpenAI()
    AUDIT_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    insight_files = [f for f in NATURE_INPUT_ROOT.glob("*.json") if "nature" in f.name.lower()]
    
    for f in insight_files:
        print(f"\n🧠 Wise Audit in progress: {f.name} using {MODEL}...")
        try:
            data = json.loads(f.read_text())
            quotes_to_process = data if isinstance(data, list) else data.get("extracted_quotes", [])

            if not quotes_to_process: continue

            # Constructing the critique list
            quotes_block = "\n".join([f"- {q.get('Quote', q.get('quote', ''))}" for q in quotes_to_process])
            
            # --- THE "WISE" PROMPT ---
            prompt = f"""
            You are a senior editor auditing an automated extraction. 
            Review these quotes and categorize them into: 'Animals', 'Weather', 'Nature Places', 'Fruit/Vegetables', or 'Trees/Flowers'.
            
            CRITICAL: Check for 'false positives'. If a quote is a metaphor (e.g., 'lion-hearted') or urban-centric, 
            mark 'is_nature_error': true and explain why.
            
            Quotes:
            {quotes_block}

            Return ONLY JSON:
            {{
                "audit_results": [
                    {{ "quote": "text", "category": "name", "is_nature_error": false, "reasoning": "Keep it brief" }}
                ]
            }}
            """

            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            ai_audit = json.loads(response.choices[0].message.content)
            
            # Metadata for clean lineage
            audit_report = {
                "audit_lineage": {
                    "input_file": f.name,
                    "auditor_model": MODEL,
                    "date": timestamp
                },
                "book_name": f.stem.split('_nature')[0],
                "results": ai_audit.get("audit_results", [])
            }

            output_file = AUDIT_OUTPUT_ROOT / f"{f.stem}_WISE_AUDIT_{timestamp}.json"
            output_file.write_text(json.dumps(audit_report, indent=4))
            
            print(f"  ✅ Saved to: {output_file}")

        except Exception as e:
            print(f"  ⚠️ Error: {e}")

if __name__ == "__main__":
    run_stage_5_wise_audit()