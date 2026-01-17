"""ToolContext definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from mock_platform.state import Clock, InMemoryStateStore


@dataclass
class ToolContext:
    """Carries per-call context.

    Attributes:
        user_id: Identifier for the acting user; also used for session isolation by default.
        trace_id: Correlation id for tracing.
        now_ms: Current logical time (derived from the clock).
        clock: Logical clock driving asynchronous events.
        state_store: Shared state store for the session.
        session_id: Optional session override; defaults to user_id.
        meta: Extra metadata.
    """

    user_id: str
    trace_id: str
    clock: Clock
    state_store: InMemoryStateStore
    session_id: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def now_ms(self) -> int:
        """Return the current logical time in milliseconds."""
        return self.clock.now_ms()

    @property
    def session(self) -> str:
        """Return the session id used for state isolation."""
        return self.session_id or self.user_id
