python-socketio
===============

.. image:: https://github.com/miguelgrinberg/python-socketio/workflows/build/badge.svg
    :target: https://github.com/miguelgrinberg/python-socketio/actions

.. image:: https://codecov.io/gh/miguelgrinberg/python-socketio/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/miguelgrinberg/python-socketio

Python implementation of the `Socket.IO`_ realtime client and server.

Version compatibility
---------------------

The Socket.IO protocol has been through a number of revisions, and some of these
introduced backward incompatible changes, which means that the client and the
server must use compatible versions for everything to work.

If you are using the Python client and server, the easiest way to ensure compatibility
is to use the same version of this package for the client and the server. If you are
using this package with a different client or server, then you must ensure the
versions are compatible.

The version compatibility chart below maps versions of this package to versions
of the JavaScript reference implementation and the versions of the Socket.IO and
Engine.IO protocols.

+------------------------------+-----------------------------+-----------------------------+-------------------------+
| JavaScript Socket.IO version | Socket.IO protocol revision | Engine.IO protocol revision | python-socketio version |
+==============================+=============================+=============================+=========================+
| 0.9.x                        | 1, 2                        | 1, 2                        | Not supported           |
+------------------------------+-----------------------------+-----------------------------+-------------------------+
| 1.x and 2.x                  | 3, 4                        | 3                           | 4.x                     |
+------------------------------+-----------------------------+-----------------------------+-------------------------+
| 3.x and 4.x                  | 5                           | 4                           | 5.x                     |
+------------------------------+-----------------------------+-----------------------------+-------------------------+

Resources
---------

-  `Documentation`_
-  `PyPI`_
-  `Change Log`_
-  Questions? See the `questions`_ others have asked on Stack Overflow, or `ask`_ your own question.

.. _Socket.IO: https://github.com/socketio/socket.io
.. _Documentation: http://python-socketio.readthedocs.io/en/latest/
.. _PyPI: https://pypi.python.org/pypi/python-socketio
.. _Change Log: https://github.com/miguelgrinberg/python-socketio/blob/master/CHANGES.md
.. _questions: https://stackoverflow.com/questions/tagged/python-socketio
.. _ask: https://stackoverflow.com/questions/ask?tags=python+python-socketio
