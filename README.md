# Hermes Mission Control

Mission Control turns complex Hermes runs into intentional, observable work. It adds two model-callable tools and a live Hermes dashboard:

- `mission_plan` creates a structured, visible plan before a multi-step task begins.
- `mission_status` returns active plans and recent telemetry.
- A `post_tool_call` hook records tool names, success/failure, timestamps, and parameter keys locally—never parameter values.
- The dashboard refreshes automatically and surfaces plan count, event count, failures, and active plans.

## Install

```bash
mkdir -p ~/.hermes/plugins
cp -r . ~/.hermes/plugins/hermes-mission-control
hermes plugins enable hermes-mission-control
```

Restart Hermes or rescan the dashboard. Set `HERMES_MISSION_CONTROL_DIR` to choose another local state directory. The default is `~/.hermes/mission-control/`.

## Why it matters

Agents are most useful when people can understand what they are doing. Mission Control adds a small, composable layer of intent and observability without replacing Hermes memory, routing, model choice, or terminal execution. It is offline by default, dependency-free, and deliberately redacts tool arguments.

## Development

```bash
python -m unittest discover -s tests -v
```

## Safety

Mission Control is read/write only to its own state directory. The dashboard API is read-only. No network calls, credentials, subprocesses, background workers, or hidden model calls are used.
