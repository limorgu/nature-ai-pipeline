import os
import json
import shutil
import re
from pathlib import Path

RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
AUDIT_INPUT_ROOT = RESULTS_BASE / "openai_audits"

def get_file_version(file_path: Path) -> str:
    try:
        data = json.loads(file_path.read_text())
        v = data.get("audit_lineage", {}).get("version") or data.get("run_metadata", {}).get("version")
        return f"V{v.strip('V')}" if v else "V1"
    except: return "V1"

def run_stage_0_validation_and_organize():
    print(f"--- 🔍 Stage 0: In-Place Results Organization ---")
    AUDIT_INPUT_ROOT.mkdir(parents=True, exist_ok=True)
    loose_files = [f for f in AUDIT_INPUT_ROOT.iterdir() if f.is_file() and not f.name.startswith(".")]
    
    if not loose_files:
        print("✨ Workspace is already organized.")
        return

    for f in loose_files:
        try:
            book_match = re.split(r'_(nature|audit|WISE|S4|S5)', f.name)[0]
            version_tag = get_file_version(f)
            stage_tag = f"S5_{version_tag}" if ("WISE_AUDIT" in f.name or "S5" in f.name) else f"S4_{version_tag}"

            target_dir = AUDIT_INPUT_ROOT / book_match / stage_tag
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(target_dir / f.name))
        except Exception as e:
            print(f"  ⚠️ Error organizing {f.name}: {e}")
    print(f"✅ Organization Complete.")