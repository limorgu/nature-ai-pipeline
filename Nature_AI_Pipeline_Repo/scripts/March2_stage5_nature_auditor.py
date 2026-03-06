import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ---------------------------
# 1. Configuration
# ---------------------------
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
# The root where all book-run folders live
AUDIT_INPUT_ROOT = RESULTS_BASE / "openai_audits"

TOPIC = "nature"
AUDIT_VERSION = "V1"
MODEL = "gpt-4o"  # The high-precision model for filtering metaphors

# ---------------------------
# 2. Helper: Awareness Logic
# ---------------------------
def get_already_audited_files():
    """Checks the hierarchical audit folders to see which files are already done."""
    audited_inputs = set()
    # Recursively look for any WISE_AUDIT files in the entire tree
    existing_audits = list(AUDIT_INPUT_ROOT.rglob("*_WISE_AUDIT_*.json"))
    
    for f in existing_audits:
        try:
            audit_data = json.loads(f.read_text())
            original_file = audit_data.get("audit_lineage", {}).get("input_file")
            if original_file:
                # Store only the filename to compare against current insight_files
                audited_inputs.add(Path(original_file).name)
        except Exception:
            continue
    return audited_inputs

# ---------------------------
# 3. Main Logic
# ---------------------------
def run_stage_5_wise_audit():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return
    
    client = OpenAI()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # 🧠 Awareness Check across all versioned subfolders
    already_audited = get_already_audited_files()
    
    # 🔍 Search recursively for S4 files to audit (matches Topic)
    insight_files = list(AUDIT_INPUT_ROOT.rglob(f"*_{TOPIC}_*.json"))
    
    if not insight_files:
        print(f"⚠️ No extraction files found for topic '{TOPIC}' in {AUDIT_INPUT_ROOT}")
        return

    for f in insight_files:
        # SKIP if this specific file has already been audited
        if f.name in already_audited:
            continue

        # 📂 Folder Discovery: Extracts [Book_Name_Timestamp] from path
        # Path structure: AUDIT_INPUT_ROOT / [Book_Run_Folder] / S4_V1 / file.json
        book_run_folder = f.parts[-3] 
        audit_dir = AUDIT_INPUT_ROOT / book_run_folder / f"S5_{AUDIT_VERSION}"
        
        print(f"\n🧠 Wise Audit in progress: {f.name} (Saved to: {book_run_folder}/S5_{AUDIT_VERSION})")
        
        try:
            data = json.loads(f.read_text())
            quotes_to_process = data.get("extracted_quotes", [])

            if not quotes_to_process:
                print(f"  🍃 Skipping: No quotes found in source.")
                continue

            # Constructing the critique list for the AI
            quotes_block = "\n".join([f"- {q.get('quote', '')}" for q in quotes_to_process])
            
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
                    {{ "quote": "text", "category": "name", "is_nature_error": false, "reasoning": "brief note" }}
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
                    "input_file": str(f.relative_to(RESULTS_BASE)),
                    "auditor_model": MODEL,
                    "version": AUDIT_VERSION,
                    "date": timestamp
                },
                "book_name": data.get("book_info", {}).get("name", "Unknown"),
                "results": ai_audit.get("audit_results", [])
            }

            # 💾 Save to the sibling S5 folder
            audit_dir.mkdir(parents=True, exist_ok=True)
            output_file = audit_dir / f"{f.stem}_WISE_AUDIT_{timestamp}.json"
            output_file.write_text(json.dumps(audit_report, indent=4))
            
            print(f"  ✅ Audit Secured: {output_file.relative_to(AUDIT_INPUT_ROOT)}")

        except Exception as e:
            print(f"  ⚠️ Error auditing {f.name}: {e}")

if __name__ == "__main__":
    run_stage_5_wise_audit()