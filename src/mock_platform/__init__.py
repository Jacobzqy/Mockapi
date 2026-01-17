"""Mock platform exposing deterministic in-process mock tools."""

from mock_platform.context import ToolContext
from mock_platform.models import Contact, Conversation, Message
from mock_platform.registry import ToolRegistry
from mock_platform.seeds import MOCK_DELIVERY_DELAY_MS, default_state_factory
from mock_platform.state import Clock, InMemoryStateStore
from mock_platform.tools import ToolError, ToolResult

__all__ = [
    "ToolContext",
    "ToolRegistry",
    "ToolResult",
    "ToolError",
    "Clock",
    "InMemoryStateStore",
    "default_state_factory",
    "MOCK_DELIVERY_DELAY_MS",
    "Contact",
    "Message",
    "Conversation",
]
