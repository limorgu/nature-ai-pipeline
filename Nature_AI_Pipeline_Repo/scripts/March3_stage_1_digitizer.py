import os
import json
import io
import base64
import random
from pathlib import Path
from typing import Any, Dict, Tuple
from PIL import Image
from openai import OpenAI

# ---------------------------
# 1. Configuration
# ---------------------------
ROOT_DIR_DEFAULT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_books_test")

# ✅ TARGET FOLDER: This is your Master Source of Truth
OUTPUT_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results/Organized_Library_Source")

MODEL = "gpt-4o-mini"
WORD_THRESHOLD = 200
PAGES_PER_ITERATION = 100

# 🧪 TEST OPTION
TEST_MODE = True  # Set to True to only process 3 pages for testing
TEST_LIMIT = 100

# ---------------------------
# Helpers
# ---------------------------
def image_to_data_url(path: Path) -> str:
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def parse_book_author_from_folder(book_folder: Path) -> Tuple[str, str]:
    name_parts = book_folder.name.split("_")
    if len(name_parts) >= 2:
        author = name_parts[-1].strip()
        title = " ".join(name_parts[:-1]).replace("_", " ").strip()
        return title or book_folder.name, author
    return book_folder.name, "Unknown"

def get_globally_processed_images(output_base: Path, book_title: str) -> set:
    processed_images = set()
    for json_file in output_base.rglob("page_*.json"):
        try:
            data = json.loads(json_file.read_text())
            if data.get("book_name") == book_title:
                source_img = data.get("source_image")
                if source_img: processed_images.add(source_img)
        except: continue
    return processed_images

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
# Main Runner
# ---------------------------
def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return

    client = OpenAI()
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    
    # 1. Select Book
    book_folders = [p for p in ROOT_DIR_DEFAULT.iterdir() if p.is_dir()]
    if not book_folders: return

    target_book_dir = random.choice(book_folders)
    book_title, author_name = parse_book_author_from_folder(target_book_dir)
    
    print(f"--- 🚀 Session Started {'(TEST MODE)' if TEST_MODE else ''} ---")
    print(f"📖 Target Book: {book_title}")

    # 2. Check for duplicates
    already_done = get_globally_processed_images(OUTPUT_BASE, book_title)
    
    # 3. Filter Images
    all_imgs = sorted([p for p in target_book_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])
    images_to_scan = [img for img in all_imgs if img.name not in already_done]
    
    if not images_to_scan:
        print("✅ Already processed!")
        return

    # 4. Flattened Folder Logic
    # This creates: .../Organized_Library_Source/Title_Author/
    book_folder_name = f"{book_title.replace(' ', '')}_{author_name.replace(' ', '')}"
    book_output_dir = OUTPUT_BASE / book_folder_name
    book_output_dir.mkdir(parents=True, exist_ok=True)

    # Apply Test Limit if enabled
    if TEST_MODE:
        images_to_scan = images_to_scan[:TEST_LIMIT]
        print(f"🧪 Test Mode Active: Only processing first {TEST_LIMIT} pages.")

    # 5. Extraction
    for img_path in images_to_scan:
        print(f"  📸 Scanning {img_path.name}...")
        raw_data = extract_page_data(client, img_path)
        
        content = raw_data.get("content") or ""
        words = content.split()
        
        if len(words) >= WORD_THRESHOLD:
            page_json = {
                "book_name": book_title,
                "book_author": author_name,
                "page_number": raw_data.get("page_number"),
                "content": content,
                "source_image": img_path.name
            }
            label = raw_data.get("page_number") or f"file_{img_path.stem}"
            (book_output_dir / f"page_{label}.json").write_text(json.dumps(page_json, indent=4))
        else:
            print(f"  ⏳ Skipping {img_path.name}: Low word count.")

    print(f"\n🏁 Finished. Check results in: {book_output_dir}")

def run_stage_1_digitizer():
    # Wrap your existing logic here
    main() 

if __name__ == "__main__":
    run_stage_1_digitizer()