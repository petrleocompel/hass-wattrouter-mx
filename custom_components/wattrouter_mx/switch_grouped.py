"""Wattrouter Switches"""
from datetime import timedelta
import xmltodict
import dicttoxml
import logging
from typing import Any, Callable, Dict, List, Optional

import async_timeout

from homeassistant import config_entries, core
from homeassistant.core import callback

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNKNOWN
from .switch_base import BaseWattrouterSwitch

from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .signature_generator import generate_signature
from .coordinator import WattrouterCoordinator
from .wattrouter_api import WattrouterApi
from .const import (
    DOMAIN,
    WR_ENABLE_BIT,
    WR_DISABLE_BIT,
)


_LOGGER = logging.getLogger(__name__)


class GroupedWattrouterSwitch(CoordinatorEntity, SwitchEntity, BaseWattrouterSwitch):
    coordinator: WattrouterCoordinator

    def __init__(self, coordinator: WattrouterCoordinator, eeids: list[str], name):
        super().__init__(coordinator)
        self._eeids = eeids
        self._name = name
        self._state = None
        self._available = False
        self._unique_id = "wattrouter-" + ('|'.join(eeids))

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
        _LOGGER.debug("Device %s - availability: %s", self._name, self._available)
        return self._available

    async def async_turn_on(self):
        """Turn the entity on."""
        _LOGGER.debug(
            "Sending ON request to SWITCH devices %s (%s)", ','.join(self._eeids), self._name
        )
        try:
            config = await self.get_config()
            for item in self._eeids:
                config["conf"][item]["M"] = config["conf"][item]["M"][:-1] + WR_ENABLE_BIT
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
        mvalue = self.coordinator.data["conf"][self._eeids[0]]["M"]
        current = mvalue[-1]
        _LOGGER.debug("Current status: %s, m value: %s, resOff: %s, resOn: %s", current, mvalue,
                     current == WR_DISABLE_BIT, current == WR_ENABLE_BIT)
        if current == WR_ENABLE_BIT:
            self._state = STATE_ON
        elif current == WR_DISABLE_BIT:
            self._state = STATE_OFF
        else:
            self._state = STATE_UNKNOWN
        self._available = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        """Turn Off method."""
        _LOGGER.debug(
            "Sending OFF request to SWITCH devices %s (%s)", ','.join(self._eeids), self._name
        )
        try:
            config = await self.get_config()
            for item in self._eeids:
                config["conf"][item]["M"] = config["conf"][item]["M"][:-1] + WR_DISABLE_BIT
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
