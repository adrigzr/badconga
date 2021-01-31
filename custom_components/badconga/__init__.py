""" badconga """
# pylint: disable=unused-argument
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from .app.conga import Conga
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_ANIMATE

VERSION = '0.0.0-development'

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_EMAIL, default=""): cv.string,
        vol.Required(CONF_PASSWORD, default=""): cv.string,
        vol.Optional(CONF_ANIMATE, default=False): cv.boolean,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """ async_setup """
    if DOMAIN not in config:
        return True
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]['config'] = dict(config[DOMAIN])

    data = hass.data[DOMAIN]['config']

    if CONF_EMAIL in data and CONF_PASSWORD in data:
        instance = Conga(data[CONF_EMAIL],
                         data[CONF_PASSWORD],
                         data[CONF_ANIMATE])
        instance.start()
        hass.data[DOMAIN]['instance'] = instance
        await hass.helpers.discovery.async_load_platform('vacuum', DOMAIN, {}, config)
        await hass.helpers.discovery.async_load_platform('camera', DOMAIN, {}, config)
    else:
        logging.error('Missing configuration')

    return True
