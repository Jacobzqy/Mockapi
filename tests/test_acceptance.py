import pytest

from mock_platform import Clock, InMemoryStateStore, ToolContext, ToolRegistry, default_state_factory
from mock_platform.services import register_admin_tools, register_contacts_tools, register_messaging_tools


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    register_contacts_tools(registry)
    register_messaging_tools(registry)
    register_admin_tools(registry)
    return registry


def build_ctx(session: str = "s1") -> tuple[ToolRegistry, ToolContext]:
    registry = build_registry()
    clock = Clock()
    state_store = InMemoryStateStore(default_state_factory)
    ctx = ToolContext(user_id=session, trace_id="trace-" + session, clock=clock, state_store=state_store)
    return registry, ctx


def test_reset_then_search_anders() -> None:
    registry, ctx = build_ctx("u-reset")
    reset = registry.call("admin.reset", {}, ctx)
    assert reset.ok

    search = registry.call("contacts.search", {"q": "Anders"}, ctx)
    assert search.ok
    contacts = search.data["contacts"]
    assert any(c["contact_id"] == "anders" for c in contacts)


def test_send_and_deliver_sentence() -> None:
    registry, ctx = build_ctx("u-send")
    text = "Let us meet up at 3 pm today"

    send = registry.call(
        "messaging.send_text",
        {"to": {"type": "contact_id", "value": "anders"}, "text": text, "client_msg_id": "cli-1"},
        ctx,
    )
    assert send.ok
    message_id = send.data["message_id"]

    ctx.clock.advance(500)

    delivered = registry.call("messaging.get_message", {"message_id": message_id}, ctx)
    assert delivered.ok
    message = delivered.data["message"]
    assert message["status"] == "delivered"
    assert text in message["text"]
    assert message["to"]["value"] == "+15550001111"


def test_snapshot_restore_contacts() -> None:
    registry, ctx = build_ctx("u-snap")
    state = ctx.state_store.get(ctx.session)
    state["contacts"]["temp"] = {"contact_id": "temp", "name": "Temp", "phones": [{"e164": "+19990009999"}]}
    snap = ctx.state_store.snapshot(ctx.session)

    state["contacts"].pop("anders")
    ctx.state_store.restore(ctx.session, snap)
    restored = ctx.state_store.get(ctx.session)

    assert "anders" in restored["contacts"]
    assert "temp" in restored["contacts"]
