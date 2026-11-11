"""Hermes Mission Control: safe planning plus local-first observability."""
from __future__ import annotations
import json, os, time, uuid
from pathlib import Path
from typing import Any
try:
    from tools.registry import tool_error, tool_result
except ImportError:
    def tool_result(value): return json.dumps(value)
    def tool_error(message, **extra): return json.dumps({"success": False, "error": message, **extra})

MAX = 100

def _state_dir() -> Path:
    path = Path(os.environ.get("HERMES_MISSION_CONTROL_DIR", Path.home() / ".hermes" / "mission-control"))
    path.mkdir(parents=True, exist_ok=True)
    return path

def _read(name: str, default):
    try: return json.loads((_state_dir() / name).read_text())
    except (OSError, ValueError): return default

def _write(name: str, value):
    target = _state_dir() / name
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, indent=2))
    tmp.replace(target)

def _handle_plan(args: dict, **kwargs: Any) -> str:
    del kwargs
    goal = args.get("goal")
    if not isinstance(goal, str) or not goal.strip(): return tool_error("goal must be a non-empty string")
    steps = args.get("steps", [])
    if not isinstance(steps, list) or not 1 <= len(steps) <= 12 or not all(isinstance(s, str) and s.strip() for s in steps):
        return tool_error("steps must contain 1-12 non-empty strings")
    plan = {"id": uuid.uuid4().hex[:10], "goal": goal.strip(), "steps": [{"title": s.strip(), "status": "pending"} for s in steps], "created_at": time.time(), "status": "active"}
    plans = _read("plans.json", [])
    plans.insert(0, plan); _write("plans.json", plans[:MAX])
    return tool_result({"success": True, "plan": plan, "next": "Work through the steps in order and update the user as milestones complete."})

def _handle_status(args: dict, **kwargs: Any) -> str:
    del args, kwargs
    plans = _read("plans.json", [])
    events = _read("events.json", [])
    return tool_result({"success": True, "active_plans": [p for p in plans if p.get("status") == "active"], "recent_events": events[-20:]})

def register(ctx: Any) -> None:
    ctx.register_tool(name="mission_plan", toolset="mission_control", schema={"description": "Create a visible, auditable execution plan for a multi-step task. Use before starting complex work.", "parameters": {"type": "object", "properties": {"goal": {"type": "string", "description": "The outcome to achieve."}, "steps": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 12, "description": "Ordered, concrete steps."}}, "required": ["goal", "steps"], "additionalProperties": False}}, handler=_handle_plan, description="Create an auditable mission plan.")
    ctx.register_tool(name="mission_status", toolset="mission_control", schema={"description": "Show active mission plans and recent tool-call telemetry from Mission Control.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}, handler=_handle_status, description="Show mission progress and telemetry.")
    def on_tool_call(tool_name, params, result):
        events = _read("events.json", [])
        ok = True
        try: ok = json.loads(result).get("success", True) is not False
        except (TypeError, ValueError): pass
        events.append({"tool": str(tool_name), "ok": ok, "timestamp": time.time(), "param_keys": sorted(params.keys()) if isinstance(params, dict) else []})
        _write("events.json", events[-500:])
    ctx.register_hook("post_tool_call", on_tool_call)
