""" badconga """
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from .app.conga import Conga

DOMAIN = 'badconga'
CONF_SESSION_ID = 'sessionId'
CONF_USER_ID = 'userId'
CONF_DEVICE_ID = 'deviceId'
CONF_EMAIL = 'email'
CONF_PASSWORD = 'password'

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            {
                vol.Required(CONF_EMAIL, default=""): cv.string,
                vol.Required(CONF_PASSWORD, default=""): cv.string,
            },
            {
                vol.Required(CONF_SESSION_ID, default=""): cv.string,
                vol.Required(CONF_USER_ID, default=""): cv.string,
                vol.Optional(CONF_DEVICE_ID, default="us"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """ async_setup """
    conf = config.get(DOMAIN)
    if conf is not None:
        instance = Conga()
        if CONF_EMAIL in conf and CONF_PASSWORD in conf:
            instance.login(conf[CONF_EMAIL], conf[CONF_PASSWORD])
        elif CONF_SESSION_ID in conf and CONF_USER_ID in conf and CONF_DEVICE_ID in conf:
            instance.set_session(conf[CONF_SESSION_ID], conf[CONF_USER_ID], conf[CONF_DEVICE_ID])
        else:
            logging.error('Missing configuration')
        hass.data[DOMAIN] = {
            'instance': instance,
        }
    return True
