"""Messaging mock tools with clock-driven delivery."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from mock_platform.context import ToolContext
from mock_platform.models import Conversation, Message
from mock_platform.registry import ToolRegistry
from mock_platform.tools import ToolError, ToolResult

_clock_listener_keys = set()


def register_messaging_tools(registry: ToolRegistry) -> None:
    """Register messaging tools.

    Args:
        registry: Tool registry to mutate.
    """
    registry.register_tool("messaging.send_text", send_text)
    registry.register_tool("messaging.get_message", get_message)
    registry.register_tool("messaging.list_messages", list_messages)


def send_text(args: dict, ctx: ToolContext) -> ToolResult:
    """Send a text message and schedule delivery via the logical clock.

    Args:
        args: Arguments containing to, text, client_msg_id.
        ctx: Tool invocation context.

    Returns:
        ToolResult with identifiers and status.
    """
    to = args.get("to")
    text = args.get("text")
    client_msg_id = args.get("client_msg_id")

    if not isinstance(to, dict) or not isinstance(text, str) or not isinstance(client_msg_id, str):
        return ToolResult(
            ok=False,
            error={"code": "invalid_arguments", "message": "to, text, client_msg_id are required", "details": None},
        )

    to_type = to.get("type")
    to_value = to.get("value")
    if to_type not in ("contact_id", "e164") or not isinstance(to_value, str):
        return ToolResult(
            ok=False,
            error={"code": "invalid_arguments", "message": "to must include type and value", "details": None},
        )

    state = ctx.state_store.get(ctx.session)
    _ensure_clock_listener(ctx)

    resolved_e164, contact_ref = _resolve_recipient(state, to_type, to_value)

    conversation_id = _ensure_conversation(state, resolved_e164, ctx.now_ms)
    message_id, message = _create_message(
        state,
        conversation_id,
        resolved_e164,
        text,
        client_msg_id,
        contact_ref,
        ctx.now_ms,
    )
    _schedule_delivery(state, message_id, ctx.now_ms, state["delivery_delay_ms"])

    return ToolResult(
        ok=True,
        data={"message_id": message_id, "conversation_id": conversation_id, "status": message["status"]},
    )


def get_message(args: dict, ctx: ToolContext) -> ToolResult:
    """Return message details.

    Args:
        args: Arguments containing message_id.
        ctx: Tool invocation context.

    Returns:
        ToolResult with message or error.
    """
    message_id = args.get("message_id")
    if not isinstance(message_id, str):
        return ToolResult(
            ok=False, error={"code": "invalid_arguments", "message": "message_id is required", "details": None}
        )

    state = ctx.state_store.get(ctx.session)
    message = state["messages"].get(message_id)
    if not message:
        raise ToolError("Message not found", code="not_found")
    return ToolResult(ok=True, data={"message": message})


def list_messages(args: dict, ctx: ToolContext) -> ToolResult:
    """List messages for a conversation.

    Args:
        args: Arguments containing conversation_id and optional limit.
        ctx: Tool invocation context.

    Returns:
        ToolResult with ordered messages or error.
    """
    conversation_id = args.get("conversation_id")
    limit = args.get("limit", 50)
    if not isinstance(conversation_id, str):
        return ToolResult(
            ok=False, error={"code": "invalid_arguments", "message": "conversation_id is required", "details": None}
        )
    if not isinstance(limit, int) or limit <= 0:
        return ToolResult(
            ok=False, error={"code": "invalid_arguments", "message": "limit must be a positive int", "details": None}
        )

    state = ctx.state_store.get(ctx.session)
    conversation = state["conversations"].get(conversation_id)
    if not conversation:
        raise ToolError("Conversation not found", code="not_found")

    message_ids: List[str] = conversation.get("messages", [])
    messages = [state["messages"][mid] for mid in message_ids][-limit:]
    return ToolResult(ok=True, data={"messages": messages})


# Helpers


def _ensure_clock_listener(ctx: ToolContext) -> None:
    """Attach delivery queue processing to the session clock."""
    key = (ctx.session, id(ctx.clock))
    if key in _clock_listener_keys:
        return

    def _on_advance(now_ms: int) -> None:
        _process_delivery_queue(ctx.session, ctx.state_store, now_ms)

    ctx.clock.add_listener(_on_advance)
    _clock_listener_keys.add(key)


def _resolve_recipient(state: dict, to_type: str, to_value: str) -> Tuple[str, Optional[dict]]:
    """Resolve recipient to e164 and optional contact reference."""
    if to_type == "e164":
        return to_value, None
    contacts = state["contacts"]
    contact = contacts.get(to_value)
    if not contact:
        raise ToolError("Contact not found", code="not_found")
    phones = contact.get("phones", [])
    if not phones:
        raise ToolError("Contact has no phone numbers", code="not_found")
    return phones[0].get("e164"), {"contact_id": contact["contact_id"]}


def _ensure_conversation(state: dict, to_e164: str, now_ms: int) -> str:
    """Find or create a conversation for the peer."""
    for conv in state["conversations"].values():
        if conv.get("peer") == to_e164:
            conv["updated_ms"] = now_ms
            return conv["conversation_id"]
    conversation_id = f"c{state['next_conversation_id']}"
    state["next_conversation_id"] += 1
    conv = Conversation(
        conversation_id=conversation_id,
        peer=to_e164,
        messages=[],
        status="active",
        created_ms=now_ms,
        updated_ms=now_ms,
    ).to_dict()
    state["conversations"][conversation_id] = conv
    return conversation_id


def _create_message(
    state: dict,
    conversation_id: str,
    to_e164: str,
    text: str,
    client_msg_id: str,
    contact_ref: Optional[dict],
    now_ms: int,
) -> Tuple[str, Dict[str, object]]:
    """Create and store a message."""
    message_id = f"m{state['next_message_id']}"
    state["next_message_id"] += 1
    message = Message(
        message_id=message_id,
        conversation_id=conversation_id,
        to={"type": "e164", "value": to_e164},
        text=text,
        client_msg_id=client_msg_id,
        status="sent",
        created_ms=now_ms,
        updated_ms=now_ms,
        contact=contact_ref,
    ).to_dict()
    state["messages"][message_id] = message
    state["conversations"][conversation_id]["messages"].append(message_id)
    state["conversations"][conversation_id]["updated_ms"] = now_ms
    return message_id, message


def _schedule_delivery(state: dict, message_id: str, now_ms: int, delay_ms: int) -> None:
    """Schedule a delivery update for a message."""
    due_ms = now_ms + delay_ms
    state["delivery_queue"].append(
        {"message_id": message_id, "due_ms": due_ms, "target_status": "delivered"}
    )


def _process_delivery_queue(session_id: str, store, now_ms: int) -> None:
    """Promote messages whose due time has passed."""
    state = store.get(session_id)
    queue: List[dict] = state.get("delivery_queue", [])
    remaining: List[dict] = []
    for item in queue:
        if item["due_ms"] <= now_ms:
            message = state["messages"].get(item["message_id"])
            if message and message.get("status") == "sent":
                message["status"] = item["target_status"]
                message["updated_ms"] = now_ms
        else:
            remaining.append(item)
    state["delivery_queue"] = remaining
