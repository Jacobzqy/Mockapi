"""Contacts mock tools."""

from __future__ import annotations

from typing import List

from mock_platform.context import ToolContext
from mock_platform.registry import ToolRegistry
from mock_platform.tools import ToolError, ToolResult


def register_contacts_tools(registry: ToolRegistry) -> None:
    """Register contact-related tools.

    Args:
        registry: Tool registry to mutate.
    """
    registry.register_tool("contacts.search", search_contacts)
    registry.register_tool("contacts.get", get_contact)


def search_contacts(args: dict, ctx: ToolContext) -> ToolResult:
    """Search contacts by name or phone substring.

    Args:
        args: Arguments containing 'q'.
        ctx: Tool invocation context.

    Returns:
        ToolResult with contacts list or error.
    """
    query = args.get("q")
    if not isinstance(query, str):
        return ToolResult(ok=False, error={"code": "invalid_arguments", "message": "q is required", "details": None})

    contacts = _contacts_state(ctx)
    q_lower = query.lower()
    matches: List[dict] = []
    for contact in contacts.values():
        if q_lower in contact.get("name", "").lower():
            matches.append(contact)
            continue
        for phone in contact.get("phones", []):
            if q_lower in phone.get("e164", "").lower():
                matches.append(contact)
                break
    return ToolResult(ok=True, data={"contacts": matches})


def get_contact(args: dict, ctx: ToolContext) -> ToolResult:
    """Return a contact by id.

    Args:
        args: Arguments containing 'contact_id'.
        ctx: Tool invocation context.

    Returns:
        ToolResult with contact or error.
    """
    contact_id = args.get("contact_id")
    if not isinstance(contact_id, str):
        return ToolResult(
            ok=False, error={"code": "invalid_arguments", "message": "contact_id is required", "details": None}
        )

    contacts = _contacts_state(ctx)
    contact = contacts.get(contact_id)
    if not contact:
        raise ToolError("Contact not found", code="not_found")
    return ToolResult(ok=True, data={"contact": contact})


def _contacts_state(ctx: ToolContext) -> dict:
    """Return contacts state for session."""
    return ctx.state_store.get(ctx.session)["contacts"]
