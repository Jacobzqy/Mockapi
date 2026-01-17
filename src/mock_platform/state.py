"""Deterministic clock and in-memory state store."""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List


class Clock:
    """Logical clock that drives asynchronous events."""

    def __init__(self, start_ms: int = 0) -> None:
        """Initialize clock.

        Args:
            start_ms: Starting logical time in milliseconds.
        """
        self._now = start_ms
        self._listeners: List[Callable[[int], None]] = []

    def now_ms(self) -> int:
        """Return current logical time.

        Returns:
            Current logical time in milliseconds.
        """
        return self._now

    def advance(self, ms: int) -> int:
        """Advance clock and trigger listeners.

        Args:
            ms: Milliseconds to advance; must be non-negative.

        Returns:
            Current logical time in milliseconds.

        Raises:
            ValueError: If ms is negative.
        """
        if ms < 0:
            raise ValueError("Cannot advance clock by negative milliseconds")
        self._now += ms
        for listener in list(self._listeners):
            listener(self._now)
        return self._now

    def add_listener(self, listener: Callable[[int], None]) -> None:
        """Register a listener invoked on every advance.

        Args:
            listener: Callback accepting the new logical time in milliseconds.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)


class InMemoryStateStore:
    """Per-session in-memory state with snapshot/restore."""

    def __init__(self, factory: Callable[[], Dict[str, Any]]) -> None:
        """Initialize state store.

        Args:
            factory: Callable returning a fresh state dict.
        """
        self._factory = factory
        self._state: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        """Return (and lazily initialize) state for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Session state dictionary.
        """
        if session_id not in self._state:
            self._state[session_id] = copy.deepcopy(self._factory())
        return self._state[session_id]

    def reset(self, session_id: str) -> Dict[str, Any]:
        """Reset state for a session to the factory seed.

        Args:
            session_id: Session identifier.

        Returns:
            Fresh session state.
        """
        self._state[session_id] = copy.deepcopy(self._factory())
        return self._state[session_id]

    def reset_all(self) -> None:
        """Clear all sessions."""
        self._state.clear()

    def snapshot(self, session_id: str) -> Dict[str, Any]:
        """Return a deep copy snapshot for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Deep copy of the session state.
        """
        return copy.deepcopy(self.get(session_id))

    def restore(self, session_id: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Restore a session from a snapshot.

        Args:
            session_id: Session identifier.
            snapshot: Snapshot to restore.

        Returns:
            Restored session state.
        """
        self._state[session_id] = copy.deepcopy(snapshot)
        return self._state[session_id]
