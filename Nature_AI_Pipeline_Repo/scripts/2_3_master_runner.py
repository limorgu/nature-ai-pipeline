import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from openai import OpenAI
import PIL.Image
import io
import base64

# 1. Unified Configuration - LOCKED
# ---------------------------
SOURCE_BOOKS_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_books_test")

# ✅ THIS IS THE FIX: Ensuring the path is INSIDE Feb_results
LIBRARY_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results/Organized_Library_Source")

# Ensure the parent folder exists so the script doesn't get confused
LIBRARY_ROOT.mkdir(parents=True, exist_ok=True)

LIBRARY_AUDITS_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Library_Audits")
FINAL_METADATA_PATH = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results/library_final_metadata.json")

MODEL = "gpt-4o-mini"
WORD_THRESHOLD = 200

# ---------------------------
# 2. Helpers (OCR & Path Parsing)
# ---------------------------
def compact_ranges(numbers: List[int]) -> str:
    if not numbers: return ""
    numbers = sorted(set(numbers))
    ranges = []
    start = numbers[0]
    for i in range(1, len(numbers) + 1):
        if i == len(numbers) or numbers[i] != numbers[i-1] + 1:
            end = numbers[i-1]
            ranges.append(f"{start}-{end}" if start != end else f"{start}")
            if i < len(numbers): start = numbers[i]
    return ", ".join(ranges)

def parse_folder_name(folder_name: str) -> Tuple[str, str]:
    parts = folder_name.split("_")
    if len(parts) >= 2:
        author = parts[-1].strip()
        title = " ".join(parts[:-1]).replace("_", " ").strip()
        return title, author
    return folder_name, "Unknown"

def image_to_data_url(path: Path) -> str:
    img = PIL.Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def extract_page_data(client: OpenAI, image_path: Path) -> Dict[str, Any]:
    prompt = "Transcribe ALL text verbatim. Return JSON: {'content': string, 'page_number': int/null}"
    try:
        data_url = image_to_data_url(image_path)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_url}}]}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except: return {"content": "", "page_number": None}

# ---------------------------
# 3. Logic: Stage 2 (The Auditor)
# ---------------------------
def run_audit_refresh():
    print(f"\n--- 🧹 Stage 2: Refreshing Metadata ---")
    audit_report = []
    all_json_files = list(LIBRARY_ROOT.rglob("page_*.json"))
    json_map = {}
    for pf in all_json_files:
        book_folder = pf.parent.name
        if book_folder not in json_map: json_map[book_folder] = []
        json_map[book_folder].append(pf)

    for s_folder in [d for d in SOURCE_BOOKS_ROOT.iterdir() if d.is_dir()]:
        title, author = parse_folder_name(s_folder.name)
        raw_images = [img for img in s_folder.iterdir() if img.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        
        book_jsons = json_map.get(s_folder.name) or json_map.get(s_folder.name.replace(" ", ""))
        if not book_jsons:
            for k in json_map.keys():
                if k.startswith(title.replace(" ", "")):
                    book_jsons = json_map[k]; break
        
        book_jsons = book_jsons or []
        found_pages = []
        for jf in book_jsons:
            try:
                p_num = json.loads(jf.read_text()).get("page_number")
                if p_num: found_pages.append(int(p_num))
            except: continue

        processed = len(book_jsons)
        total = len(raw_images)
        pct = (processed / total * 100) if total > 0 else 0
        
        audit_report.append({
            "book_name": title, "author": author,
            "completion_percentage": f"{pct:.1f}%",
            "pages_processed": processed, "total_images_in_source": total,
            "missing_count": total - processed,
            "sequence_gaps": compact_ranges(found_pages)
        })

    # Priority Sort
    audit_report.sort(key=lambda x: float(x['completion_percentage'].replace('%','')))
    FINAL_METADATA_PATH.write_text(json.dumps(audit_report, indent=4))
    print(f"✅ Metadata refreshed and prioritized.")

# ---------------------------
# 4. Logic: Stage 3 (The Iterative Filler)
# ---------------------------
def run_smart_fill():
    run_audit_refresh() # Always refresh before filling
    client = OpenAI()
    audit_data = json.loads(FINAL_METADATA_PATH.read_text())
    incomplete = [b for b in audit_data if b['completion_percentage'] != "100.0%"]

    if not incomplete:
        print("🎉 All books are 100% complete!")
        return

    print("\n--- 📑 Priority Queue (Lowest Progress First) ---")
    for i, b in enumerate(incomplete):
        print(f"[{i}] {b['book_name']} - {b['completion_percentage']} ({b['missing_count']} missing)")

    choice = input("\nSelect book number to process (or 'q'): ").strip()
    if choice.lower() == 'q': return

    selected = incomplete[int(choice)]
    # Match source folder
    target_folder = next((d for d in SOURCE_BOOKS_ROOT.iterdir() if d.is_dir() and d.name.replace(" ","").startswith(selected['book_name'].replace(" ",""))), None)
    
    if not target_folder:
        print(f"❌ Source not found for {selected['book_name']}")
        return

    book_output_dir = LIBRARY_ROOT / target_folder.name
    book_output_dir.mkdir(parents=True, exist_ok=True)

    # Deduplication
    processed_sources = {json.loads(jf.read_text()).get("source_image") for jf in book_output_dir.glob("page_*.json")}
    images_to_do = [img for img in sorted(target_folder.iterdir()) if img.suffix.lower() in ['.jpg', '.png', '.jpeg'] and img.name not in processed_sources]

    if not images_to_do:
        print("✅ No gaps found.")
        return

    print(f"🚀 Found {len(images_to_do)} gaps. How many to fill? (Number or 'all'): ")
    limit_input = input().strip().lower()
    limit = len(images_to_do) if limit_input == 'all' else int(limit_input or 5)

    for img in images_to_do[:limit]:
        print(f"  📸 Scanning {img.name}...")
        res = extract_page_data(client, img)
        res.update({"source_image": img.name, "book_name": selected['book_name'], "book_author": selected['author']})
        label = res.get("page_number") or f"file_{img.stem}"
        (book_output_dir / f"page_{label}.json").write_text(json.dumps(res, indent=4))

    print(f"\n✅ Batch complete. Run this script again to refresh and continue.")

if __name__ == "__main__":
    run_smart_fill()