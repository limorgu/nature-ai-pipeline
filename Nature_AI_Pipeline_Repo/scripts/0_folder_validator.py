import os
from pathlib import Path

# ---------------------------
# Config
# ---------------------------
SOURCE_BOOKS_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_books_test")

def run_stage_0_validation():
    print(f"--- 🔍 Stage 0: Folder Format Validation ---")
    
    if not SOURCE_BOOKS_ROOT.exists():
        print(f"❌ Error: Source directory not found at {SOURCE_BOOKS_ROOT}")
        return

    folders = [d for d in SOURCE_BOOKS_ROOT.iterdir() if d.is_dir()]
    
    passed = []
    failed = []

    for f in folders:
        # Check for the underscore separator
        parts = f.name.split("_")
        
        # Validation Rules:
        # 1. Must have at least one underscore
        # 2. Must not have spaces (for cleaner CLI/Path handling)
        if len(parts) >= 2 and " " not in f.name:
            passed.append(f.name)
        else:
            reason = ""
            if len(parts) < 2: reason += "[Missing underscore] "
            if " " in f.name: reason += "[Contains spaces] "
            failed.append((f.name, reason))

    # --- Report ---
    if passed:
        print(f"\n✅ {len(passed)} Folders Ready:")
        for name in passed:
            print(f"  • {name}")

    if failed:
        print(f"\n⚠️ {len(failed)} Folders Need Attention:")
        for name, reason in failed:
            print(f"  • {name} <--- {reason}")
        print("\n💡 Suggested Fix: Rename to 'BookTitle_Author' (no spaces).")
    else:
        print("\n🚀 All folders are perfectly formatted for the pipeline!")

if __name__ == "__main__":
    run_stage_0_validation()