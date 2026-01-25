import time
import inspect
import functools
import socketio
import pytest


def _mk_server():
    """Basic in-memory server suitable for unit tests."""
    return socketio.Server(async_mode="threading")


# ---------- Discovery and adaptation helpers ----------

def _iter_callables(obj, max_depth=3):
    """Yield (owner, name, callable) by recursively scanning attributes up to max_depth."""
    seen = set()

    def walk(target, depth):
        if depth > max_depth:
            return
        for name in dir(target):
            if name.startswith("_"):
                continue
            try:
                cand = getattr(target, name, None)
            except Exception:
                continue
            if callable(cand):
                key = (id(target), name)
                if key not in seen:
                    seen.add(key)
                    yield (target, name, cand)
            if cand is None or callable(cand):
                continue
            try:
                yield from walk(cand, depth + 1)
            except Exception:
                continue

    yield from walk(obj, 0)


def _find_callable(obj, predicate):
    """Find first callable matching predicate."""
    for owner, name, fn in _iter_callables(obj):
        if predicate(name, fn):
            return name, fn
    return None, None


def _has_roomish_param(fn):
    """Check if function has a room-like parameter."""
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return False
    pnames = set(sig.parameters.keys())
    # Only use aliases from the spec
    return _pick_alias(pnames, ["room", "room_id", "room_name"]) is not None


def _pick_alias(param_names, aliases):
    """Return the first alias that exists in param_names, else None."""
    for a in aliases:
        if a in param_names:
            return a
    return None


def _wrap_kwargs(fn, semantic_kwargs=True):
    """Build a wrapper for fn that accepts semantic kwargs using spec-defined aliases."""
    sig = inspect.signature(fn)
    params = set(sig.parameters.keys())
    # Only aliases from the spec
    alias_map = {
        "room": ["room", "room_id", "room_name"],
        "limit": ["limit", "n", "count", "max_items"],
        "namespace": ["namespace", "ns"],
        "include_events": ["include_events", "include", "events_include"],
        "exclude_events": ["exclude_events", "exclude", "events_exclude"],
        "payload_size_cap": ["payload_size_cap", "cap", "size_cap"],
        "enabled": ["enabled", "enable", "on"],
        "max_entries": ["max_entries", "max", "limit"],
        "retention_seconds": ["retention_seconds", "retention", "ttl"],
    }

    def map_kwargs(kwargs):
        mapped = {}
        for sem_key, value in kwargs.items():
            aliases = alias_map.get(sem_key, [sem_key])
            chosen = _pick_alias(params, aliases)
            if chosen is not None:
                mapped[chosen] = value
        return mapped

    @functools.wraps(fn)
    def wrapper(**kwargs):
        return fn(**map_kwargs(kwargs))

    return wrapper


def discover_get_history(sio):
    """Find the best matching fetch method by scoring candidates."""
    candidates = []
    for owner, name, fn in _iter_callables(sio):
        lname = name.lower()
        try:
            sig = inspect.signature(fn)
            pnames = set(sig.parameters.keys())
        except (TypeError, ValueError):
            continue

        # Only use aliases from the spec
        room_ok = _pick_alias(pnames, ["room", "room_id", "room_name"]) is not None
        limit_ok = _pick_alias(pnames, ["limit", "n", "count", "max_items"]) is not None
        any_opt = any(_pick_alias(pnames, alist) for alist in [
            ["namespace", "ns"],
            ["include_events", "include", "events_include"],
            ["exclude_events", "exclude", "events_exclude"],
            ["payload_size_cap", "cap", "size_cap"],
        ])

        has_fetch_get = any(k in lname for k in ["get", "fetch"]) or lname.startswith("list")
        is_setter_like = any(k in lname for k in ["set", "configure", "update", "assign"]) and not ("get" in lname or "fetch" in lname)
        has_history_hint = ("history" in lname) or ("recent" in lname) or ("buffer" in lname)

        score = 0
        if room_ok:
            score += 2
        if limit_ok:
            score += 2
        if any_opt:
            score += 1
        if has_fetch_get:
            score += 1
        if is_setter_like:
            score -= 2
        if has_history_hint:
            score += 1

        if room_ok and limit_ok:
            candidates.append((score, name, fn))

    assert candidates, "Missing a room history getter per spec."
    candidates.sort(key=lambda t: (-t[0], t[1]))
    _, _, best = candidates[0]
    return _wrap_kwargs(best, semantic_kwargs=True)


