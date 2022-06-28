"""Wattrouter Switches"""
from datetime import timedelta
import xmltodict
import dicttoxml
import logging
from typing import Any, Callable, Dict, List, Optional

import async_timeout

from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNKNOWN

from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .wattrouter_api import WattrouterApi
from .dataview import DataView
from .const import (
    DOMAIN,
)
import hashlib


logging.getLogger('dicttoxml').setLevel(logging.CRITICAL)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_entry(
        hass: core.HomeAssistant,
        config_entry: config_entries.ConfigEntry,
        async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)
    session = async_get_clientsession(hass)
    sensors = []
    if config[CONF_ADDRESS] is not None and config[CONF_USERNAME] is not None and config[CONF_PASSWORD] is not None:
        api = WattrouterApi(session, config[CONF_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD])
        sensors.append(WattrouterSwitch(api, "TS41", "TS41"))
        # sensors.append(WattrouterSwitch(api, "TS51", "TS51"))
        # sensors.append(WattrouterSwitch(api, "TS61", "TS61"))
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
        hass: HomeAssistantType,
        config: ConfigType,
        async_add_entities: Callable,
        discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    sensors = []
    if config[CONF_USERNAME] is not None and config[CONF_PASSWORD] is not None:
        api = WattrouterApi(session, config[CONF_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD])
        sensors.append(WattrouterSwitch(api, "TS41", "TS41"))
        # sensors.append(WattrouterSwitch(api, "TS51", "TS51"))
        # sensors.append(WattrouterSwitch(api, "TS61", "TS61"))
    async_add_entities(sensors, update_before_add=True)


WR_ENABLE_BIT = "4"
WR_DISABLE_BIT = "2"


class WattrouterSwitch(SwitchEntity):
    def __init__(self, api: WattrouterApi, eeid, name):
        super().__init__()
        self._eeid = eeid
        self._api = api
        self._name = name
        self._state = None
        self._available = False

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
            with async_timeout.timeout(5):
                resp = await self._api.get_config()
            if resp.status != 200:
                self._available = False
                _LOGGER.error("%s returned %s", resp.url, resp.status)
                return

            _LOGGER.debug("async_update: %s", resp.text)

            text_config = await resp.text()
            config = xmltodict.parse(text_config)
            config["conf"][self._eeid]["M"] = config["conf"][self._eeid]["M"][:-1] + WR_ENABLE_BIT
            config["conf"]["UN"] = self._api.username
            config["conf"]["UP"] = self._api.password

            sig = generate_signature(text_config, self._api.username, self._api.password)
            new_config = dicttoxml.dicttoxml(config, attr_type=False, root=False).decode("utf-8")
            data = "\n" + "\n" + new_config
            #+ "<sig>" + sig + "</sig>"
            _LOGGER.debug("MX request: %s", data)
            res = await self._api.set_config(data)
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

    async def async_update(self):
        try:
            with async_timeout.timeout(5):
                resp = await self._api.get_config()
            if resp.status != 200:
                self._available = False
                _LOGGER.error("%s returned %s", resp.url, resp.status)
                return


            config = xmltodict.parse(await resp.text())
            mvalue = config["conf"][self._eeid]["M"]
            current = config["conf"][self._eeid]["M"][-1]
            _LOGGER.info("Current status: %s, m value: %s, resOff: %s, resOn: %s", current, mvalue, current == WR_DISABLE_BIT, current == WR_ENABLE_BIT)
            if current == WR_ENABLE_BIT:
                self._state = STATE_ON
            elif current == WR_DISABLE_BIT:
                self._state = STATE_OFF
            else:
                self._state = STATE_UNKNOWN
            #self.schedule_update_ha_state()
            #self.async_write_ha_state()
            self._available = True
        except Exception:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from Wattrouter for switch %s", self.name
            )

    async def async_turn_off(self):
        """Turn Off method."""
        _LOGGER.info(
            "Sending OFF request to SWITCH device %s (%s)", self._eeid, self._name
        )
        try:
            with async_timeout.timeout(5):
                resp = await self._api.get_config()
            if resp.status != 200:
                self._available = False
                _LOGGER.error("%s returned %s", resp.url, resp.status)
                return

            text_config = await resp.text()
            config = xmltodict.parse(text_config)
            config["conf"][self._eeid]["M"] = config["conf"][self._eeid]["M"][:-1] + WR_DISABLE_BIT
            config["conf"]["UN"] = self._api.username
            config["conf"]["UP"] = self._api.password

            sig = generate_signature(text_config, self._api.username, self._api.password)
            new_config = dicttoxml.dicttoxml(config, attr_type=False, root=False).decode("utf-8")

            data = "\n" + "\n" + new_config
            # + "<sig>" + sig + "</sig>"

            _LOGGER.debug("MX request: %s", data)
            res = await self._api.set_config(data)
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


def generate_signature(config: str, user: str, password: str) -> str:
    #_LOGGER.debug("po user admin %", po(user, 16))
    un = "455156572e" #sigdata(po(user, 16))
    pr = "e3e5e7f4" #sigdata(po(password, 16))
    pf = config + un + pr
    return hashlib.sha256(pf.encode('utf-8')).hexdigest()


def sigdata(data) -> str:
    pl = DataView(data)
    counter = 0
    byte_length = pl.byte_length
    pm = ''

    while counter < byte_length:
        hex_num = hex(pl.get_uint_8(counter))
        if len(hex_num) < 2:
            hex_num = "0" + hex_num
        pm += hex_num
        counter += 1

    return pm


def po(src: str, length: int):
    ef = 0
    dR = len(src)
    if dR > length:
        dR = length
    pq = []
    _LOGGER.info("shit src %s, length %s, dR %s, ", src, length, dR)
    while ef < length and ef < dR:
        pq.append(ord(src[ef]) - 0x80)
        _LOGGER.info("shit ef %s, dR %s", ef, dR)
        if ef < (dR - 1):
            pq[ef] += ord(src[ef+1])
        else:
            pq[ef] += 0x40
        ef += 1
    return pq
