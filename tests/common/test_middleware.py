import unittest
from unittest import mock

from socketio import middleware


class TestMiddleware(unittest.TestCase):
    def test_wsgi_routing(self):
        mock_wsgi_app = mock.MagicMock()
        mock_sio_app = 'foo'
        m = middleware.Middleware(mock_sio_app, mock_wsgi_app)
        environ = {'PATH_INFO': '/foo'}
        start_response = "foo"
        m(environ, start_response)
        mock_wsgi_app.assert_called_once_with(environ, start_response)

    def test_sio_routing(self):
        mock_wsgi_app = 'foo'
        mock_sio_app = mock.Mock()
        mock_sio_app.handle_request = mock.MagicMock()
        m = middleware.Middleware(mock_sio_app, mock_wsgi_app)
        environ = {'PATH_INFO': '/socket.io/'}
        start_response = "foo"
        m(environ, start_response)
        mock_sio_app.handle_request.assert_called_once_with(
            environ, start_response
        )

    def test_404(self):
        mock_wsgi_app = None
        mock_sio_app = mock.Mock()
        m = middleware.Middleware(mock_sio_app, mock_wsgi_app)
        environ = {'PATH_INFO': '/foo/bar'}
        start_response = mock.MagicMock()
        r = m(environ, start_response)
        assert r == [b'Not Found']
        start_response.assert_called_once_with(
            "404 Not Found", [('Content-Type', 'text/plain')]
        )
