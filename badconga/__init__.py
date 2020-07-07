""" badconga """
import logging
from .app.conga import Conga

DOMAIN = 'badconga'
CONF_SESSION_ID = 'sessionId'
CONF_USER_ID = 'userId'
CONF_DEVICE_ID = 'deviceId'

async def async_setup(hass, config):
    """ async_setup """
    conf = config.get(DOMAIN)
    instance = Conga()
    instance.set_session(conf[CONF_SESSION_ID], conf[CONF_USER_ID], conf[CONF_DEVICE_ID])
    hass.data[DOMAIN] = {
        'instance': instance,
    }
    return True
