"""Admin tools for managing state and delivery."""

from __future__ import annotations

from mock_platform.context import ToolContext
from mock_platform.registry import ToolRegistry
from mock_platform.tools import ToolError, ToolResult


def register_admin_tools(registry: ToolRegistry) -> None:
    """Register admin/maintenance tools.

    Args:
        registry: Tool registry to mutate.
    """
    registry.register_tool("admin.reset", reset_state)
    registry.register_tool("admin.set_delivery", set_delivery)
    registry.register_tool("admin.set_rule", set_rule)


def reset_state(args: dict, ctx: ToolContext) -> ToolResult:
    """Clear session state and restore seed data.

    Args:
        args: Unused.
        ctx: Tool invocation context.

    Returns:
        ToolResult indicating success.
    """
    ctx.state_store.reset(ctx.session)
    return ToolResult(ok=True, data={})


def set_delivery(args: dict, ctx: ToolContext) -> ToolResult:
    """Force a message delivery status.

    Args:
        args: Arguments containing message_id and status.
        ctx: Tool invocation context.

    Returns:
        ToolResult with updated message or error.
    """
    message_id = args.get("message_id")
    status = args.get("status")
    if not isinstance(message_id, str) or status not in {"sent", "delivered", "failed"}:
        return ToolResult(
            ok=False, error={"code": "invalid_arguments", "message": "message_id and status are required", "details": None}
        )

    state = ctx.state_store.get(ctx.session)
    message = state["messages"].get(message_id)
    if not message:
        raise ToolError("Message not found", code="not_found")
    message["status"] = status
    message["updated_ms"] = ctx.now_ms
    state["delivery_queue"] = [item for item in state.get("delivery_queue", []) if item["message_id"] != message_id]
    return ToolResult(ok=True, data={"message": message})


def set_rule(args: dict, ctx: ToolContext) -> ToolResult:
    """Reserve extension point for future fault injection.

    Args:
        args: Arguments containing name and value.
        ctx: Tool invocation context.

    Returns:
        ToolResult acknowledging the stored rule.
    """
    name = args.get("name")
    value = args.get("value")
    if not isinstance(name, str):
        return ToolResult(ok=False, error={"code": "invalid_arguments", "message": "name is required", "details": None})
    state = ctx.state_store.get(ctx.session)
    state.setdefault("rules", {})[name] = value
    return ToolResult(ok=True, data={"name": name, "value": value})
