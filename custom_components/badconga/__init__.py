""" badconga """
import logging
from .app.conga import Conga

DOMAIN = 'badconga'
CONF_SESSION_ID = 'sessionId'
CONF_USER_ID = 'userId'
CONF_DEVICE_ID = 'deviceId'
CONF_EMAIL = 'email'
CONF_PASSWORD = 'password'

async def async_setup(hass, config):
    """ async_setup """
    conf = config.get(DOMAIN)
    instance = Conga()
    if CONF_EMAIL in conf and CONF_PASSWORD in conf:
        instance.login(conf[CONF_EMAIL], conf[CONF_PASSWORD])
    elif CONF_SESSION_ID in conf and CONF_USER_ID in conf and CONF_DEVICE_ID in conf:
        instance.set_session(conf[CONF_SESSION_ID], conf[CONF_USER_ID], conf[CONF_DEVICE_ID])
    else:
        raise Exception('missing configuration')
    hass.data[DOMAIN] = {
        'instance': instance,
    }
    return True
