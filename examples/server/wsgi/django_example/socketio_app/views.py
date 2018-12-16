# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
async_mode = None

import os

from django.http import HttpResponse
import socketio

basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.Server(async_mode=async_mode)
thread = None


def index(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return HttpResponse(open(os.path.join(basedir, 'static/index.html')))


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('my response', {'data': 'Server generated event'},
                 namespace='/test')


@sio.on('my event', namespace='/test')
def test_message(sid, message):
    sio.emit('my response', {'data': message['data']}, room=sid,
             namespace='/test')


@sio.on('my broadcast event', namespace='/test')
def test_broadcast_message(sid, message):
    sio.emit('my response', {'data': message['data']}, namespace='/test')


@sio.on('join', namespace='/test')
def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    sio.emit('my response', {'data': 'Entered room: ' + message['room']},
             room=sid, namespace='/test')


@sio.on('leave', namespace='/test')
def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/test')
    sio.emit('my response', {'data': 'Left room: ' + message['room']},
             room=sid, namespace='/test')


@sio.on('close room', namespace='/test')
def close(sid, message):
    sio.emit('my response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'], namespace='/test')
    sio.close_room(message['room'], namespace='/test')


@sio.on('my room event', namespace='/test')
def send_room_message(sid, message):
    sio.emit('my response', {'data': message['data']}, room=message['room'],
             namespace='/test')


@sio.on('disconnect request', namespace='/test')
def disconnect_request(sid):
    sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
def test_connect(sid, environ):
    sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
             namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')

