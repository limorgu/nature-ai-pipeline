import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_run_name(now: datetime) -> str:
    return f"RUN_{now.strftime('%Y%m%d_%H%M')}"


def initialize_workspace(project_config_path: Path, domain_config_path: Path) -> Path:
    project_config = load_json(project_config_path)
    domain_config = load_json(domain_config_path)

    storage_root_value = project_config.get("storage_root", "__PROJECT_ROOT__")
    if storage_root_value == "__PROJECT_ROOT__":
        storage_root = project_config_path.resolve().parent
    else:
        storage_root = Path(storage_root_value)
    runs_root = storage_root / project_config.get("runs_dirname", "Runs")
    runs_root.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    run_name = build_run_name(now)
    run_root = runs_root / run_name
    run_root.mkdir(parents=True, exist_ok=True)

    stage_names = project_config["stage_names"]
    stage_folders = []
    for stage_id in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
        folder_name = f"{stage_id}_{stage_names[stage_id]}"
        stage_path = run_root / folder_name
        stage_path.mkdir(parents=True, exist_ok=True)
        stage_folders.append(
            {
                "stage_id": stage_id,
                "folder_name": folder_name,
                "path": str(stage_path),
                "status": "pending"
            }
        )

    run_log = {
        "run_id": run_name,
        "project_name": project_config["project_name"],
        "domain": domain_config["domain"],
        "binary_label": domain_config["binary_label"],
        "taxonomy": domain_config["taxonomy"],
        "relationship_analysis": domain_config.get("relationship_analysis", False),
        "extraction_strategy": domain_config.get("extraction_strategy", "sentence"),
        "raw_sources_root": project_config["raw_sources_root"],
        "run_root": str(run_root),
        "created_at": now.isoformat(),
        "stages": stage_folders
    }

    run_log_path = run_root / "run_log.json"
    with run_log_path.open("w", encoding="utf-8") as handle:
        json.dump(run_log, handle, indent=2)

    latest_path = storage_root / "LATEST_RUN.txt"
    latest_path.write_text(f"{run_name}\n{run_root}\n", encoding="utf-8")

    return run_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 0 workspace initializer.")
    parser.add_argument(
        "--project-config",
        default=str(Path(__file__).resolve().parent / "project_config.json")
    )
    parser.add_argument(
        "--domain-config",
        default=str(Path(__file__).resolve().parent / "domain_config.json")
    )
    args = parser.parse_args()

    run_root = initialize_workspace(
        project_config_path=Path(args.project_config),
        domain_config_path=Path(args.domain_config)
    )
    print(json.dumps({"status": "ok", "run_root": str(run_root)}, indent=2))


if __name__ == "__main__":
    main()
