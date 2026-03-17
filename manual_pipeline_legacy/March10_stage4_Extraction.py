import json
import os
import re
from pathlib import Path
from openai import OpenAI
from datetime import datetime
from pipeline_config import OCR_LIBRARY, CURRENT_MODEL, CURRENT_TOPIC, get_model_gold_path

def parse_json_response(raw_content):
    """
    Small fallback parser for models that return:
    - <think>...</think> before JSON
    - ```json ... ``` code fences
    - extra text around the JSON object
    """
    if not raw_content:
        raise ValueError("Empty model response")

    text = raw_content.strip()

    # Remove DeepSeek/Ollama reasoning tags if present
    if "<think>" in text and "</think>" in text:
        text = text.split("</think>")[-1].strip()

    # Remove markdown code fences
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    # First try: direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract first JSON object from the text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError(f"Could not parse JSON response: {text[:300]}")

def run_model_specific_stage_4():
    # --- AUTOMATIC ROUTING ---
    model_lower = CURRENT_MODEL.lower()

    if ":" in CURRENT_MODEL or "llama" in model_lower or "mistral" in model_lower or "gemma" in model_lower:
        local_url = "http://127.0.0.1:11434/v1"
        print(f"🤖 ROUTING: Ollama Local API ({local_url}) for {CURRENT_MODEL}")
        client = OpenAI(base_url=local_url, api_key="ollama")

    elif "deepseek" in model_lower:
        deepseek_url = "https://api.deepseek.com/v1"
        print(f"🌊 ROUTING: DeepSeek Cloud API ({deepseek_url}) for {CURRENT_MODEL}")
        client = OpenAI(
            base_url=deepseek_url,
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )

    else:
        print(f"☁️  ROUTING: OpenAI Cloud for {CURRENT_MODEL}")
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print(f"🚀 Extraction Started: Topic={CURRENT_TOPIC}")

    for book_folder in [d for d in OCR_LIBRARY.iterdir() if d.is_dir()]:
        book_id = book_folder.name
        meta_file = book_folder / "folder_metadata.json"
        if not meta_file.exists():
            continue
        total_words = json.loads(meta_file.read_text()).get("total_word_count", 0)

        book_dest = get_model_gold_path(book_id)
        final_file = book_dest / f"{book_id}_{CURRENT_MODEL.replace(':', '_')}_FINAL.json"

        # ... (Existing deduplication logic) ...

        new_quotes = []
        page_files = sorted(list(book_folder.glob("page_*.json")))

        for pf in page_files:
            try:
                page_data = json.loads(pf.read_text())
                content = page_data.get("content", "")
                if not content:
                    continue

                prompt = (
                    f"Analyze this text: '{content}'. "
                    f"Find quotes about {CURRENT_TOPIC}. "
                    f"Return ONLY a JSON object with this structure: "
                    f"{{\"found\": true, \"items\": [{{ \"quote\": \"text\", \"relevancy\": 2 }}]}}. "
                    f"If nothing is found, return "
                    f"{{\"found\": false, \"items\": []}}"
                )

                request_kwargs = {
                    "model": CURRENT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                }

                if "o4" not in model_lower:
                    request_kwargs["response_format"] = {"type": "json_object"}

                res = client.chat.completions.create(**request_kwargs)

                raw_content = res.choices[0].message.content or ""
                ai_res = parse_json_response(raw_content)

                if ai_res.get("found"):
                    for item in ai_res.get("items", []):
                        item.update({
                            "page_id": pf.stem,
                            "model": CURRENT_MODEL,
                            "timestamp": datetime.now().isoformat()
                        })
                        new_quotes.append(item)
            except Exception as e:
                print(f"    ⚠️ Skipping {pf.name}: {e}")
                continue

        if new_quotes:
            master = {"book_id": book_id, "model": CURRENT_MODEL, "total_words": total_words, "quotes": []}
            if final_file.exists():
                try:
                    master = json.loads(final_file.read_text())
                except:
                    pass

            master["quotes"].extend(new_quotes)
            master["total_quotes"] = len(master["quotes"])
            final_file.write_text(json.dumps(master, indent=4))
            print(f"  ✅ {book_id}: Added {len(new_quotes)} quotes.")

if __name__ == "__main__":
    run_model_specific_stage_4()