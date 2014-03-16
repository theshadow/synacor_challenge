"""Collection of classes for a simplified pubsub pattern.
"""

class PubSub(object):
    @property
    def subscribers(self):
        return self._subscribers

    @subscribers.setter
    def subscribers(self, subscribers):
        self._subscribers = subscribers

    def __init__(self):
        self._subscribers = {}

    def publish(self, event, *args, **kwargs):
        if event not in self.subscribers:
            return

        for subscriber in self.subscribers[event]:
            subscriber(*args, **kwargs)

    def subscribe(self, event, func):
        if event not in self.subscribers:
            self.subscribers[event] = []

        self.subscribers[event].append(func)

    def new_publisher(self):
        publisher = Publisher(manager=self)
        return publisher


class Publisher(object):
    @property
    def manager(self):
        if self._manager is None:
            self._manager = PubSub()
        return self._manager

    @manager.setter
    def manager(self, manager):
        self._manager = manager

    def __init__(self, manager=None):
        self._manager = None

        self.manager = manager

    def publish(self, event, *args, **kwargs):
        self.manager.publish(event, *args, **kwargs)


class PublisherAware(object):
    @property
    def publisher(self):
        if self._pubsub_publisher is None:
            self._pubsub_publisher = Publisher()
        return self._pubsub_publisher

    @publisher.setter
    def publisher(self, publisher):
        self._pubsub_publisher = publisher

    def __init__(self):
        self._pubsub_publisher = None