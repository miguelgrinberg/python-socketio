import six


class BaseManager(object):
    """Manage client connections.

    This class keeps track of all the clients and the rooms they are in, to
    support the broadcasting of messages. The data used by this class is
    stored in a memory structure, making it appropriate only for single process
    services. More sophisticated storage backends can be implemented by
    subclasses.
    """
    def __init__(self, server):
        self.server = server
        self.rooms = {}
        self.pending_removals = []

    def get_namespaces(self):
        """Return an iterable with the active namespace names."""
        return six.iterkeys(self.rooms)

    def get_participants(self, namespace, room):
        """Return an iterable with the active participants in a room."""
        for sid, active in six.iteritems(self.rooms[namespace][room]):
            if active:
                yield sid
        self._clean_rooms()

    def connect(self, sid, namespace):
        """Register a client connection to a namespace."""
        self.enter_room(sid, namespace, None)
        self.enter_room(sid, namespace, sid)

    def is_connected(self, sid, namespace):
        return sid in self.rooms[namespace][None] and \
            self.rooms[namespace][None][sid]

    def disconnect(self, sid, namespace):
        """Register a client disconnect from a namespace."""
        rooms = []
        for room_name, room in six.iteritems(self.rooms[namespace]):
            if sid in room:
                rooms.append(room_name)
        for room in rooms:
            self.leave_room(sid, namespace, room)

    def enter_room(self, sid, namespace, room):
        """Add a client to a room."""
        if namespace not in self.rooms:
            self.rooms[namespace] = {}
        if room not in self.rooms[namespace]:
            self.rooms[namespace][room] = {}
        self.rooms[namespace][room][sid] = True

    def leave_room(self, sid, namespace, room):
        """Remove a client from a room."""
        try:
            # do not delete immediately, just mark the client as inactive
            # _clean_rooms() will do the clean up when it is safe to do so
            self.rooms[namespace][room][sid] = False
            self.pending_removals.append((namespace, room, sid))
        except KeyError:
            pass

    def close_room(self, namespace, room):
        """Remove all participants from a room."""
        try:
            for sid in self.get_participants(namespace, room):
                self.leave_room(sid, namespace, room)
        except KeyError:
            pass

    def get_rooms(self, sid, namespace):
        """Return the rooms a client is in."""
        r = []
        for room_name, room in six.iteritems(self.rooms[namespace]):
            if room_name is not None and sid in room and room[sid]:
                r.append(room_name)
        return r

    def emit(self, event, data, namespace, room=None, skip_sid=None,
             callback=None):
        """Emit a message to a single client, a room, or all the clients
        connected to the namespace."""
        if namespace not in self.rooms or room not in self.rooms[namespace]:
            return
        for sid in self.get_participants(namespace, room):
            if sid != skip_sid:
                self.server._emit_internal(sid, event, data, namespace,
                                           callback)

    def _clean_rooms(self):
        """Remove all the inactive room participants."""
        for namespace, room, sid in self.pending_removals:
            try:
                del self.rooms[namespace][room][sid]
            except KeyError:
                # failures here could mean there were duplicates so we ignore
                continue
            if len(self.rooms[namespace][room]) == 0:
                del self.rooms[namespace][room]
                if len(self.rooms[namespace]) == 0:
                    del self.rooms[namespace]
        self.pending_removals = []
