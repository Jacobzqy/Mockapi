import pytest

from mock_platform import Clock, InMemoryStateStore, ToolContext, ToolRegistry, default_state_factory
from mock_platform.services import register_admin_tools, register_contacts_tools, register_memo_tools, register_messaging_tools


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    register_contacts_tools(registry)
    register_messaging_tools(registry)
    register_admin_tools(registry)
    register_memo_tools(registry)
    return registry


def build_ctx(session: str = "memo-session") -> tuple[ToolRegistry, ToolContext]:
    registry = build_registry()
    clock = Clock()
    state_store = InMemoryStateStore(default_state_factory)
    ctx = ToolContext(user_id=session, trace_id="trace-" + session, clock=clock, state_store=state_store)
    return registry, ctx


def test_reset_loads_memo_seed() -> None:
    registry, ctx = build_ctx("m1")
    reset = registry.call("admin.reset", {}, ctx)
    assert reset.ok
    memos = registry.call("memo.list_memos", {}, ctx)
    assert memos.ok
    ids = [m["memo_id"] for m in memos.data["memos"]]
    assert "decision" in ids


def test_search_and_get_memo() -> None:
    registry, ctx = build_ctx("m2")
    search = registry.call("memo.search", {"title": "Decision"}, ctx)
    assert search.ok
    assert any(m["memo_id"] == "decision" for m in search.data["memos"])

    memo = registry.call("memo.get_memo", {"memo_id": "decision"}, ctx)
    assert memo.ok
    assert "Casey is the successful candidate" in memo.data["memo"]["content"]


def test_snapshot_restore_memos() -> None:
    registry, ctx = build_ctx("m3")
    state = ctx.state_store.get(ctx.session)
    state["memos"]["extra"] = {
        "memo_id": "extra",
        "title": "Extra",
        "content": "Temp content",
        "created_at": ctx.now_ms,
        "updated_at": ctx.now_ms,
    }
    snap = ctx.state_store.snapshot(ctx.session)

    state["memos"].pop("decision")
    ctx.state_store.restore(ctx.session, snap)
    restored = ctx.state_store.get(ctx.session)
    assert "decision" in restored["memos"]
    assert "extra" in restored["memos"]


def test_messaging_with_memo_content() -> None:
    registry, ctx = build_ctx("m4")
    memo = registry.call("memo.get_memo", {"memo_id": "decision"}, ctx)
    text = memo.data["memo"]["content"]
    send = registry.call(
        "messaging.send_text",
        {"to": {"type": "contact_id", "value": "anders"}, "text": text, "client_msg_id": "memo-msg"},
        ctx,
    )
    assert send.ok
    ctx.clock.advance(600)
    delivered = registry.call("messaging.get_message", {"message_id": send.data["message_id"]}, ctx)
    assert delivered.data["message"]["status"] == "delivered"
