import os
import json
from datetime import datetime
from pathlib import Path

def log_video_event(video_url, status, message=None):
    """Log a video processing event to logs/video_log.json as a JSON object per line."""
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "video_log.json"
    print(f"[LOGGER] Called with url={video_url}, status={status}, message={message}")
    print(f"[LOGGER] Writing to: {log_file.resolve()}")
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "video_url": video_url,
        "status": status,
    }
    if message:
        log_entry["message"] = message
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    print("Testing logger...")
    log_video_event("test_url", "test_status", "test_message")
    print("Check if logs/video_log.json was created")