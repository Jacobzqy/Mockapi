"""Tool utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """Structured tool response.

    Attributes:
        ok: True when the tool succeeded.
        data: Optional payload dictionary.
        error: Optional error info with code/message/details.
        meta: Optional metadata about the execution.
    """

    ok: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a dict representation for logging or transport.

        Returns:
            Dictionary form of the result.
        """
        return {"ok": self.ok, "data": self.data, "error": self.error, "meta": self.meta}


class ToolError(Exception):
    """Raised by tool handlers for expected business failures."""

    def __init__(self, message: str, code: str = "error", details: Any | None = None) -> None:
        """Initialize ToolError.

        Args:
            message: Human-readable message.
            code: Machine-readable code.
            details: Optional structured details.
        """
        super().__init__(message)
        self.code = code
        self.details = details
