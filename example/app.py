import eventlet
eventlet.monkey_patch()

import time
from threading import Thread
import eventlet
from eventlet import wsgi
from flask import Flask, render_template
from socketio import Server as SocketIOServer
from socketio import Middleware as SocketIOMiddleware

socketio = SocketIOServer(logger=True)
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(10)
        count += 1
        socketio.emit('my response',
                      {'data': 'Server generated event'}, namespace='/test')


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(sid, message):
    socketio.emit('my response', {'data': message['data']},
                  room=sid, namespace='/test')


@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(sid, message):
    socketio.emit('my response', {'data': message['data']},
                  namespace='/test')


@socketio.on('join', namespace='/test')
def join(sid, message):
    socketio.enter_room(sid, message['room'], namespace='/test')
    socketio.emit('my response',
                  {'data': 'Entered room: ' + message['room']},
                  room=sid, namespace='/test')


@socketio.on('leave', namespace='/test')
def leave(sid, message):
    socketio.leave_room(sid, message['room'], namespace='/test')
    socketio.emit('my response',
                  {'data': 'Left room: ' + message['room']},
                  room=sid, namespace='/test')


@socketio.on('close room', namespace='/test')
def close(sid, message):
    socketio.emit('my response',
                  {'data': 'Room ' + message['room'] + ' is closing.'},
                  room=message['room'], namespace='/test')
    socketio.close_room(message['room'], namespace='/test')


@socketio.on('my room event', namespace='/test')
def send_room_message(sid, message):
    socketio.emit('my response', {'data': message['data']},
                  room=message['room'], namespace='/test')


@socketio.on('disconnect request', namespace='/test')
def disconnect_request(sid):
    socketio.disconnect(sid, namespace='/test')


@socketio.on('connect', namespace='/test')
def test_connect(sid, environ):
    socketio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
                  namespace='/test')


@socketio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')


if __name__ == '__main__':
    app = SocketIOMiddleware(socketio, app)
    wsgi.server(eventlet.listen(('', 5000)), app)
