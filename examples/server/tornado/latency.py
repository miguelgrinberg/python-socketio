import os

import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

import socketio

define("port", default=5000, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

sio = socketio.AsyncServer(async_mode="tornado")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("latency.html")


@sio.event
async def ping_from_client(sid):
    await sio.emit("pong_from_server", room=sid)


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/socket.io/", socketio.get_tornado_handler(sio)),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
    )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
