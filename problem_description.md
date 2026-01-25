
# Feature Request: In-Memory Message History for Socket.IO Rooms

## Problem

Clients that reconnect or join a room late cannot fetch recent context, degrading user experience.

## Requirements

### Core Features
- **Per-room history** - Store and retrieve recent messages for specific rooms
- **Disabled by default** - Opt-in per room to avoid unnecessary memory usage  
- **Namespace isolation** - History isolated per `(namespace, room)` pair
- **Default namespace** - Omitting namespace defaults to "/"

### Retention Controls
- **Size limit (required)** - Configurable max entries (oldest evicted first)
- **Time-based expiry (optional)** - TTL to remove old messages
- **Fetch limit** - Retrieve up to N most recent messages

### Query Capabilities
- **Event filtering** - Include/exclude specific event types
  - When both filters provided, apply inclusion first, then exclusion
- **Payload truncation** - Optionally limit payload size
  - Fetch-time truncation takes precedence over any enable-time setting
- **Chronological order** - Return messages oldest-to-newest among selected entries

## Behavior Specifications

1. **When disabled**: Fetching returns empty list; emitted events are not recorded
2. **Re-enabling**: Previously disabled rooms start fresh (no retained entries required)

## API Requirements

The following methods must be accessible from `socketio.Server` instance:

### Required Methods

1. **Enable/configure history** - Enable or configure history for a room
   - Must have explicit `room` parameter
   
2. **Disable history** - Disable history for a room
   - Must have explicit `room` parameter
   
3. **Fetch history** - Get history for a room
   - **Must have explicit parameters**: `room` AND `limit` (not in **kwargs)
   - **Returns**: List of entry dictionaries
   
4. **Get statistics** - Get stats for a room's history
   - Must have explicit `room` parameter
   - **Returns**: Dictionary with statistics counters

### Important: Parameter Implementation

**Critical**: The `room` and `limit` parameters MUST be explicit in the fetch method signature, not captured via `**kwargs`. For example:

✅ CORRECT:
```python
def get_history(room, limit, namespace='/', include_events=None, ...):
```

❌ INCORRECT:
```python
def get_history(room, **kwargs):  # limit hidden in kwargs
```

### Accepted Parameter Names

Parameters must use one of these accepted names:

| Concept | Accepted Names |
|---------|----------------|
| Room identifier | `room`, `room_id`, `room_name` |
| Namespace | `namespace`, `ns` |
| Fetch limit | `limit`, `n`, `count`, `max_items` |
| Max buffer size | `max_entries`, `max`, `limit` |
| Time-to-live | `retention_seconds`, `retention`, `ttl` |
| Payload cap | `payload_size_cap`, `cap`, `size_cap` |
| Include filter | `include_events`, `include`, `events_include` |
| Exclude filter | `exclude_events`, `exclude`, `events_exclude` |
| Enabled toggle | `enabled`, `enable`, `on` |

### Return Formats

**History entries** (each dict in the returned list contains):
- `event`: Event name (string)
- `data`: Event payload
- `timestamp`: Unix timestamp in seconds (float)

**Statistics dict** (must use one of these keys for each metric):

| Metric | Accepted Keys |
|--------|--------------|
| Entry count | `entries_count`, `entries`, `count` |
| Size evictions | `evictions_size`, `size_evictions`, `evictions_by_size` |
| Time evictions | `evictions_time`, `time_evictions`, `evictions_by_time` |

## Integration

The feature should integrate with Socket.IO's existing emit mechanism to automatically record messages when history is enabled for a room.
```

---

## Key Addition

The critical addition is the **"Important: Parameter Implementation"** section that explicitly states:

1. `room` and `limit` MUST be explicit parameters
2. They cannot be hidden in `**kwargs`
3. Shows correct vs incorrect examples

This should eliminate the TEST_MISMATCH failures where agents use `**kwargs` and the discovery mechanism can't find the parameters.

---

## Result

With this change, agents will know to use explicit parameters, and the discovery mechanism will be able to find them. This should convert the 3 TEST_MISMATCH failures into either passes or legitimate logic failures. 🎯