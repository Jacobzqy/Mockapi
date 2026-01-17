# Architecture notes

- Single entry point: `ToolRegistry.call(tool_name, args, ctx)` returning `ToolResult`.
- Determinism: `Clock` (logical time) and `InMemoryStateStore` (per-session, snapshot/restore).
- Async behavior: scheduled events (e.g., message delivery) run when `Clock.advance(ms)` is called.
- Data models: ToolContext(user_id, trace_id, now_ms), ToolResult(ok, data, error, meta), Contact/Message/Conversation.
- Namespaces: `contacts.*`, `messaging.*`, `admin.*`
- Seed data: Anders contact (`contact_id="anders"`, `e164="+15550001111"`). `admin.reset` restores seed state.
