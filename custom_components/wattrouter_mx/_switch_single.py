"""Wattrouter Switches"""
import xmltodict
import dicttoxml
import logging
import async_timeout
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

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


class BaseWattrouterSwitch(CoordinatorEntity):
    coordinator: WattrouterCoordinator

    def __init__(self, coordinator: WattrouterCoordinator):
        super().__init__(coordinator)

    def get_config(self) -> dict:
        with async_timeout.timeout(5):
            resp = await self.coordinator.api.get_config()
        if resp.status != 200:
            _LOGGER.error("%s returned %s", resp.url, resp.status)
            raise Exception("Error in getting data")

        _LOGGER.debug("async_update: %s", resp.text)

        text_config = await resp.text()
        config = xmltodict.parse(text_config)
        return config

    async def async_turn_on(self):
        """Turn the entity on."""
        _LOGGER.info(
            "Sending ON request to SWITCH device %s (%s)", self._eeid, self._name
        )
        try:
            config = self.get_config()
            config["conf"][self._eeid]["M"] = config["conf"][self._eeid]["M"][:-1] + WR_ENABLE_BIT
            config["conf"]["UN"] = self.coordinator.api.username
            config["conf"]["UP"] = self.coordinator.api.password

            sig = generate_signature(text_config, self.coordinator.api.username, self.coordinator.api.password)
            new_config = dicttoxml.dicttoxml(config, attr_type=False, root=False).decode("utf-8")
            data = "\n" + "\n" + new_config
            #+ "<sig>" + sig + "</sig>"
            _LOGGER.debug("MX request: %s", data)
            res = await self.coordinator.api.set_config(data)
            _LOGGER.debug("MX response: %s", res)
            if res:
                self._state = STATE_ON
                self._available = True
                self.schedule_update_ha_state()
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
            with async_timeout.timeout(5):
                resp = await self.coordinator.api.get_config()
            if resp.status != 200:
                self._available = False
                _LOGGER.error("%s returned %s", resp.url, resp.status)
                return

            text_config = await resp.text()
            config = xmltodict.parse(text_config)
            config["conf"][self._eeid]["M"] = config["conf"][self._eeid]["M"][:-1] + WR_DISABLE_BIT
            config["conf"]["UN"] = self.coordinator.api.username
            config["conf"]["UP"] = self.coordinator.api.password

            sig = generate_signature(text_config, self.coordinator.api.username, self.coordinator.api.password)
            new_config = dicttoxml.dicttoxml(config, attr_type=False, root=False).decode("utf-8")

            data = "\n" + "\n" + new_config
            # + "<sig>" + sig + "</sig>"

            _LOGGER.debug("MX request: %s", data)
            res = await self.coordinator.api.set_config(data)
            _LOGGER.debug("MX response: %s", res)
            if res:
                self._state = STATE_OFF
                self._available = True
                self.schedule_update_ha_state()
            else:
                self._available = False
        except Exception:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from Wattrouter for switch %s", self.name
            )

