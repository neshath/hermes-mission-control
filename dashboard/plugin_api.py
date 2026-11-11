"""Read-only local Mission Control dashboard API."""
import json, os
from pathlib import Path
from fastapi import APIRouter
router = APIRouter()
def _load(name, default):
    try: return json.loads((Path(os.environ.get("HERMES_MISSION_CONTROL_DIR", Path.home()/".hermes"/"mission-control"))/name).read_text())
    except (OSError, ValueError): return default
@router.get("/snapshot")
async def snapshot():
    plans = _load("plans.json", []); events = _load("events.json", [])
    return {"plans": plans[:20], "events": events[-50:], "counts": {"plans": len(plans), "events": len(events), "failures": sum(1 for e in events if not e.get("ok", True))}}
