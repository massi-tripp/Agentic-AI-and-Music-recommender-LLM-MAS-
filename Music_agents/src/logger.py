# src/logger.py
import json, os
from pathlib import Path

class RunLogger:
    def __init__(self, run_dir: str):
        self.dir = Path(run_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.fp = open(self.dir / "messages.jsonl", "a", encoding="utf-8")
    def log_msg(self, obj: dict):
        # non filtrare! scrivi qualunque record
        self.fp.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self.fp.flush()
    def close(self):
        try:
            self.fp.close()
        except Exception:
            pass
