""" vacuum """
import logging
import voluptuous as vol
from homeassistant.components.vacuum import (
    VacuumEntity,
    SUPPORT_START,
    SUPPORT_STOP,
    SUPPORT_RETURN_HOME,
    SUPPORT_FAN_SPEED,
    SUPPORT_BATTERY,
    SUPPORT_LOCATE,
    SUPPORT_MAP
)
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from .app.constants import FAN_MODE_NONE, FAN_MODE_ECO, FAN_MODE_NORMAL, FAN_MODE_TURBO
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_SESSION_ID = 'sessionId'
CONF_USER_ID = 'userId'
CONF_DEVICE_ID = 'deviceId'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_SESSION_ID, default=False): cv.string,
    vol.Optional(CONF_USER_ID, default=False): cv.Number,
    vol.Optional(CONF_DEVICE_ID, default=False): cv.Number,
})

MAX_BATTERY = 200

def setup_platform(hass, _, add_devices):
    """ setup_platform """
    instance = hass.data[DOMAIN]['instance']
    add_devices([CongaVacuum(instance)])

class CongaVacuum(VacuumEntity):
    """ CongaVacuum """
    def __init__(self, instance):
        super().__init__()
        self.instance = instance
        self.instance.on('update_device', self.schedule_update_ha_state)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return 'Conga'

    @property
    def state(self):
        return self.instance.device.state

    @property
    def state_attributes(self):
        data = super().state_attributes
        data['clean_mode'] = self.instance.device.clean_mode
        data['robot_x'] = self.instance.map.robot.x
        data['robot_y'] = self.instance.map.robot.y
        data['robot_phi'] = self.instance.map.robot.phi
        data['charger_x'] = self.instance.map.charger.x
        data['charger_y'] = self.instance.map.charger.y
        data['charger_phi'] = self.instance.map.charger.phi
        data['clean_time'] = self.instance.device.clean_time
        data['clean_size'] = self.instance.device.clean_size
        return data

    @property
    def battery_level(self):
        if not self.instance.device.battery_level:
            return None
        return self.instance.device.battery_level * 100 / MAX_BATTERY

    @property
    def fan_speed(self):
        return self.instance.device.fan_mode

    @property
    def fan_speed_list(self):
        return [FAN_MODE_NONE, FAN_MODE_ECO, FAN_MODE_NORMAL, FAN_MODE_TURBO]

    def turn_on(self, **kwargs):
        """ turn_on """
        return self.instance.turn_on()

    def start(self):
        """ start """
        return self.instance.turn_on()

    def start_pause(self, **kwargs):
        """ start_pause """
        return self.instance.turn_on()

    def turn_off(self, **kwargs):
        """ turn_off """
        return self.instance.turn_off()

    def stop(self, **kwargs):
        """ stop """
        return self.instance.turn_off()

    def return_to_base(self, **kwargs):
        """ return_to_base """
        return self.instance.return_home()

    def locate(self, **kwargs):
        """ locate """
        return self.instance.locate()

    def set_fan_speed(self, fan_speed, **kwargs):
        """ set_fan_speed """
        self.instance.set_fan_mode(fan_speed)

    @property
    def supported_features(self):
        # SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_PAUSE | SUPPORT_STOP | SUPPORT_CLEAN_SPOT |
        # SUPPORT_SEND_COMMAND | SUPPORT_START  | SUPPORT_STATUS
        return SUPPORT_START | SUPPORT_STOP | SUPPORT_RETURN_HOME | SUPPORT_FAN_SPEED | \
            SUPPORT_BATTERY | SUPPORT_LOCATE | SUPPORT_MAP
