""" camera """
# pylint: disable=unused-argument
import logging
from homeassistant.components.camera import PLATFORM_SCHEMA, Camera
from . import DOMAIN
from .app.conga import Conga

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """ async_setup_platform """
    if 'instance' in hass.data[DOMAIN] and discovery_info is not None:
        async_add_entities([CongaCamera(hass.data[DOMAIN]['instance'])])

class CongaCamera(Camera):
    """ CongaCamera """
    def __init__(self, instance: Conga):
        super().__init__()
        self.content_type = 'image/png'
        self.instance = instance
        self.instance.client.on('update_map', self.schedule_update_ha_state)
        self.instance.client.on('update_position', self.schedule_update_ha_state)

    @property
    def name(self):
        return 'Conga'

    def camera_image(self):
        return self.instance.client.map.image
