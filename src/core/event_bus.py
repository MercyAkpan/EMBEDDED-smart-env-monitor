import logging

class EventBus:
    """
    A simple synchronous event bus.
    Lives ONLY in the Main Process.
    """
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data=None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event_type, data)
                except Exception as e:
                    logging.error(f"Error in event handler for {event_type}: {e}")

# Global Instance
bus = EventBus()
