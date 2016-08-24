class Interceptor(object):
    """Base class for event handler interceptors."""

    def __init__(self, server):
        self.server = server

    def ignore_for(self, event, namespace):
        return False

    def before_event(self, event, namespace, args):
        pass

    def after_event(self, event, namespace, args):
        pass

    def handle_exception(self, event, namespace, exc):
        raise exc
