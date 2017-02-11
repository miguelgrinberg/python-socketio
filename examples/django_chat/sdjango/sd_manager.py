from socketio.base_manager import BaseManager


class SdManager(BaseManager):

    """Currently, there is no need to use custom manager
    """

    def initialize(self, server):
        super().initialize(server)

    def connect(self, sid, namespace):
        """Register a client connection to a namespace.
        and set the django request object?
        """

        self.enter_room(sid, namespace, None)
        self.enter_room(sid, namespace, sid)