def discover_enable_disable_configure(sio):
    """Return a tuple of wrappers: (enable_fn, disable_fn, configure_fn, enable_params_set)."""
    def pred_enable(name, fn):
        lname = name.lower()
        return any(k in lname for k in ["enable", "on", "start", "activate", "set"]) and _has_roomish_param(fn)

    def pred_disable(name, fn):
        lname = name.lower()
        return any(k in lname for k in ["disable", "off", "stop", "deactivate", "unset"]) and _has_roomish_param(fn)

    def pred_config(name, fn):
        lname = name.lower()
        return any(k in lname for k in ["config", "configure", "set"]) and _has_roomish_param(fn)

    _, e_fn = _find_callable(sio, pred_enable)
    _, d_fn = _find_callable(sio, pred_disable)
    _, c_fn = _find_callable(sio, pred_config)

    e_wrap = _wrap_kwargs(e_fn, semantic_kwargs=True) if e_fn else None
    d_wrap = _wrap_kwargs(d_fn, semantic_kwargs=True) if d_fn else None
    c_wrap = _wrap_kwargs(c_fn, semantic_kwargs=True) if c_fn else None

    enable_params_set = set()
    if e_fn:
        p = set(inspect.signature(e_fn).parameters.keys())
        for sem, aliases in {
            "namespace": ["namespace", "ns"],
            "max_entries": ["max_entries", "max", "limit"],
            "retention_seconds": ["retention_seconds", "retention", "ttl"],
            "payload_size_cap": ["payload_size_cap", "cap", "size_cap"],
            "enabled": ["enabled", "enable", "on"],
        }.items():
            if _pick_alias(p, aliases):
                enable_params_set.add(sem)

    return e_wrap, d_wrap, c_wrap, enable_params_set


def discover_stats_getter(sio):
    """Return (stats_fn_wrapper, fields_alias) or (None, None)."""
    def pred(name, fn):
        lname = name.lower()
        return any(k in lname for k in ["stats", "metrics", "observability", "counters", "counts"])

    _, fn = _find_callable(sio, pred)
    if not fn:
        return None, None

    stats_wrap = _wrap_kwargs(fn, semantic_kwargs=True)
    # Only aliases from the spec
    fields_alias = {
        "entries": ["entries_count", "entries", "count"],
        "evict_size": ["evictions_size", "size_evictions", "evictions_by_size"],
        "evict_time": ["evictions_time", "time_evictions", "evictions_by_time"],
    }
    return stats_wrap, fields_alias


def pick_stat_keys(stats_dict, fields_alias):
    """Pick actual keys from stats dict based on allowed aliases."""
    picked = {}
    for need, aliases in fields_alias.items():
        for key in aliases:
            if key in stats_dict:
                picked[need] = key
                break
        assert need in picked, f"stats missing required semantic field: {need}"
    return picked


# ---------- Tests ----------

def test_default_disabled_is_required_with_enable_path():
    """History must be disabled by default and require explicit enablement."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    assert enable_fn or configure_fn, (
        "Spec requires per-room enablement."
    )

    hist = get_history(room="__t:default_disabled__", limit=10, namespace="/")
    assert isinstance(hist, list)
    assert hist == [], "History must be empty before enabling."

    sio.emit("x_disabled", 1, room="__t:default_disabled__", namespace="/")
    hist2 = get_history(room="__t:default_disabled__", limit=10, namespace="/")
    assert hist2 == []


def test_ordering_and_schema_after_enable():
    """After enabling, messages should be recorded with correct schema and ordering."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:order__"

    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        if "max_entries" in enable_params:
            kwargs["max_entries"] = 50
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        max_key = _pick_alias(cfg_sig, ["max_entries", "max", "limit"])
        if max_key:
            kwargs[max_key] = 50
        configure_fn(**kwargs)

    sio.emit("message", {"text": "hello"}, room=room)
    time.sleep(0.01)
    sio.emit("message", {"text": "world"}, room=room)
    time.sleep(0.01)
    sio.emit("message", {"text": "!"}, room=room)

    hist = get_history(room=room, limit=2, namespace="/")
    assert isinstance(hist, list)
    assert len(hist) == 2
    assert [e["data"]["text"] for e in hist] == ["world", "!"]

    now = time.time()
    for e in hist:
        assert "event" in e and "data" in e and "timestamp" in e
        assert isinstance(e["timestamp"], float)
        assert now - 24 * 3600 <= e["timestamp"] <= now + 5


