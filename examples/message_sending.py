"""Send a text to Anders and verify delivery after advancing the logical clock."""

from mock_platform import (
    Clock,
    InMemoryStateStore,
    ToolContext,
    ToolRegistry,
    default_state_factory,
)
from mock_platform.services import register_admin_tools, register_contacts_tools, register_messaging_tools


def build_registry() -> ToolRegistry:
    """Create a registry with default tools."""
    registry = ToolRegistry()
    register_contacts_tools(registry)
    register_messaging_tools(registry)
    register_admin_tools(registry)
    return registry


def main() -> None:
    registry = build_registry()
    clock = Clock()
    state_store = InMemoryStateStore(default_state_factory)
    ctx = ToolContext(user_id="demo_user", trace_id="demo-trace", clock=clock, state_store=state_store)

    search = registry.call("contacts.search", {"q": "anders"}, ctx)
    print("contacts.search ->", search.to_dict())

    send = registry.call(
        "messaging.send_text",
        {
            "to": {"type": "contact_id", "value": "anders"},
            "text": "Let us meet up at 3 pm today",
            "client_msg_id": "msg-1",
        },
        ctx,
    )
    print("messaging.send_text ->", send.to_dict())

    clock.advance(500)  # trigger delivery

    message_id = send.data["message_id"]
    delivered = registry.call("messaging.get_message", {"message_id": message_id}, ctx)
    print("messaging.get_message ->", delivered.to_dict())


if __name__ == "__main__":
    main()
