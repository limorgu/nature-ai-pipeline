import os
from pathlib import Path

# --- 1. GLOBAL PATHS ---
# Root directory for all your research data
BASE_PATH = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test")

# Master folder containing the original JPG/PNG photos
SOURCE_IMAGES = BASE_PATH / "Feb_books_test"

# Main folder for intermediate outputs and OCR
FEBRUARY_RESULTS = BASE_PATH / "Feb_results"

# --- 2. DYNAMIC DIRECTORIES ---
# Stage 2-3 Output: Where the raw transcribed page JSONs live
OCR_LIBRARY = FEBRUARY_RESULTS / "Organized_Library_Source"

# Stage 4 Output: The "Source of Truth" for your categorized results
GOLD_LIBRARY = BASE_PATH / "Gold_Standardized"

# Stage 5 Output: Where CSV logs and density reports go
AUDIT_REPORTS = BASE_PATH / "Library_Audits"

# Stage 2-3 Progress Tracking: The high-level % completion report
METADATA_LOG = FEBRUARY_RESULTS / "library_final_metadata.json"

# --- 3. MODEL & TOPIC SETTINGS ---
# 🔄 CHANGE THESE TWO LINES to redirect the entire pipeline's logic
CURRENT_MODEL = "llama3.1:8b"  # Options: "gpt-4o-mini", "o4", "deepseek"
CURRENT_TOPIC = "nature"        # Options: "nature", "psychology", "biology"

# Extraction Thresholds
WORD_THRESHOLD = 200  # Minimum words to consider a page valid
MIN_RELEVANCY = 1      # Minimum score on the 0-2 scale to keep a quote
# --- 4. MODEL REGISTRY ---
# One name -> one routing rule
#
# provider:
#   - "openai"   => OpenAI cloud
#   - "deepseek" => DeepSeek cloud
#   - "ollama"   => Local Ollama server
#
# json_mode:
#   True  => send response_format={"type": "json_object"}
#   False => rely on prompt-only JSON instruction
#
# strip_think_tags:
#   True => useful for some reasoning/local models that may emit <think>...</think>

MODEL_REGISTRY = {
    # OpenAI cloud models
    "gpt-4o-mini": {
        "provider": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "json_mode": True,
        "strip_think_tags": False,
        "temperature": 0
    },
    "gpt-4o": {
        "provider": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "json_mode": True,
        "strip_think_tags": False,
        "temperature": 0
    },
    "o4-mini": {
        "provider": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "json_mode": False,
        "strip_think_tags": False,
        "temperature": 0
    },

    # DeepSeek cloud models
    # DeepSeek supports OpenAI-compatible usage through base_url. :contentReference[oaicite:1]{index=1}
    "deepseek-chat": {
        "provider": "deepseek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
        "json_mode": True,
        "strip_think_tags": False,
        "temperature": 0
    },
    "deepseek-reasoner": {
        "provider": "deepseek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
        "json_mode": True,
        "strip_think_tags": False,
        "temperature": 0
    },

    # Local Ollama models
    # Ollama supports OpenAI-compatible APIs and structured outputs via response_format. :contentReference[oaicite:2]{index=2}
    "deepseek-r1:8b": {
        "provider": "ollama",
        "api_key_env": None,
        "base_url": "http://127.0.0.1:11434/v1",
        "json_mode": True,
        "strip_think_tags": True,
        "temperature": 0
    },
    "llama3.1:8b": {
        "provider": "ollama",
        "api_key_env": None,
        "base_url": "http://127.0.0.1:11434/v1",
        "json_mode": True,
        "strip_think_tags": False,
        "temperature": 0
    },
    "gemma3:12b": {
        "provider": "ollama",
        "api_key_env": None,
        "base_url": "http://127.0.0.1:11434/v1",
        "json_mode": True,
        "strip_think_tags": False,
        "temperature": 0
    },
}

def get_model_settings(model_name: str) -> dict:
    """
    Return routing/settings for the selected model.
    Falls back to a reasonable default based on the name.
    """
    if model_name in MODEL_REGISTRY:
        return MODEL_REGISTRY[model_name]

    name = model_name.lower()

    # Fallback rules for models not explicitly listed
    if "deepseek" in name and ":" in model_name:
        # likely local Ollama tag such as deepseek-r1:8b
        return {
            "provider": "ollama",
            "api_key_env": None,
            "base_url": "http://127.0.0.1:11434/v1",
            "json_mode": True,
            "strip_think_tags": True,
            "temperature": 0
        }

    if "llama" in name or "gemma" in name or "mistral" in name:
        return {
            "provider": "ollama",
            "api_key_env": None,
            "base_url": "http://127.0.0.1:11434/v1",
            "json_mode": True,
            "strip_think_tags": False,
            "temperature": 0
        }

    if "deepseek" in name:
        return {
            "provider": "deepseek",
            "api_key_env": "DEEPSEEK_API_KEY",
            "base_url": "https://api.deepseek.com/v1",
            "json_mode": True,
            "strip_think_tags": False,
            "temperature": 0
        }

    return {
        "provider": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "json_mode": True,
        "strip_think_tags": False,
        "temperature": 0
    }

# --- 5. SHARED UTILS ---

def get_model_gold_path(book_id):
    """
    Creates a clean hierarchy: 
    Gold_Standardized / nature / gpt-4o-mini / AutismInHeels_JeniferCookOtoole
    """
    p = GOLD_LIBRARY / CURRENT_TOPIC / CURRENT_MODEL / book_id
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_audit_run_path(timestamp):
    """Creates: Library_Audits / Audit_nature_20260310_1345"""
    p = AUDIT_REPORTS / f"Audit_{CURRENT_TOPIC}_{timestamp}"
    p.mkdir(parents=True, exist_ok=True)
    return p

def ensure_dirs():
    """Initializes the workspace structure."""
    dirs = [
        OCR_LIBRARY,
        GOLD_LIBRARY,
        AUDIT_REPORTS,
        GOLD_LIBRARY / CURRENT_TOPIC / CURRENT_MODEL.replace(":", "_")
    ]
    for p in dirs:
        p.mkdir(parents=True, exist_ok=True)

def validate_model_config():
    """
    Fails early if the chosen model needs an API key that is missing.
    """
    settings = get_model_settings(CURRENT_MODEL)
    api_key_env = settings.get("api_key_env")

    if api_key_env:
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(
                f"Missing environment variable: {api_key_env} "
                f"for model '{CURRENT_MODEL}'"
            )

if __name__ == "__main__":
    ensure_dirs()
    validate_model_config()

    settings = get_model_settings(CURRENT_MODEL)

    print("--- 🛠️  PIPELINE CONFIGURATION ---")
    print(f"📍 Base Path:      {BASE_PATH}")
    print(f"🏷️  Active Topic:   {CURRENT_TOPIC.upper()}")
    print(f"🤖 Active Model:    {CURRENT_MODEL}")
    print(f"🔀 Provider:        {settings['provider']}")
    print(f"🌐 Base URL:        {settings['base_url'] or 'OpenAI default'}")
    print("✅ Environment verified and folders ready.")