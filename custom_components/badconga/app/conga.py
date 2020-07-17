""" conga """
import logging
from .client import Client

logger = logging.getLogger(__name__)

class Conga():
    """ Conga """
    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password
        self.is_running = False
        self.is_logged = False
        self.is_device_connected = False
        self.client = Client()
        self.client.on('login', self.on_login)
        self.client.on('logout', self.on_logout)
        self.client.on('connect_device', self.on_connect_device)
        self.client.on('disconnect_device', self.on_disconnect_device)

    # private

    def loop(self):
        """ loop """
        logger.debug('[loop] is_running=%s, is_logged=%s, is_device_connected=%s',
                     self.is_running, self.is_logged, self.is_device_connected)
        if self.is_running:
            if not self.is_logged:
                return self.client.login(self.email, self.password)
            if not self.is_device_connected:
                return self.client.connect_device()
        if not self.is_running:
            if self.is_device_connected:
                return self.client.disconnect_device()
            if self.is_logged:
                return self.client.logout()
        return None

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
        self.loop()

    def on_disconnect_device(self):
        """ on_connect_device """
        self.is_device_connected = False
        self.loop()

    # methods

    def start(self):
        """ login """
        self.is_running = True
        self.loop()

    def stop(self):
        """ logout """
        self.is_running = False
        self.loop()
