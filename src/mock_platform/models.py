"""Dataclasses for mock platform entities."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Contact:
    """Contact record."""

    contact_id: str
    name: str
    phones: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return dict representation."""
        return asdict(self)


@dataclass
class Message:
    """Message record."""

    message_id: str
    conversation_id: str
    to: Dict[str, str]
    text: str
    client_msg_id: str
    status: str
    created_ms: int
    updated_ms: int
    contact: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return dict representation."""
        return asdict(self)


@dataclass
class Conversation:
    """Conversation record."""

    conversation_id: str
    peer: str
    messages: List[str] = field(default_factory=list)
    status: str = "active"
    created_ms: int = 0
    updated_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Return dict representation."""
        return asdict(self)
