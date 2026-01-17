# Mock Platform (in-process)

Deterministic mock app APIs for large-scale agent task evaluation. Everything runs in-process with a single `ToolRegistry` entry point, a logical `Clock` (no real sleeps), snapshot-capable `InMemoryStateStore`, and tools for contacts, messaging, and admin controls.

## Requirements

- Python 3.11+
- No network calls; all state is local and JSON-serializable.

## Install

```bash
python -m pip install -e .
```

## Run the example

```bash
python examples/message_sending.py
```

The script sends “Let us meet up at 3 pm today” to Anders, advances the logical clock by 500ms, and reads back the delivered message.

## Core concepts

- `ToolRegistry.call(tool_name, args, ctx) -> ToolResult`: single entry point with uniform error handling.
- `ToolContext`: `user_id`, `trace_id`, `now_ms` (via the logical `Clock`), plus shared `InMemoryStateStore` for session isolation.
- `Clock`: `now_ms()` and `advance(ms)`; advancing triggers scheduled events (e.g., message delivery).
- `InMemoryStateStore`: per-session state with `snapshot()` and `restore()` using deep copies.
- Seed data: one contact `Anders` (`contact_id="anders"`, `e164="+15550001111"`); `admin.reset` restores seeds per session.
- Tools:
  - `contacts.search`, `contacts.get`
  - `messaging.send_text`, `messaging.get_message`, `messaging.list_messages`
  - `admin.reset`, `admin.set_delivery`, `admin.set_rule` (reserved for fault injection)

## Testing

Tests use `pytest`:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```
