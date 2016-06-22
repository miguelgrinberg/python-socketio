from socketio.base_manager import BaseManager


class SdManager(BaseManager):

    """
    """

    def initialize(self, server):
        # import pdb; pdb.set_trace()
        super().initialize(server)

    def connect(self, sid, namespace):
        """Register a client connection to a namespace.
        and set the django request object?
        """
        # TODO: process user authentication here?
        # if 'django_request' in self.server.environ[sid]:
        #     print(self.server.environ[sid]['django_request'].user)

        self.enter_room(sid, namespace, None)
        self.enter_room(sid, namespace, sid)
