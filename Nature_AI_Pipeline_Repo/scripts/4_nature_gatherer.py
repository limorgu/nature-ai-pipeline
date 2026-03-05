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
NATURE_OUTPUT_ROOT = RESULTS_BASE / "Nature_Insights"

MODEL = "gpt-4o-mini"
MIN_RELEVANCY = 6   
MIN_CONFIDENCE = 7   

# ---------------------------
# 2. Helper: Get Already Processed Pages
# ---------------------------
def get_processed_pages(book_name):
    """Checks the output folder for existing JSONs and returns a set of page numbers."""
    processed_pages = set()
    # Look for files like 'Educated_TaraWestover_nature_20260304_1200.json'
    existing_files = list(NATURE_OUTPUT_ROOT.glob(f"{book_name}_nature_*.json"))
    
    for f in existing_files:
        try:
            data = json.loads(f.read_text())
            for entry in data.get("extracted_quotes", []):
                # We track by page number to avoid re-scanning the same page
                p_num = entry.get("page_number")
                if p_num is not None:
                    processed_pages.add(int(p_num))
        except Exception as e:
            print(f"  ⚠️ Warning: Could not read existing file {f.name}: {e}")
            
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
        
        # --- AWARENESS CHECK ---
        already_done = get_processed_pages(book_name)
        if already_done:
            print(f"🧠 Awareness: Book '{book_name}' already has {len(already_done)} pages processed.")
        
        final_output = {
            "run_metadata": {
                "timestamp": timestamp,
                "model": MODEL,
                "thresholds": {"min_relevancy": MIN_RELEVANCY, "min_confidence": MIN_CONFIDENCE}
            },
            "book_info": {"name": book_name},
            "extracted_quotes": [],
            "processing_summary": {"total_pages_scanned": 0, "kept_quotes": 0}
        }
        
        page_files = sorted(list(b_folder.glob("page_*.json")))
        
        for pf in page_files:
            try:
                # Extract page number from filename (e.g., 'page_12.json' -> 12)
                current_page_num = int(pf.stem.split('_')[1])
                
                # --- SKIP LOGIC ---
                if current_page_num in already_done:
                    continue 

                page_data = json.loads(pf.read_text())
                content = page_data.get("content", "")
                if not content: continue

                print(f"  ✨ Extracting nature from {book_name} - Page {current_page_num}...")
                
                prompt = f"Extract nature quotes (landscapes, animals, weather) from: {content}. Return ONLY JSON: {{'nature_quotes_found': bool, 'extracted_items': [{{'quote': 'text', 'confidence': 0-10, 'relevancy': 0-10}}]}}"
                
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                ai_res = json.loads(response.choices[0].message.content)

                if ai_res.get("nature_quotes_found"):
                    for item in ai_res.get("extracted_items", []):
                        rel = item.get("relevancy", 0)
                        conf = item.get("confidence", 0)

                        if rel >= MIN_RELEVANCY and conf >= MIN_CONFIDENCE:
                            entry = {
                                "author": page_data.get("book_author", "Unknown"),
                                "quote": item.get("quote"),
                                "confidence": conf,
                                "relevancy": rel,
                                "page_number": current_page_num
                            }
                            final_output["extracted_quotes"].append(entry)
                            final_output["processing_summary"]["kept_quotes"] += 1
                
                final_output["processing_summary"]["total_pages_scanned"] += 1

            except Exception as e:
                print(f"  ⚠️ Error processing {pf.name}: {e}")

        # 💾 Save only if new pages were processed
        if final_output["processing_summary"]["total_pages_scanned"] > 0:
            filename = f"{book_name}_nature_{timestamp}.json"
            (NATURE_OUTPUT_ROOT / filename).write_text(json.dumps(final_output, indent=4))
            print(f"  ✅ Batch Complete: Saved {filename}")
        else:
            print(f"  ⏭️ Skipping {book_name}: No new pages to process.")

if __name__ == "__main__":
    run_stage_4_nature_extraction()
