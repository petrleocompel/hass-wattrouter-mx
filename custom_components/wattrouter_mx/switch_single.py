"""Wattrouter Switches"""
from datetime import timedelta
import xmltodict
import dicttoxml
import logging
from typing import Any, Callable, Dict, List, Optional
import async_timeout
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)
from .switch_base import BaseWattrouterSwitch
try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNKNOWN

from .signature_generator import generate_signature
from .coordinator import WattrouterCoordinator
from .const import (
    DOMAIN,
    WR_ENABLE_BIT,
    WR_DISABLE_BIT,
)


logging.getLogger('dicttoxml').setLevel(logging.CRITICAL)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class WattrouterSwitch(CoordinatorEntity, SwitchEntity, BaseWattrouterSwitch):
    coordinator: WattrouterCoordinator

    def __init__(self, coordinator: WattrouterCoordinator, eeid: str, name):
        super().__init__(coordinator)
        self._eeid = eeid
        self._name = name
        self._state = None
        self._available = False
        self._unique_id = "wattrouter-" + eeid

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
        """Return is_on status."""
        return self._state == STATE_ON

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def available(self):
        """Return availability."""
        _LOGGER.info("Device %s - availability: %s", self._name, self._available)
        return self._available

    async def async_turn_on(self):
        """Turn the entity on."""
        _LOGGER.info(
            "Sending ON request to SWITCH device %s (%s)", self._eeid, self._name
        )
        try:
            config = await self.get_config()
            config["conf"][self._eeid]["M"] = config["conf"][self._eeid]["M"][:-1] + WR_ENABLE_BIT
            res = await self.set_config(config)
            if res:
                self._state = STATE_ON
                self._available = True
                self.async_write_ha_state()
            else:
                self._available = False
        except Exception:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from Wattrouter for switch %s", self.name
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        mvalue = self.coordinator.data["conf"][self._eeid]["M"]
        current = mvalue[-1]
        _LOGGER.info("Current status: %s, m value: %s, resOff: %s, resOn: %s", current, mvalue,
                     current == WR_DISABLE_BIT, current == WR_ENABLE_BIT)
        if current == WR_ENABLE_BIT:
            self._state = STATE_ON
        elif current == WR_DISABLE_BIT:
            self._state = STATE_OFF
        else:
            self._state = STATE_UNKNOWN
        # self.schedule_update_ha_state()
        # self.async_write_ha_state()
        self._available = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        """Turn Off method."""
        _LOGGER.info(
            "Sending OFF request to SWITCH device %s (%s)", self._eeid, self._name
        )
        try:
            config = await self.get_config()
            config["conf"][self._eeid]["M"] = config["conf"][self._eeid]["M"][:-1] + WR_DISABLE_BIT
            res = await self.set_config(config)
            if res:
                self._state = STATE_OFF
                self._available = True
                self.async_write_ha_state()
            else:
                self._available = False
        except Exception:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from Wattrouter for switch %s", self.name
            )

