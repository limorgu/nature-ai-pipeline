import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# ---------------------------
# 1. Configuration
# ---------------------------
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
LIBRARY_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Organized_Library_Source")
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
NATURE_OUTPUT_ROOT = RESULTS_BASE / "Nature_Insights"
# --- STEP 4 CONFIG UPDATES ---
MODEL = "gpt-4o-mini"
MIN_RELEVANCY = 6   # Lowered to ensure we don't miss potential "edge case" quotes
MIN_CONFIDENCE = 7   # Keep this higher to maintain quality, but we can be more lenient on relevancy since we'll audit later 

# ---------------------------
# 2. Logic
# ---------------------------
def run_stage_4_nature_extraction():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return
    
    client = OpenAI()
    NATURE_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # 🕒 Create a unique timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    book_folders = [d for d in LIBRARY_ROOT.iterdir() if d.is_dir()]
    
    for b_folder in book_folders:
        final_output = {
            "run_metadata": {
                "timestamp": timestamp,
                "model": MODEL,
                "thresholds": {"min_relevancy": MIN_RELEVANCY, "min_confidence": MIN_CONFIDENCE}
            },
            "book_info": {"name": b_folder.name},
            "extracted_quotes": [],
            "processing_summary": {
                "total_quotes_identified": 0,
                "kept_quotes": 0,
                "filtered_out_low_quality": 0
            }
        }
        
        print(f"🌿 Analyzing {b_folder.name} (Run: {timestamp})...")
        page_files = sorted(list(b_folder.glob("page_*.json")))
        
        for pf in page_files:
            try:
                page_data = json.loads(pf.read_text())
                content = page_data.get("content", "")
                if not content: continue

                prompt = f"""
                Extract any quotes that mention nature, landscapes, animals, or weather. 
                Err on the side of inclusion.
                Assign scores based on your best judgment.
                
                Text: {content}
                
                Return ONLY a JSON object:
                {{
                    "nature_quotes_found": true,
                    "extracted_items": [
                        {{ "quote": "text", "confidence": 8, "relevancy": 7 }}
                    ]
                }}
                """
                
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                ai_res = json.loads(response.choices[0].message.content)

                if ai_res.get("nature_quotes_found"):
                    for item in ai_res.get("extracted_items", []):
                        final_output["processing_summary"]["total_quotes_identified"] += 1
                        
                        rel = item.get("relevancy", 0)
                        conf = item.get("confidence", 0)

                        if rel >= MIN_RELEVANCY and conf >= MIN_CONFIDENCE:
                            entry = {
                                "author": page_data.get("book_author", "Unknown"),
                                "quote": item.get("quote"),
                                "confidence": conf,
                                "relevancy": rel,
                                "page_number": page_data.get("page_number")
                            }
                            final_output["extracted_quotes"].append(entry)
                            final_output["processing_summary"]["kept_quotes"] += 1
                        else:
                            final_output["processing_summary"]["filtered_out_low_quality"] += 1

            except Exception as e:
                print(f"  ⚠️ Error processing {pf.name}: {e}")

        # 💾 Save results with timestamp in the name
        if final_output["extracted_quotes"]:
            filename = f"{b_folder.name}_nature_{timestamp}.json"
            output_file = NATURE_OUTPUT_ROOT / filename
            output_file.write_text(json.dumps(final_output, indent=4))
            
            s = final_output["processing_summary"]
            print(f"  ✅ Saved: {filename} (Kept {s['kept_quotes']}, Filtered {s['filtered_out_low_quality']})")
        else:
            print(f"  🍃 No quotes met the bar for {b_folder.name} in this run.")

if __name__ == "__main__":
    run_stage_4_nature_extraction()