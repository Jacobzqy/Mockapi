"""Example: search a memo, read content, and send via messaging."""

from mock_platform import (
    Clock,
    InMemoryStateStore,
    ToolContext,
    ToolRegistry,
    default_state_factory,
)
from mock_platform.services import (
    register_admin_tools,
    register_contacts_tools,
    register_memo_tools,
    register_messaging_tools,
)


def build_registry() -> ToolRegistry:
    """Create a registry with default tools including memo."""
    registry = ToolRegistry()
    register_contacts_tools(registry)
    register_messaging_tools(registry)
    register_admin_tools(registry)
    register_memo_tools(registry)
    return registry


def main() -> None:
    registry = build_registry()
    clock = Clock()
    state_store = InMemoryStateStore(default_state_factory)
    ctx = ToolContext(user_id="demo_user", trace_id="memo-trace", clock=clock, state_store=state_store)

    search = registry.call("memo.search", {"title": "Decision"}, ctx)
    print("memo.search ->", search.to_dict())

    memo_id = search.data["memos"][0]["memo_id"]
    memo = registry.call("memo.get_memo", {"memo_id": memo_id}, ctx)
    print("memo.get_memo ->", memo.to_dict())

    content = memo.data["memo"]["content"]
    send = registry.call(
        "messaging.send_text",
        {"to": {"type": "contact_id", "value": "anders"}, "text": content, "client_msg_id": "memo-1"},
        ctx,
    )
    print("messaging.send_text ->", send.to_dict())

    clock.advance(600)

    delivered = registry.call("messaging.get_message", {"message_id": send.data["message_id"]}, ctx)
    print("messaging.get_message ->", delivered.to_dict())


if __name__ == "__main__":
    main()
