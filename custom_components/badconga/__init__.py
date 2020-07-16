""" badconga """
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from .app.conga import Conga
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD

VERSION = '0.0.0-development'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_EMAIL, default=""): cv.string,
        vol.Required(CONF_PASSWORD, default=""): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """ async_setup """
    if DOMAIN not in config:
        return True
    data = dict(config.get(DOMAIN))
    if CONF_EMAIL in data and CONF_PASSWORD in data:
        instance = Conga(data[CONF_EMAIL], data[CONF_PASSWORD])
        instance.start()
        hass.data[DOMAIN] = {
            'instance': instance,
        }
    else:
        logging.error('Missing configuration')
    return True
