django-socketio
===============

This is an example Django application integrated with Socket.IO.

You can run it with the Django development web server:

```bash
python manage.py runserver
```

When running in this mode, you will get an error message:

    RuntimeError: Cannot obtain socket from WSGI environment.

This is expected, and it happens because the Django web server does not support
the WebSocket protocol. You can ignore the error, as the server will still work
using long-polling.

To run the application with WebSocket enabled, you can use the Gunicorn web
server as follows:

    gunicorn -b :8000 --threads 100 --access-logfile - django_socketio.wsgi:application

See the documentation for information on other supported deployment methods
that you can use to add support for WebSocket.
