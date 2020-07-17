""" evented """
# pylint: disable=invalid-name
import logging
import threading

logger = logging.getLogger(__name__)

class Evented:
    """ Evented """
    callbacks = None

    def __init__(self):
        self.callbacks = {}

    def on(self, event_name, callback):
        """ on """
        if event_name not in self.callbacks:
            self.callbacks[event_name] = [callback]
        else:
            self.callbacks[event_name].append(callback)

    def trigger(self, event_name, args=None):
        """ trigger """
        logger.debug('triggering %s', event_name)
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                if args:
                    threading.Thread(target=callback, args=[args]).start()
                else:
                    threading.Thread(target=callback).start()
