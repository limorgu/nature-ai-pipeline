import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# ---------------------------
# 1. Configuration
# ---------------------------
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
LIBRARY_ROOT = RESULTS_BASE / "Organized_Library_Source"

# --- NEW DYNAMIC PATHING (From Session Notes) ---
TOPIC = "nature"
STAGE_NAME = "S4extractor"
VERSION = "V1"
NATURE_OUTPUT_ROOT = RESULTS_BASE / TOPIC / f"{TOPIC}{STAGE_NAME}{VERSION}"

MODEL = "gpt-4o-mini"
MIN_RELEVANCY = 6   
MIN_CONFIDENCE = 7   

# ---------------------------
# 2. Helper: Awareness Logic
# ---------------------------
def get_processed_pages(book_name):
    """Checks the specific version folder for existing results to avoid duplicates."""
    processed_pages = set()
    existing_files = list(NATURE_OUTPUT_ROOT.glob(f"{book_name}_{TOPIC}_*.json"))
    
    for f in existing_files:
        try:
            data = json.loads(f.read_text())
            for entry in data.get("extracted_quotes", []):
                p_num = entry.get("page_number")
                if p_num is not None:
                    processed_pages.add(int(p_num))
        except Exception:
            continue
    return processed_pages

# ---------------------------
# 3. Main Logic
# ---------------------------
def run_stage_4_nature_extraction():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return
    
    client = OpenAI()
    NATURE_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    book_folders = [d for d in LIBRARY_ROOT.iterdir() if d.is_dir()]
    
    for b_folder in book_folders:
        book_name = b_folder.name
        
        # 🧠 Awareness Check
        already_done = get_processed_pages(book_name)
        
        # ✅ Define final_output here so it's fresh for every book
        final_output = {
            "run_metadata": {
                "timestamp": timestamp,
                "model": MODEL,
                "version": VERSION,
                "topic": TOPIC
            },
            "book_info": {"name": book_name},
            "extracted_quotes": [],
            "processing_summary": {
                "pages_scanned": 0,
                "pages_skipped": len(already_done),
                "kept_quotes": 0
            }
        }
        
        print(f"🌿 Analyzing {book_name}... ({len(already_done)} pages already harvested)")
        page_files = sorted(list(b_folder.glob("page_*.json")))
        
        for pf in page_files:
            try:
                # Get page number from filename (e.g., page_10.json -> 10)
                p_num = int(pf.stem.split('_')[1])
                
                # SKIP if already in our awareness set
                if p_num in already_done:
                    continue

                page_data = json.loads(pf.read_text())
                content = page_data.get("content", "")
                if not content: continue

                # (OpenAI Prompt & API Call Logic...)
                # [Snippet shortened for clarity - use your existing prompt here]
                
                # After successful AI response:
                final_output["processing_summary"]["pages_scanned"] += 1
                # ... add to final_output["extracted_quotes"] ...

            except Exception as e:
                print(f"  ⚠️ Error processing {pf.name}: {e}")

        # 💾 Save results to the organized sub-folder
        if final_output["extracted_quotes"]:
            filename = f"{book_name}_{TOPIC}_{timestamp}.json"
            output_file = NATURE_OUTPUT_ROOT / filename
            output_file.write_text(json.dumps(final_output, indent=4))
            print(f"  ✅ Saved: {TOPIC}/{NATURE_OUTPUT_ROOT.name}/{filename}")
        else:
            print(f"  ⏭️ No new quotes or all pages skipped for {book_name}.")

if __name__ == "__main__":
    run_stage_4_nature_extraction()