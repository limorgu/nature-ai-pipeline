import os
import json
import requests
from datetime import datetime
from pathlib import Path

# ---------------------------
# 1. Configuration
# ---------------------------
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
LIBRARY_ROOT = RESULTS_BASE / "Organized_Library_Source"

# List of models to benchmark
MODELS_TO_RUN = [
    "deepseek-r1:8b",
    "gemma2:9b",
    "qwen2.5:14b"
]

OLLAMA_URL = "http://localhost:11434/api/chat"
TOPIC = "nature"
BOOKS_LIMIT = 2
PAGES_LIMIT = 10 

# ---------------------------
# 2. Sequential Extraction
# ---------------------------
def run_multi_model_benchmarking():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    for model_name in MODELS_TO_RUN:
        # STEP 1: Create Model-Specific Root (e.g., S7_Gemma2_Drafts)
        clean_model_name = model_name.split(":")[0].replace(".", "_").capitalize()
        model_root_folder = RESULTS_BASE / f"S7_{clean_model_name}_Drafts"
        model_root_folder.mkdir(parents=True, exist_ok=True)

        print(f"\n🚀 STARTING EXTRACTION: {model_name}")
        
        book_folders = sorted([d for d in LIBRARY_ROOT.iterdir() if d.is_dir()])
        books_processed = 0

        for b_folder in book_folders:
            if books_processed >= BOOKS_LIMIT: break
            book_name = b_folder.name
            
            # STEP 2: Create Book-Specific Folder inside the Model Root
            # Path: .../S7_Gemma2_Drafts/Educated/
            book_output_dir = model_root_folder / book_name
            
            # STEP 3: Create a timestamped Run Folder
            # Path: .../S7_Gemma2_Drafts/Educated/Gemma2_Run_20260309_1930/
            run_dir = book_output_dir / f"{clean_model_name}_Run_{timestamp}"
            run_dir.mkdir(parents=True, exist_ok=True)

            final_output = {
                "run_metadata": {
                    "timestamp": timestamp,
                    "model": model_name,
                    "type": "local_worker"
                },
                "book_info": {"name": book_name},
                "extracted_quotes": []
            }

            page_files = sorted(list(b_folder.glob("page_*.json")))[:PAGES_LIMIT]
            print(f"  📖 Processing {book_name} with {model_name}...")

            for pf in page_files:
                try:
                    page_data = json.loads(pf.read_text())
                    content = page_data.get("content", "")
                    p_num = pf.stem.split('_')[1]

                    prompt = f"Extract literal nature quotes from: {content}. Return ONLY JSON."

                    response = requests.post(OLLAMA_URL, json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "format": "json"
                    })
                    
                    res_data = response.json()
                    ai_content = json.loads(res_data['message']['content'])

                    if ai_content.get("nature_found"):
                        for item in ai_content.get("items", []):
                            final_output["extracted_quotes"].append({
                                "quote": item.get("quote"),
                                "category": item.get("category"),
                                "page_number": p_num,
                                "model_id": model_name
                            })
                except Exception as e:
                    print(f"    ⚠️ Error on {pf.name}: {e}")

            # STEP 4: Save file with bookname_timestamp
            # Path: .../Educated_20260309_1930.json
            out_file = run_dir / f"{book_name}_{timestamp}.json"
            out_file.write_text(json.dumps(final_output, indent=4))
            books_processed += 1

if __name__ == "__main__":
    run_multi_model_benchmarking()