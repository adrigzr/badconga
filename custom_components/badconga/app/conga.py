""" conga """
import logging
import threading
from .client import Client

logger = logging.getLogger(__name__)

class Conga():
    """ Conga """

    # pylint: disable=too-many-instance-attributes
    # maybe put is_* into a State class object

    def __init__(self, email, password, animate):
        super().__init__()
        self.email = email
        self.password = password
        self.animate = animate
        self.is_running = False
        self.is_logged = False
        self.is_device_connected = False
        self.is_inuse = False
        self.timer = None
        self.client = Client()
        self.client.on('login', self.on_login)
        self.client.on('logout', self.on_logout)
        self.client.on('device_inuse', self.on_device_inuse)
        self.client.on('connect_device', self.on_connect_device)
        self.client.on('disconnect_device', self.on_disconnect_device)

    # private

    def loop(self):
        """ loop """
        logger.debug('[loop] is_running=%s, is_logged=%s, is_device_connected=%s, is_inuse=%s',
                     self.is_running, self.is_logged,
                     self.is_device_connected, self.is_inuse)
        if self.is_running:
            if self.is_inuse:
                self.reschedule()
                return None
            if not self.is_logged:
                return self.client.connect(self.email, self.password)
            if not self.is_device_connected:
                return self.client.connect_device()
        if not self.is_running:
            if self.is_device_connected:
                return self.client.disconnect_device()
            if self.is_logged:
                return self.client.logout()
        return None

    def reschedule(self):
        """ reschedule """
        if self.timer:
            return
        self.timer = threading.Timer(60.0, self.resume)
        self.timer.start()

    def resume(self):
        """ resume """
        self.is_inuse = False
        self.timer = None
        self.loop()

    # events

    def on_login(self):
        """ on_login """
        self.is_logged = True
        self.loop()

    def on_logout(self):
        """ on_login """
        self.is_logged = False
        self.is_device_connected = False
        self.loop()

    def on_connect_device(self):
        """ on_connect_device """
        self.is_device_connected = True
        self.client.map.animate = self.animate
        self.loop()

    def on_disconnect_device(self):
        """ on_connect_device """
        self.is_device_connected = False
        self.loop()

    def on_device_inuse(self):
        """ on_device_inuse """
        self.is_inuse = True

    # methods

    def start(self):
        """ start """
        self.is_running = True
        self.loop()

    def stop(self):
        """ logout """
        self.is_running = False
        self.loop()
