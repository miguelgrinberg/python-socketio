class SocketIOError(Exception):
    pass


class ConnectionError(SocketIOError):
    pass

 
class ConnectionRefusedError(ConnectionError):
    """
    Raised when connection is refused on the application level
    """
    def __init__(self, info):
        self._info = info

    def get_info(self):
        """
        This method could be overridden in subclass to add extra logic for data output
        """
        return self._info

      
class TimeoutError(SocketIOError):
    pass
