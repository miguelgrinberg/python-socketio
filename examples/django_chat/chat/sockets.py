import logging
from sdjango import namespace


online_user_num = 0


@namespace('/test')
class TestNamespace:

    def __init__(self, name):
        self.name = name
        self.request = None  # django request object

    def _get_socket(self, sid):
        socket = namespace.server.eio._get_socket(sid)
        return socket

    def _get_request(self, sid):
        socket = self._get_socket(sid)
        return socket._request

    def emit(self, *args, **kwargs):
        if 'namespace' not in kwargs:
            kwargs['namespace'] = self.name

        namespace.server.emit(*args, **kwargs)

    def on_my_event(self, sid, message):
        self.emit('my response', {'data': message['data']}, room=sid)

    def on_my_broadcast_event(self, sid, message):
        self.emit('my response', {'data': message['data']})

    def on_join(self, sid, message):
        namespace.server.enter_room(sid, message['room'], namespace='/test')
        self.emit('my response', {'data': 'Entered room: '+message['room']}, room=sid)

    def on_leave(self, sid, message):
        namespace.server.leave_room(sid, message['room'], namespace='/test')
        self.emit('my response', {'data': 'Left room:'+message['room']}, room=sid)

    def on_close_room(self, sid, message):
        self.emit('my response', {'data': 'Room '+message['room']+ ' is closing'},
                 room=message['room'])
        namespace.server.close_room(message['room'], namespace='/test')

    def on_my_room_event(self, sid, message):
        self.emit('my response', {'data': message['data']}, room=message['room'])

    def on_disconnect_request(self, sid):
        namespace.server.disconnect(sid, namespace='/test')

    # two method must have
    def on_connect(self, sid, environ):
        if 'django_request' in environ:
            request = environ['django_request']
            socket = self._get_socket(sid)
            socket._request = request

        self.emit('my response', {'data': "{} Connected".format(request.user), "count": 0}, room=sid)

    def on_disconnect(self, sid):
        print('Client disconnected')
