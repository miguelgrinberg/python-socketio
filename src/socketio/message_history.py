import copy
import time
import threading
from collections import deque
from typing import Any, Dict, List, Optional, Set, Union


class RoomHistory:
    """Manages message history for a single (namespace, room) pair."""

    def __init__(self, max_entries: int = 100, retention_seconds: Optional[float] = None,
                 payload_size_cap: Optional[int] = None):
        # Validate inputs
        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        if retention_seconds is not None and retention_seconds <= 0:
            raise ValueError("retention_seconds must be positive")
        if payload_size_cap is not None and payload_size_cap <= 0:
            raise ValueError("payload_size_cap must be positive")

        self.max_entries = max_entries
        self.retention_seconds = retention_seconds
        self.payload_size_cap = payload_size_cap
        self.enabled = True
        self.buffer: deque = deque(maxlen=max_entries)
        self.lock = threading.Lock()

        # Statistics
        self.evictions_size = 0
        self.evictions_time = 0

    def add_entry(self, event: str, data: Any, timestamp: float):
        """Add a new entry to the history buffer."""
        if not self.enabled:
            return

        with self.lock:
            # Apply enable-time payload cap if configured
            if self.payload_size_cap is not None:
                data = self._truncate_payload(data, self.payload_size_cap)

            entry = {
                "event": event,
                "data": data,
                "timestamp": timestamp
            }

            # Check if we're at capacity before adding
            if len(self.buffer) == self.max_entries:
                self.evictions_size += 1

            self.buffer.append(entry)

            # Prune old entries based on retention time
            if self.retention_seconds is not None:
                self._prune_old_entries(timestamp)

    def _prune_old_entries(self, current_time: float):
        """Remove entries older than retention_seconds."""
        cutoff_time = current_time - self.retention_seconds

        while self.buffer and self.buffer[0]["timestamp"] < cutoff_time:
            self.buffer.popleft()
            self.evictions_time += 1

    def _truncate_payload(self, data: Any, size_cap: int) -> Any:
        """Truncate string or bytes payloads to the specified size."""
        if isinstance(data, str):
            return data[:size_cap]
        elif isinstance(data, bytes):
            return data[:size_cap]
        elif isinstance(data, dict):
            # Recursively truncate dict values
            return {k: self._truncate_payload(v, size_cap) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            # Recursively truncate list/tuple items
            result = [self._truncate_payload(item, size_cap) for item in data]
            return type(data)(result) if isinstance(data, tuple) else result
        return data

    def get_history(self, limit: int, include_events: Optional[Set[str]] = None,
                    exclude_events: Optional[Set[str]] = None,
                    payload_size_cap: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve history with filters applied."""
        if not self.enabled:
            return []

        with self.lock:
            # Prune old entries if retention is configured
            if self.retention_seconds is not None:
                self._prune_old_entries(time.time())

            # Convert buffer to list for filtering
            entries = list(self.buffer)

            # Apply include filter first
            if include_events is not None:
                entries = [e for e in entries if e["event"] in include_events]

            # Apply exclude filter second
            if exclude_events is not None:
                entries = [e for e in entries if e["event"] not in exclude_events]

            # Select the most recent N entries (where N = limit)
            if len(entries) > limit:
                entries = entries[-limit:]

            # Apply fetch-time payload cap if provided (overrides enable-time cap)
            if payload_size_cap is not None:
                entries = [
                    {
                        "event": e["event"],
                        "data": self._truncate_payload(e["data"], payload_size_cap),
                        "timestamp": e["timestamp"]
                    }
                    for e in entries
                ]
            else:
                # Deep copy to avoid external modifications
                entries = [
                    {
                        "event": e["event"],
                        "data": copy.deepcopy(e["data"]),
                        "timestamp": e["timestamp"]
                    }
                    for e in entries
                ]

            return entries

    def get_stats(self) -> Dict[str, int]:
        """Get statistics for this room's history."""
        with self.lock:
            return {
                "entries": len(self.buffer),
                "evictions_size": self.evictions_size,
                "evictions_time": self.evictions_time
            }

    def disable(self):
        """Disable history recording for this room."""
        with self.lock:
            self.enabled = False

    def enable(self):
        """Enable history recording for this room."""
        with self.lock:
            self.enabled = True

    def clear(self):
        """Clear all entries from the buffer."""
        with self.lock:
            self.buffer.clear()

    def configure(self, enabled: Optional[bool] = None, max_entries: Optional[int] = None,
                  retention_seconds: Optional[float] = None,
                  payload_size_cap: Optional[int] = None):
        """Update configuration for this room's history."""
        with self.lock:
            if enabled is not None:
                self.enabled = enabled
            if max_entries is not None:
                if max_entries <= 0:
                    raise ValueError("max_entries must be positive")
                self.max_entries = max_entries
                # Resize the buffer
                new_buffer = deque(self.buffer, maxlen=max_entries)
                evicted = len(self.buffer) - len(new_buffer)
                if evicted > 0:
                    self.evictions_size += evicted
                self.buffer = new_buffer
            if retention_seconds is not None:
                if retention_seconds <= 0:
                    raise ValueError("retention_seconds must be positive")
                self.retention_seconds = retention_seconds
            if payload_size_cap is not None:
                if payload_size_cap <= 0:
                    raise ValueError("payload_size_cap must be positive")
                self.payload_size_cap = payload_size_cap


class MessageHistory:
    """Manages message history for all rooms across all namespaces."""

    def __init__(self):
        self.histories: Dict[tuple, RoomHistory] = {}
        self.lock = threading.Lock()

    def _get_key(self, namespace: str, room: str) -> tuple:
        """Get the key for a (namespace, room) pair."""
        return (namespace, room)

    def record_message(self, event: str, data: Any, namespace: str, room: str):
        """Record a message to the history if enabled for this room."""
        key = self._get_key(namespace, room)

        # Fast path: check without holding lock for too long
        history = self.histories.get(key)
        if history is None:
            return

        # Record outside the main lock to minimize contention
        timestamp = time.time()
        try:
            history.add_entry(event, data, timestamp)
        except Exception:
            # Best-effort: if recording fails, don't break the emit
            pass

    def enable_history(self, room: str, namespace: str = "/", max_entries: int = 100,
                       retention_seconds: Optional[float] = None,
                       payload_size_cap: Optional[int] = None):
        """Enable history for a specific room."""
        key = self._get_key(namespace, room)

        with self.lock:
            if key not in self.histories:
                self.histories[key] = RoomHistory(
                    max_entries=max_entries,
                    retention_seconds=retention_seconds,
                    payload_size_cap=payload_size_cap
                )
            else:
                # Re-enabling: clear buffer and enable
                self.histories[key].clear()
                self.histories[key].enable()

    def disable_history(self, room: str, namespace: str = "/"):
        """Disable history for a specific room."""
        key = self._get_key(namespace, room)

        with self.lock:
            if key in self.histories:
                self.histories[key].disable()

    def configure_history(self, room: str, namespace: str = "/", enabled: Optional[bool] = None,
                          max_entries: Optional[int] = None,
                          retention_seconds: Optional[float] = None,
                          payload_size_cap: Optional[int] = None):
        """Configure history settings for a specific room."""
        key = self._get_key(namespace, room)

        with self.lock:
            if key not in self.histories:
                # Create new history with provided settings
                self.histories[key] = RoomHistory(
                    max_entries=max_entries or 100,
                    retention_seconds=retention_seconds,
                    payload_size_cap=payload_size_cap
                )
                if enabled is not None:
                    self.histories[key].enabled = enabled
            else:
                # Check if re-enabling (was disabled, now enabled)
                was_enabled = self.histories[key].enabled
                if enabled is True and not was_enabled:
                    # Re-enabling: clear buffer
                    self.histories[key].clear()

                self.histories[key].configure(
                    enabled=enabled,
                    max_entries=max_entries,
                    retention_seconds=retention_seconds,
                    payload_size_cap=payload_size_cap
                )

    def get_history(self, room: str, limit: int = 50, namespace: str = "/",
                    include_events: Optional[Union[List[str], tuple, Set[str]]] = None,
                    exclude_events: Optional[Union[List[str], tuple, Set[str]]] = None,
                    payload_size_cap: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get history for a specific room with optional filters."""
        key = self._get_key(namespace, room)

        with self.lock:
            if key not in self.histories:
                return []
            history = self.histories[key]

        # Convert iterables to sets for efficient lookup
        include_set = set(include_events) if include_events is not None else None
        exclude_set = set(exclude_events) if exclude_events is not None else None

        return history.get_history(limit, include_set, exclude_set, payload_size_cap)

    def get_stats(self, room: str, namespace: str = "/") -> Dict[str, int]:
        """Get statistics for a specific room's history."""
        key = self._get_key(namespace, room)

        with self.lock:
            if key not in self.histories:
                return {
                    "entries": 0,
                    "evictions_size": 0,
                    "evictions_time": 0
                }
            history = self.histories[key]

        return history.get_stats()