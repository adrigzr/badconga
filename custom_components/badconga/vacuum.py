""" vacuum """
# pylint: disable=unused-argument
import logging
from functools import partial
from homeassistant.components.vacuum import (
    VacuumEntity,
    SUPPORT_START,
    SUPPORT_STOP,
    SUPPORT_STATE,
    SUPPORT_STATUS,
    SUPPORT_RETURN_HOME,
    SUPPORT_FAN_SPEED,
    SUPPORT_BATTERY,
    SUPPORT_LOCATE,
    SUPPORT_MAP
)
from .app.const import FAN_MODE_NONE, FAN_MODE_ECO, FAN_MODE_NORMAL, FAN_MODE_TURBO, MODEL_NAME
from .app.conga import Conga
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

MAX_BATTERY = 200

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """ async_setup_platform """
    if 'instance' in hass.data[DOMAIN] and discovery_info is not None:
        async_add_entities([CongaVacuum(hass.data[DOMAIN]['instance'])])

class CongaVacuum(VacuumEntity):
    """ CongaVacuum """
    def __init__(self, instance: Conga):
        super().__init__()
        self.instance = instance
        self.instance.client.on('update_device', self.schedule_update_ha_state)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return 'Conga'

    @property
    def state(self):
        return self.instance.client.device.state

    @property
    def status(self):
        if self.instance.client.device.charge_status:
            return 'charging'
        return self.instance.client.device.state

    @property
    def state_attributes(self):
        data = super().state_attributes
        data['clean_mode'] = self.instance.client.device.clean_mode
        data['robot_x'] = self.instance.client.map.robot.x
        data['robot_y'] = self.instance.client.map.robot.y
        data['robot_phi'] = self.instance.client.map.robot.phi
        data['charger_x'] = self.instance.client.map.charger.x
        data['charger_y'] = self.instance.client.map.charger.y
        data['charger_phi'] = self.instance.client.map.charger.phi
        data['clean_time'] = self.instance.client.device.clean_time
        data['clean_size'] = self.instance.client.device.clean_size
        data['name'] = self.instance.client.device.alias
        data['model'] = MODEL_NAME[self.instance.client.device.model] if (
            self.instance.client.device.model in MODEL_NAME) else (
                self.instance.client.device.model)
        data['serial'] = self.instance.client.device.serial_number
        data['revision'] = self.instance.client.device.controller_version
        data['firmware'] = self.instance.client.device.firmware_version
        data['registered'] = self.instance.client.device.utc_registered
        return data

    @property
    def battery_level(self):
        if not self.instance.client.device.battery_level:
            return None
        return self.instance.client.device.battery_level * 100 / MAX_BATTERY

    @property
    def fan_speed(self):
        return self.instance.client.device.fan_mode

    @property
    def fan_speed_list(self):
        return [FAN_MODE_NONE, FAN_MODE_ECO, FAN_MODE_NORMAL, FAN_MODE_TURBO]

    def start(self, **kwargs):
        """ start """
        return self.instance.client.turn_on()

    async def async_start(self, **kwargs):
        await self.hass.async_add_executor_job(partial(self.start, **kwargs))

    def stop(self, **kwargs):
        """ stop """
        return self.instance.client.turn_off()

    async def async_stop(self, **kwargs):
        await self.hass.async_add_executor_job(partial(self.stop, **kwargs))

    def return_to_base(self, **kwargs):
        """ return_to_base """
        return self.instance.client.return_home()

    def locate(self, **kwargs):
        """ locate """
        return self.instance.client.locate()

    def set_fan_speed(self, fan_speed, **kwargs):
        """ set_fan_speed """
        self.instance.client.set_fan_mode(fan_speed)

    @property
    def supported_features(self):
        return \
            SUPPORT_STOP | \
            SUPPORT_RETURN_HOME | \
            SUPPORT_FAN_SPEED | \
            SUPPORT_BATTERY | \
            SUPPORT_STATUS | \
            SUPPORT_LOCATE | \
            SUPPORT_MAP | \
            SUPPORT_STATE | \
            SUPPORT_START
            # SUPPORT_CLEAN_SPOT | \
            # SUPPORT_SEND_COMMAND | \
            # SUPPORT_TURN_ON | \
            # SUPPORT_TURN_OFF | \
            # SUPPORT_PAUSE | \
