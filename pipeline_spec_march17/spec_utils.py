import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union


ROOT = Path(__file__).resolve().parent


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Union[Dict, List]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def latest_run_root() -> Path:
    latest_path = ROOT / "LATEST_RUN.txt"
    if not latest_path.exists():
        raise FileNotFoundError("LATEST_RUN.txt not found. Run Stage 0 first.")
    lines = latest_path.read_text(encoding="utf-8").strip().splitlines()
    if len(lines) < 2:
        raise ValueError("LATEST_RUN.txt is malformed.")
    return Path(lines[1].strip())


def update_stage_status(run_root: Path, stage_id: str, status: str, extra: Optional[Dict] = None) -> None:
    run_log_path = run_root / "run_log.json"
    run_log = load_json(run_log_path)
    for stage in run_log["stages"]:
        if stage["stage_id"] == stage_id:
            stage["status"] = status
            stage["updated_at"] = datetime.now().isoformat()
            if extra:
                stage.update(extra)
            break
    write_json(run_log_path, run_log)


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "_", lowered)
    return lowered.strip("_") or "unknown"