def test_include_only_and_exclude_only_filters_required():
    """Include and exclude filters must work correctly."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:filters__"

    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        configure_fn(**kwargs)

    sio.emit("state", {"v": 1}, room=room)
    sio.emit("info", {"v": 2}, room=room)
    sio.emit("other", {"v": 3}, room=room)

    inc = get_history(
        room=room, limit=10, namespace="/",
        include_events=["state", "info"], exclude_events=None, payload_size_cap=None
    )
    assert all(h["event"] in {"state", "info"} for h in inc)

    exc = get_history(
        room=room, limit=10, namespace="/",
        include_events=None, exclude_events=["info"], payload_size_cap=None
    )
    assert all(h["event"] != "info" for h in exc)

    both = get_history(
        room=room, limit=10, namespace="/",
        include_events=("state", "info"), exclude_events={"info"}, payload_size_cap=None
    )
    assert all(h["event"] in {"state", "info"} for h in both)
    assert all(h["event"] != "info" for h in both)

def test_stats_getter_is_per_room():
    """Stats getter must accept room parameter and return room-specific stats."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    stats_fn, fields_alias = discover_stats_getter(sio)
    assert stats_fn is not None, "Spec requires stats getter"

    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    r1, r2 = "__t:stats_room:1__", "__t:stats_room:2__"

    # Enable both rooms
    if enable_fn:
        kwargs = {}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        if "max_entries" in enable_params:
            kwargs["max_entries"] = 10
        enable_fn(room=r1, **kwargs)
        enable_fn(room=r2, **kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        base = {"enabled": True}
        if "namespace" in cfg_sig:
            base["namespace"] = "/"
        max_key = _pick_alias(cfg_sig, ["max_entries", "max", "limit"])
        if max_key:
            base[max_key] = 10
        configure_fn(room=r1, **base)
        configure_fn(room=r2, **base)

    # Emit different counts to each room
    sio.emit("a", 1, room=r1)
    sio.emit("a", 2, room=r1)
    sio.emit("a", 3, room=r1)
    sio.emit("b", 1, room=r2)

    # Stats should be per-room, not global
    s1 = stats_fn(room=r1, namespace="/")
    s2 = stats_fn(room=r2, namespace="/")

    keys1 = pick_stat_keys(s1, fields_alias)
    keys2 = pick_stat_keys(s2, fields_alias)

    # Room 1 has 3 entries, Room 2 has 1
    assert s1[keys1["entries"]] == 3, "Stats must be per-room"
    assert s2[keys2["entries"]] == 1, "Stats must be per-room"

def test_size_eviction_required():
    """Size-based eviction must work correctly (required feature)."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room1 = "__t:evict:size__"

    if enable_fn:
        kwargs = {"room": room1}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        if "max_entries" in enable_params:
            kwargs["max_entries"] = 2
            enable_fn(**kwargs)
        else:
            enable_fn(**kwargs)
            if configure_fn:
                cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
                max_key = _pick_alias(cfg_sig, ["max_entries", "max", "limit"])
                if max_key:
                    cfg_kwargs = {"room": room1, "enabled": True, max_key: 2}
                    if "namespace" in cfg_sig:
                        cfg_kwargs["namespace"] = "/"
                    configure_fn(**cfg_kwargs)
                else:
                    pytest.fail("Spec requires a size cap knob; none discovered")
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        max_key = _pick_alias(cfg_sig, ["max_entries", "max", "limit"])
        assert max_key is not None, "Spec requires a size cap knob"
        cfg_kwargs = {"room": room1, "enabled": True, max_key: 2}
        if "namespace" in cfg_sig:
            cfg_kwargs["namespace"] = "/"
        configure_fn(**cfg_kwargs)

    for i in range(5):
        sio.emit("message", {"i": i}, room=room1)

    h1 = get_history(room=room1, limit=10, namespace="/")
    assert [e["data"]["i"] for e in h1] == [3, 4]

def test_api_requirements_accessible_on_server():
    """Required methods must be accessible directly on socketio.Server."""
    sio = _mk_server()
    
    assert hasattr(sio, 'enable_history') and callable(getattr(sio, 'enable_history'))
    assert hasattr(sio, 'disable_history') and callable(getattr(sio, 'disable_history'))  
    assert hasattr(sio, 'get_history') and callable(getattr(sio, 'get_history'))
    assert hasattr(sio, 'get_history_stats') and callable(getattr(sio, 'get_history_stats'))
    
    sig_enable = inspect.signature(sio.enable_history)
    assert 'room' in sig_enable.parameters
    
    sig_disable = inspect.signature(sio.disable_history)  
    assert 'room' in sig_disable.parameters
    
    sig_get = inspect.signature(sio.get_history)
    assert 'room' in sig_get.parameters
    assert 'limit' in sig_get.parameters
    
    sig_stats = inspect.signature(sio.get_history_stats)
    assert 'room' in sig_stats.parameters

def test_filter_ordering_include_then_exclude():
    """When both filters provided, include must be applied first, then exclude."""
    sio = _mk_server()
    
    room = "__t:filter_order__"
    sio.enable_history(room=room)
    
    sio.emit("A", {"val": 1}, room=room)
    sio.emit("B", {"val": 2}, room=room)
    sio.emit("C", {"val": 3}, room=room)
    sio.emit("D", {"val": 4}, room=room)
    
    result = sio.get_history(
        room=room, limit=10,
        include_events=["A", "B"],
        exclude_events=["B", "D"]
    )
    
    events = [e["event"] for e in result]
    assert "A" in events, "A should be included"
    assert "B" not in events, "B should be excluded (after being included)"
    assert "C" not in events, "C should not be included"
    assert "D" not in events, "D should be excluded"
    assert len(events) == 1, "Only event A should remain"

    result2 = sio.get_history(
        room=room, limit=10,
        include_events=["B"], 
        exclude_events=["B"]
    )
    assert len(result2) == 0, "Include must be applied first, then exclude"

def test_time_retention_optional():
    """Time-based eviction (optional feature per spec)."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room2 = "__t:evict:time__"

    # Check if TTL is supported
    ttl_supported = False
    ret_key = None

    if enable_fn and "retention_seconds" in enable_params:
        ttl_supported = True
    elif configure_fn:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        ret_key = _pick_alias(cfg_sig, ["retention_seconds", "retention", "ttl"])
        if ret_key:
            ttl_supported = True

    if not ttl_supported:
        pytest.skip("Time-based expiry is optional per spec; not supported by this implementation")

    if enable_fn and "retention_seconds" in enable_params:
        kwargs = {"room": room2, "retention_seconds": 0.5}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        ret_key = _pick_alias(cfg_sig, ["retention_seconds", "retention", "ttl"])
        cfg_kwargs = {"room": room2, "enabled": True, ret_key: 0.5}
        if "namespace" in cfg_sig:
            cfg_kwargs["namespace"] = "/"
        configure_fn(**cfg_kwargs)

    sio.emit("m", {"x": 1}, room=room2)
    time.sleep(0.7)
    h2 = get_history(room=room2, limit=10, namespace="/")
    assert h2 == []


def test_namespace_isolation_using_fetch_namespace():
    """History must be isolated by namespace."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:ns__"
    ns1 = "/"
    ns2 = "/admin"

    if enable_fn:
        if "namespace" in enable_params:
            enable_fn(room=room, namespace=ns1)
            enable_fn(room=room, namespace=ns2)
        else:
            enable_fn(room=room)
    elif configure_fn:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        if "namespace" in cfg_sig:
            configure_fn(room=room, enabled=True, namespace=ns1)
            configure_fn(room=room, enabled=True, namespace=ns2)
        else:
            configure_fn(room=room, enabled=True)

    sio.emit("e1", {"n": 1}, room=room, namespace=ns1)
    sio.emit("e2", {"n": 2}, room=room, namespace=ns2)

    h1 = get_history(room=room, limit=10, namespace=ns1)
    h2 = get_history(room=room, limit=10, namespace=ns2)

    assert any(e["event"] == "e1" for e in h1)
    assert not any(e["event"] == "e2" for e in h1)
    assert any(e["event"] == "e2" for e in h2)
    assert not any(e["event"] == "e1" for e in h2)


def test_limit_applies_after_filters_oldest_to_newest():
    """Limit should apply after filtering, returning oldest-to-newest."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:filters_limit__"

    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        configure_fn(**kwargs)

    for i in range(6):
        sio.emit("state" if i % 2 == 0 else "info", {"i": i}, room=room)

    hist = get_history(
        room=room, limit=2, namespace="/",
        include_events=["state"], exclude_events=None, payload_size_cap=None
    )
    assert len(hist) == 2
    assert [e["data"]["i"] for e in hist] == [2, 4]


def test_default_namespace_fallback_behaves_like_root():
    """Omitting namespace should default to root namespace."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:ns_default__"

    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        configure_fn(**kwargs)

    sio.emit("x", {"v": 1}, room=room)
    h_no_ns = get_history(room=room, limit=10)
    h_root = get_history(room=room, limit=10, namespace="/")
    assert [e["event"] for e in h_no_ns] == [e["event"] for e in h_root]


def test_enable_time_payload_cap_if_supported():
    """Enable-time payload cap should apply when fetch-time cap is omitted (if supported)."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:cap_enable_only__"
    long_txt = "abcdefghijklmnopqrstuvwxyz"

    # Check if enable-time cap is supported
    applied = False
    if enable_fn and "payload_size_cap" in enable_params:
        kwargs = {"room": room, "payload_size_cap": 5}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
        applied = True
    elif configure_fn:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        cap_key = _pick_alias(cfg_sig, ["payload_size_cap", "cap", "size_cap"])
        enabled_key = _pick_alias(cfg_sig, ["enabled", "enable", "on"])
        if enabled_key and cap_key:
            kwargs = {"room": room, enabled_key: True, cap_key: 5}
            if "namespace" in cfg_sig:
                kwargs["namespace"] = "/"
            configure_fn(**kwargs)
            applied = True

    if not applied:
        pytest.skip("Payload truncation is optional; not supported by this implementation")

    sio.emit("text", long_txt, room=room)
    hist = get_history(room=room, limit=10, namespace="/")
    txt = next(e for e in hist if e["event"] == "text")["data"]
    assert isinstance(txt, str) and len(txt) <= 5

def test_payload_size_cap_at_fetch_time_if_supported():
    """Payload size cap should truncate strings and bytes at fetch time (if supported)."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    # Check if fetch-time payload cap is supported
    try:
        sig = inspect.signature(get_history.__wrapped__)
    except AttributeError:
        sig = inspect.signature(get_history)
    
    params = set(sig.parameters.keys())
    cap_param = _pick_alias(params, ["payload_size_cap", "cap", "size_cap"])
    
    if cap_param is None:
        pytest.skip("Fetch-time payload truncation is optional; not supported by this implementation")

    room = "__t:cap__"

    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        configure_fn(**kwargs)

    sio.emit("text", "abcdefghij", room=room)
    sio.emit("blob", b"ABCDEFGHIJ", room=room)

    hist = get_history(
        room=room, limit=10, namespace="/",
        include_events=None, exclude_events=None, payload_size_cap=5
    )
    txt = next(e for e in hist if e["event"] == "text")["data"]
    blob = next(e for e in hist if e["event"] == "blob")["data"]
    assert txt == "abcde"
    assert blob == b"ABCDE"


def test_fetch_time_cap_precedence_if_both_supported():
    """Fetch-time payload cap takes precedence over enable-time cap (if both supported)."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    # Check if fetch-time cap is supported
    try:
        sig = inspect.signature(get_history.__wrapped__)
    except AttributeError:
        sig = inspect.signature(get_history)
    
    params = set(sig.parameters.keys())
    fetch_cap_param = _pick_alias(params, ["payload_size_cap", "cap", "size_cap"])
    
    if fetch_cap_param is None:
        pytest.skip("Fetch-time payload truncation is optional; not supported")

    # Check if enable-time cap is supported
    enable_cap_supported = False
    if enable_fn and "payload_size_cap" in enable_params:
        enable_cap_supported = True
    elif configure_fn:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        if _pick_alias(cfg_sig, ["payload_size_cap", "cap", "size_cap"]):
            enable_cap_supported = True
    
    if not enable_cap_supported:
        pytest.skip("Enable-time payload cap not supported; cannot test precedence")

    room = "__t:cap-precedence__"

    # Set enable-time cap to 10
    if enable_fn and "payload_size_cap" in enable_params:
        kwargs = {"room": room, "payload_size_cap": 10}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        cap_key = _pick_alias(cfg_sig, ["payload_size_cap", "cap", "size_cap"])
        kwargs = {"room": room, "enabled": True, cap_key: 10}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        configure_fn(**kwargs)

    sio.emit("text", "abcdefghij", room=room)
    
    # Fetch with smaller cap (5); should override enable-time cap (10)
    hist = get_history(room=room, limit=10, namespace="/", payload_size_cap=5)
    txt = next(e for e in hist if e["event"] == "text")["data"]
    assert txt == "abcde", "Fetch-time cap should take precedence"

def test_cross_room_isolation_same_namespace():
    """Different rooms in same namespace must have isolated history."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    r1, r2 = "__t:rooms:1__", "__t:rooms:2__"

    if enable_fn:
        kwargs = {}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(room=r1, **kwargs)
        enable_fn(room=r2, **kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        base = {"enabled": True}
        if "namespace" in cfg_sig:
            base["namespace"] = "/"
        configure_fn(room=r1, **base)
        configure_fn(room=r2, **base)

    sio.emit("a", 1, room=r1)
    sio.emit("b", 2, room=r2)

    h1 = get_history(room=r1, limit=10, namespace="/")
    h2 = get_history(room=r2, limit=10, namespace="/")

    assert any(e["event"] == "a" for e in h1)
    assert not any(e["event"] == "b" for e in h1)
    assert any(e["event"] == "b" for e in h2)
    assert not any(e["event"] == "a" for e in h2)


def test_stats_required_with_size_eviction():
    """Stats getter must return required fields with size eviction tracking."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    stats_fn, fields_alias = discover_stats_getter(sio)
    assert stats_fn is not None, "Spec requires basic stats for observability"

    enable_fn, _, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:stats__"

    configured = False
    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        if "max_entries" in enable_params:
            kwargs["max_entries"] = 3
        enable_fn(**kwargs)
        configured = True

        # Also try to configure via configure_fn if max_entries not in enable
        if "max_entries" not in enable_params and configure_fn:
            cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
            max_key = _pick_alias(cfg_sig, ["max_entries", "max", "limit"])
            if max_key:
                cfg_kwargs = {"room": room, "enabled": True, max_key: 3}
                if "namespace" in cfg_sig:
                    cfg_kwargs["namespace"] = "/"
                try:
                    configure_fn(**cfg_kwargs)
                except TypeError:
                    pass
    elif configure_fn:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        cfg_kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            cfg_kwargs["namespace"] = "/"
        max_key = _pick_alias(cfg_sig, ["max_entries", "max", "limit"])
        assert max_key, "Spec requires size limit parameter"
        cfg_kwargs[max_key] = 3
        configure_fn(**cfg_kwargs)
        configured = True

    assert configured, "Spec requires per-room enable/configuration"

    s0 = stats_fn(room=room, namespace="/")
    assert isinstance(s0, dict)
    keys = pick_stat_keys(s0, fields_alias)

    sio.emit("a", 1, room=room)
    sio.emit("b", 2, room=room)
    sio.emit("c", 3, room=room)
    sio.emit("d", 4, room=room)

    s1 = stats_fn(room=room, namespace="/")
    assert s1[keys["entries"]] >= 0
    assert s1[keys["evict_size"]] >= s0[keys["evict_size"]]

    for k in keys.values():
        assert s1[k] >= 0


def test_disable_stops_new_recordings_and_getter_returns_empty():
    """Disabling history must stop recording and return empty list."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, disable_fn, configure_fn, enable_params = discover_enable_disable_configure(sio)

    assert enable_fn or configure_fn, "Spec requires a per-room enable/configure mechanism."
    assert disable_fn or configure_fn, "Spec requires a way to disable."

    room = "__t:disable:getter__"

    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        if "max_entries" in enable_params:
            kwargs["max_entries"] = 5
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        max_key = _pick_alias(cfg_sig, ["max_entries", "max", "limit"])
        if max_key:
            kwargs[max_key] = 5
        configure_fn(**kwargs)

    sio.emit("before", {"v": 1}, room=room)
    assert len(get_history(room=room, limit=10, namespace="/")) >= 1

    if disable_fn:
        disable_fn(room=room, namespace="/")
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": False}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        configure_fn(**kwargs)

    sio.emit("after_disable", {"v": 2}, room=room)
    assert get_history(room=room, limit=10, namespace="/") == []

    if enable_fn:
        kwargs = {"room": room}
        if "namespace" in enable_params:
            kwargs["namespace"] = "/"
        enable_fn(**kwargs)
    else:
        cfg_sig = set(inspect.signature(configure_fn).parameters.keys())
        kwargs = {"room": room, "enabled": True}
        if "namespace" in cfg_sig:
            kwargs["namespace"] = "/"
        configure_fn(**kwargs)

    sio.emit("after_reenable", {"v": 3}, room=room)
    reh = get_history(room=room, limit=10, namespace="/")
    assert any(e["event"] == "after_reenable" for e in reh)
    assert not any(e["event"] == "after_disable" for e in reh), \
        "Events emitted while disabled MUST NOT surface after re-enabling"


def test_re_enable_starts_fresh():
    """Re-enabling a room must start with empty history (no retained entries)."""
    sio = _mk_server()
    get_history = discover_get_history(sio)
    enable_fn, disable_fn, configure_fn, enable_params = discover_enable_disable_configure(sio)

    room = "__t:re_enable_fresh__"

    # Enable and emit
    if enable_fn:
        enable_fn(room=room, namespace="/")
    else:
        configure_fn(room=room, enabled=True, namespace="/")

    sio.emit("old_event", {"data": "old"}, room=room)
    assert len(get_history(room=room, limit=10, namespace="/")) == 1

    # Disable
    if disable_fn:
        disable_fn(room=room, namespace="/")
    else:
        configure_fn(room=room, enabled=False, namespace="/")

    # Re-enable
    if enable_fn:
        enable_fn(room=room, namespace="/")
    else:
        configure_fn(room=room, enabled=True, namespace="/")

    # History must be empty after re-enable
    hist = get_history(room=room, limit=10, namespace="/")
    assert hist == [], "Re-enabling must start with fresh history"

    # New events should be recorded
    sio.emit("new_event", {"data": "new"}, room=room)
    hist = get_history(room=room, limit=10, namespace="/")
    assert len(hist) == 1
    assert hist[0]["event"] == "new_event"


@pytest.mark.skip(reason="Non-functional: best-effort/non-blocking not reliably testable")
def test_recording_is_best_effort_and_non_blocking():
    """Placeholder for non-functional requirement."""
    pass


@pytest.mark.skip(reason="Non-functional: single-process/in-memory not verifiable in unit tests")
def test_in_memory_single_process_only():
    """Placeholder for non-functional requirement."""
    pass