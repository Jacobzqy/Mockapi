"""Memo mock tools (content-agnostic)."""

from __future__ import annotations

from typing import List

from mock_platform.context import ToolContext
from mock_platform.models import Memo
from mock_platform.registry import ToolRegistry
from mock_platform.tools import ToolError, ToolResult


def register_memo_tools(registry: ToolRegistry) -> None:
    """Register memo tools.

    Args:
        registry: Tool registry to mutate.
    """
    registry.register_tool("memo.list_memos", list_memos)
    registry.register_tool("memo.search", search_memos)
    registry.register_tool("memo.get_memo", get_memo)


def list_memos(args: dict, ctx: ToolContext) -> ToolResult:
    """List memo summaries.

    Args:
        args: Unused.
        ctx: Tool invocation context.

    Returns:
        ToolResult with memo summaries.
    """
    memos = _memo_state(ctx)
    summaries = [_summary(memo) for memo in memos.values()]
    return ToolResult(ok=True, data={"memos": summaries})


def search_memos(args: dict, ctx: ToolContext) -> ToolResult:
    """Search memos by title substring (case-insensitive).

    Args:
        args: Arguments containing 'title'.
        ctx: Tool invocation context.

    Returns:
        ToolResult with memo summaries.
    """
    title = args.get("title")
    if not isinstance(title, str):
        return ToolResult(
            ok=False,
            error={"code": "invalid_arguments", "message": "title is required", "details": None},
        )

    memos = _memo_state(ctx)
    needle = title.lower()
    matches: List[dict] = [_summary(m) for m in memos.values() if needle in m.get("title", "").lower()]
    return ToolResult(ok=True, data={"memos": matches})


def get_memo(args: dict, ctx: ToolContext) -> ToolResult:
    """Fetch a memo by id.

    Args:
        args: Arguments containing 'memo_id'.
        ctx: Tool invocation context.

    Returns:
        ToolResult with memo details or error.
    """
    memo_id = args.get("memo_id")
    if not isinstance(memo_id, str):
        return ToolResult(
            ok=False,
            error={"code": "invalid_arguments", "message": "memo_id is required", "details": None},
        )
    memos = _memo_state(ctx)
    memo = memos.get(memo_id)
    if not memo:
        raise ToolError("Memo not found", code="not_found")
    return ToolResult(ok=True, data={"memo": memo})


# Helpers


def _memo_state(ctx: ToolContext) -> dict:
    """Return memos state for session."""
    return ctx.state_store.get(ctx.session).setdefault("memos", {})


def _summary(memo: dict) -> dict:
    """Return summary view of a memo."""
    return {
        "memo_id": memo["memo_id"],
        "title": memo["title"],
        "updated_at": memo["updated_at"],
    }
