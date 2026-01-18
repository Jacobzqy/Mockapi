"""Seed data and defaults."""

from __future__ import annotations

from typing import Any, Dict

from mock_platform.models import Contact, Memo

MOCK_DELIVERY_DELAY_MS = 500


def default_state_factory() -> Dict[str, Any]:
    """Return a seeded, JSON-serializable state snapshot.

    Returns:
        Seeded state dictionary.
    """
    anders = Contact(contact_id="anders", name="Anders", phones=[{"e164": "+15550001111"}])
    contacts = {anders.contact_id: anders.to_dict()}
    memo_seed = Memo(
        memo_id="decision",
        title="Decision",
        content="Casey is the successful candidate",
        created_at=0,
        updated_at=0,
    )
    return {
        "contacts": contacts,
        "memos": {memo_seed.memo_id: memo_seed.to_dict()},
        "messages": {},
        "conversations": {},
        "delivery_queue": [],
        "rules": {},
        "next_message_id": 1,
        "next_conversation_id": 1,
        "delivery_delay_ms": MOCK_DELIVERY_DELAY_MS,
    }
