import os
import shutil
from pathlib import Path
from pipeline_config import OCR_LIBRARY, GOLD_LIBRARY, BASE_PATH, CURRENT_TOPIC, CURRENT_MODEL

def run_stage_0_sanitization():
    print(f"--- 🧹 Stage 0: Pipeline Sanitization & Safety Check ---")
    
    # 1. Clean System Junk (Prevents crashes during JSON loading)
    junk_patterns = [".DS_Store", "Thumbs.db", "__MACOSX"]
    print("  🗑️  Cleaning system junk files...")
    for pattern in junk_patterns:
        for junk in BASE_PATH.rglob(pattern):
            try:
                junk.unlink()
            except: pass

    # 2. Remove Empty Folders in Gold Library
    # These are the specific culprits that caused your Stage 5 IndexError
    print("  📁 Checking for empty book folders in Gold Library...")
    target_gold = GOLD_LIBRARY / CURRENT_TOPIC / CURRENT_MODEL
    if target_gold.exists():
        for book_dir in target_gold.iterdir():
            if book_dir.is_dir():
                # Check if it contains any JSON files
                jsons = list(book_dir.glob("*.json"))
                if not jsons:
                    print(f"    ⚠️ Removing empty folder: {book_dir.name}")
                    shutil.rmtree(book_dir)

    # 3. Verify Folder Lineage
    # Ensures Organized_Library_Source is mapped correctly
    if not OCR_LIBRARY.exists():
        print(f"  🚨 WARNING: OCR_LIBRARY not found at {OCR_LIBRARY}")
    else:
        book_count = len([d for d in OCR_LIBRARY.iterdir() if d.is_dir()])
        print(f"  ✅ OCR Library Verified: {book_count} books ready for analysis.")

    # 4. Backup Critical Progress Log
    meta_log = BASE_PATH / "Feb_results" / "library_final_metadata.json"
    if meta_log.exists():
        backup = meta_log.with_suffix(".json.bak")
        shutil.copy2(meta_log, backup)
        print(f"  💾 Progress backup created: {backup.name}")

    print(f"✅ Stage 0 Complete: The environment is clean and stable.")

if __name__ == "__main__":
    run_stage_0_sanitization()