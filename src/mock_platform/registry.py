"""Tool registry with unified entry point."""

from __future__ import annotations

from typing import Callable, Dict

from mock_platform.context import ToolContext
from mock_platform.tools import ToolError, ToolResult

ToolFn = Callable[[dict, ToolContext], ToolResult]


class ToolRegistry:
    """Registers tools and exposes a single call entry point with uniform error handling."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._tools: Dict[str, ToolFn] = {}

    def register_tool(self, name: str, fn: ToolFn) -> None:
        """Register a tool handler.

        Args:
            name: Fully qualified tool name (e.g., `contacts.search`).
            fn: Callable accepting args dict and ToolContext, returning ToolResult.

        Raises:
            ValueError: If a tool with the same name already exists.
        """
        if name in self._tools:
            raise ValueError(f"Tool '{name}' already registered")
        self._tools[name] = fn

    def call(self, tool_name: str, args: dict, ctx: ToolContext) -> ToolResult:
        """Invoke a tool by name with standardized error handling.

        Args:
            tool_name: Registered tool name.
            args: Arguments dictionary.
            ctx: ToolContext for the invocation.

        Returns:
            ToolResult describing success or failure.
        """
        if tool_name not in self._tools:
            return ToolResult(
                ok=False,
                error={"code": "tool_not_found", "message": f"Tool '{tool_name}' not found", "details": None},
            )

        if not isinstance(args, dict):
            return ToolResult(
                ok=False,
                error={"code": "invalid_arguments", "message": "args must be a dict", "details": None},
            )

        handler = self._tools[tool_name]
        try:
            result = handler(args, ctx)
        except TypeError as exc:
            return ToolResult(
                ok=False,
                error={"code": "invalid_arguments", "message": str(exc), "details": None},
            )
        except ToolError as exc:
            return ToolResult(
                ok=False,
                error={"code": exc.code, "message": str(exc), "details": exc.details},
            )
        except Exception as exc:  # pylint: disable=broad-except
            return ToolResult(
                ok=False,
                error={"code": "internal_error", "message": str(exc), "details": None},
            )

        if not isinstance(result, ToolResult):
            return ToolResult(
                ok=False,
                error={"code": "invalid_return", "message": "Tool did not return ToolResult", "details": None},
            )
        return result
