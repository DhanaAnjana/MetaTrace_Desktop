import json
import hashlib
from datetime import datetime
from pathlib import Path


LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
LOGS_FILE = LOGS_DIR / "metatrace.log"


def log_action(action, files=None, error=None):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "files": files or [],
        "error": error
    }
    
    with open(LOGS_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry


def get_all_logs():
    logs = []
    
    if not LOGS_FILE.exists():
        return logs
    
    with open(LOGS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    
    return logs


def export_logs(output_path):
    logs = get_all_logs()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2)
    
    return {"success": True, "message": f"Logs exported to {output_path}"}


def calculate_logs_hash():
    if not LOGS_FILE.exists():
        return hashlib.sha256(b"").hexdigest()
    
    sha256_hash = hashlib.sha256()
    with open(LOGS_FILE, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def get_logs_summary():
    logs = get_all_logs()
    
    summary = {
        "total_entries": len(logs),
        "first_entry": logs[0]["timestamp"] if logs else None,
        "last_entry": logs[-1]["timestamp"] if logs else None,
        "sha256_hash": calculate_logs_hash()
    }
    
    return summary
