```markdown
# python-socketio

[![Build Status](https://img.shields.io/travis/miguelgrinberg/python-socketio/master.svg)](https://travis-ci.org/miguelgrinberg/python-socketio)
[![Codecov](https://img.shields.io/codecov/c/github/miguelgrinberg/python-socketio.svg)](https://codecov.io/gh/miguelgrinberg/python-socketio)

Python implementation of the Socket.IO realtime client and server.

## Sponsors

The following organizations are funding this project:

- **Socket.IO**
- **Socket.IO Add your company here!**

Many individual sponsors also support this project through small ongoing contributions. Why not join them?

## Features

- Real-time communication using WebSockets (or long-polling for older browsers)
- Full support for both client and server-side Socket.IO in Python
- Event-based communication for interactive applications (e.g., chat apps, live updates, gaming)
- Easy integration with Flask, Django, or other Python frameworks
- **Supports Socket.IO protocol versions 3.x, 4.x, and 5.x**

## Version Compatibility

The Socket.IO protocol has gone through several revisions, and some of these revisions are **not backward-compatible**. For smooth operation, it's important that both the Python client and the JavaScript server use compatible versions of Socket.IO. 

### **Socket.IO Version Compatibility Chart**

To ensure compatibility between your `python-socketio` client and your JavaScript Socket.IO server, refer to the following table:

| **JavaScript Socket.IO Version** | **Socket.IO Protocol Revision** | **Engine.IO Protocol Revision** | **python-socketio Version** |
|----------------------------------|---------------------------------|---------------------------------|-----------------------------|
| 0.9.x                            | 1, 2                             | 1, 2                             | Not supported              |
| 1.x and 2.x                      | 3, 4                             | 3                               | 4.x                         |
| 3.x and 4.x                      | 5                               | 4                               | 5.x                         |

### **How This Affects You**

- **Socket.IO version 0.9.x**: Not supported by `python-socketio`. You'll need to upgrade to a newer version.
- **Socket.IO versions 1.x and 2.x**: Use `python-socketio` version 4.x for compatibility.
- **Socket.IO versions 3.x and 4.x**: Use `python-socketio` version 5.x to ensure compatibility with the latest protocol revisions.

### **How to Ensure Compatibility**

1. **Check the version of Socket.IO on the server**: If you're using a JavaScript-based server, check the version of Socket.IO installed by running `npm list socket.io` on the server.
   
2. **Check the version of `python-socketio`**: On the Python client, verify that you're using the correct version of `python-socketio`. Install a specific version using:

   ```bash
   pip install python-socketio==<version>
   ```

3. **Match versions**: Refer to the compatibility chart above to ensure that your Python client version matches the JavaScript server version.

4. **Stay up-to-date**: Socket.IO evolves, so make sure both your client and server are using versions that are actively maintained and compatible.

### **Upgrading or Downgrading Versions**

If you need to upgrade or downgrade the version of either the server or the client, it's important to test your application thoroughly after the change. You may need to adjust event handling or other parts of your app to accommodate the changes in the protocol or library.

## Installation

To install the latest stable version of `python-socketio`, simply run:

```bash
pip install python-socketio
```

If you need a specific version (for compatibility reasons, as outlined above), you can install it like so:

```bash
pip install python-socketio==5.0.0
```

For development versions, use:

```bash
pip install git+https://github.com/miguelgrinberg/python-socketio.git
```

## Usage

Here’s a basic example to get you started with `python-socketio` as both a client and server.

### Server Example

```python
import socketio

# Create a new Socket.IO server instance
sio = socketio.Server()

# Create a new WSGI application
app = socketio.WSGIApp(sio)

# Event handler for when a client connects
@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

# Event handler for when a client sends a message
@sio.event
def message(sid, data):
    print(f"Message from {sid}: {data}")
    sio.send(sid, "Hello from server!")

# Event handler for when a client disconnects
@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Running the app with a WSGI server (e.g., Flask, Django, or a simple server)
if __name__ == '__main__':
    import os
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app)
```

### Client Example

```python
import socketio

# Create a new Socket.IO client instance
sio = socketio.Client()

# Connect to the Socket.IO server
sio.connect('http://localhost:5000')

# Send a message to the server
sio.send("Hello from client!")

# Event handler for messages from the server
@sio.event
def message(data):
    print(f"Message from server: {data}")

# Event handler for when the connection is established
@sio.event
def connect():
    print("Connected to server")

# Event handler for when the client disconnects
@sio.event
def disconnect():
    print("Disconnected from server")

# Keep the client running to listen for events
sio.wait()
```

## Documentation

- **[Official Documentation](https://python-socketio.readthedocs.io/)**: Comprehensive information on using `python-socketio`.
- **[PyPI](https://pypi.org/project/python-socketio/)**: Python Package Index page for installation and version details.
- **[Change Log](https://github.com/miguelgrinberg/python-socketio/blob/master/CHANGELOG.md)**: History of updates and changes.
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/python-socketio)**: If you have questions, check out the community discussions or ask your own!

## How to Contribute

If you find bugs or areas that need improvement in the documentation or the code, feel free to contribute!

1. **Fork the repository**: Start by forking the repository from [python-socketio's GitHub page](https://github.com/miguelgrinberg/python-socketio).
2. **Make your changes**: Edit the code or documentation files as needed.
3. **Submit a pull request**: Once your changes are ready, submit a pull request for review.

Your contributions help improve the project for everyone!

## License

`python-socketio` is licensed under the [MIT License](LICENSE).
```

### Explanation of the Content:

- **Badges**: At the top, there are status badges (build status and code coverage) which indicate the current health of the project.
- **Sponsors Section**: Highlights the organizations and individuals who are supporting the project.
- **Version Compatibility**: A detailed chart explaining which versions of `python-socketio` work with which versions of the JavaScript Socket.IO server.
- **Installation**: Instructions for installing the library using `pip`, including installation for specific versions and development versions.
- **Usage Examples**: Both server-side and client-side examples to help users get started quickly.
- **Documentation Links**: Links to the official documentation, PyPI, change log, and Stack Overflow for support.
- **How to Contribute**: Encourages users to fork the repo, make changes, and contribute back to the project.
- **License**: The project is licensed under the MIT License.