"""
Write each message to   media/conversations/<assistant-id>/<message-id>.json
Useful if you want a file-system backup or to feed Retrieval later.
"""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent.parent / 'media' / 'conversations'
BASE.mkdir(parents=True, exist_ok=True)

def save_message_json(msg):
    assistant_dir = BASE / str(msg.assistant_id)
    assistant_dir.mkdir(exist_ok=True)
    fp = assistant_dir / f"{msg.id}.json"
    fp.write_text(json.dumps({
        "id": str(msg.id),
        "role": msg.role,
        "content": msg.content,
        "created_at": msg.created_at.isoformat()
    }, indent=2))
