import json
from pathlib import Path
from datetime import datetime
# Import our unified configuration
from pipeline_config import OCR_LIBRARY

def run_stage_3_5_aggregator():
    """
    Scans Organized_Library_Source and creates a folder_metadata.json 
    for every book. This provides the 'Total Word Count' Stage 4 and 5 need.
    """
    print(f"🔄 Stage 3.5: Aggregating Metadata from {OCR_LIBRARY.name}...")
    
    # 1. Get all book folders that have OCR results
    book_folders = [d for d in OCR_LIBRARY.iterdir() if d.is_dir()]
    
    if not book_folders:
        print("❌ No book folders found. Check your OCR_LIBRARY path in config.")
        return

    for b_folder in book_folders:
        page_files = list(b_folder.glob("page_*.json"))
        
        if not page_files:
            print(f"  ⚠️ Skipping {b_folder.name}: No page JSONs found.")
            continue
            
        total_word_count = 0
        pages_processed = []
        
        # 2. Sum up the words across all transcribed pages
        for pf in page_files:
            try:
                page_data = json.loads(pf.read_text())
                content = page_data.get("content", "")
                
                # Count words (simple split)
                words = len(content.split())
                total_word_count += words
                
                # Track page numbers for the range
                p_num = page_data.get("page_number")
                if p_num is not None:
                    pages_processed.append(int(p_num))
            except Exception as e:
                print(f"    ❌ Error reading {pf.name}: {e}")

        # 3. Create the metadata payload
        metadata = {
            "book_name": b_folder.name,
            "total_pages_captured": len(page_files),
            "page_range": f"{min(pages_processed) if pages_processed else 0} - {max(pages_processed) if pages_processed else 0}",
            "total_word_count": total_word_count,
            "last_organized": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pipeline_status": "Ready for Stage 4 Extraction"
        }

        # 4. Save inside the book's folder
        meta_path = b_folder / "folder_metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=4))
        
        print(f"  ✅ {b_folder.name}: {total_word_count} words across {len(page_files)} pages.")

if __name__ == "__main__":
    run_stage_3_5_aggregator()