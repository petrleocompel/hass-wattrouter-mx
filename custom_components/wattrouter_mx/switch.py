"""Wattrouter Switches"""
from datetime import timedelta
import logging
from typing import Any, Callable, Dict, List, Optional


from homeassistant import config_entries, core


from homeassistant.const import (
    CONF_ADDRESS,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .switch_single import WattrouterSwitch
from .switch_grouped import GroupedWattrouterSwitch

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity


from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .coordinator import WattrouterCoordinator
from .wattrouter_api import WattrouterApi
from .const import (
    DOMAIN,
)


logging.getLogger('dicttoxml').setLevel(logging.CRITICAL)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)


PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
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
    """Setup entities from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)
    session = async_get_clientsession(hass)
    entities = []
    if config[CONF_ADDRESS] is not None and config[CONF_USERNAME] is not None and config[CONF_PASSWORD] is not None:
        api = WattrouterApi(session, config[CONF_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD])
        coordinator = WattrouterCoordinator(hass, api)
        await coordinator.async_config_entry_first_refresh()
        entities.append(WattrouterSwitch(coordinator, "TS11", "TS11"))
        entities.append(WattrouterSwitch(coordinator, "TS21", "TS21"))
        entities.append(WattrouterSwitch(coordinator, "TS31", "TS31"))
        entities.append(GroupedWattrouterSwitch(coordinator, ["TS11", "TS21", "TS31"], "TS-1-3"))
        entities.append(WattrouterSwitch(coordinator, "TS41", "TS41"))
        entities.append(WattrouterSwitch(coordinator, "TS51", "TS51"))
        entities.append(WattrouterSwitch(coordinator, "TS61", "TS61"))
        entities.append(GroupedWattrouterSwitch(coordinator, ["TS41", "TS51", "TS61"], "TS-4-6"))
    for entity in entities:
        hass.data[DOMAIN]['entities'][entity.unique_id] = entity
    async_add_entities(entities, update_before_add=True)


async def async_setup_platform(
        hass: HomeAssistantType,
        config: ConfigType,
        async_add_entities: Callable,
        discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    entities = []
    if config[CONF_USERNAME] is not None and config[CONF_PASSWORD] is not None:
        api = WattrouterApi(session, config[CONF_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD])
        coordinator = WattrouterCoordinator(hass, api)
        await coordinator.async_config_entry_first_refresh()
        entities.append(WattrouterSwitch(coordinator, "TS11", "TS11"))
        entities.append(WattrouterSwitch(coordinator, "TS21", "TS21"))
        entities.append(WattrouterSwitch(coordinator, "TS31", "TS31"))
        entities.append(GroupedWattrouterSwitch(coordinator, ["TS11", "TS21", "TS31"], "TS-1-3"))
        entities.append(WattrouterSwitch(coordinator, "TS41", "TS41"))
        entities.append(WattrouterSwitch(coordinator, "TS51", "TS51"))
        entities.append(WattrouterSwitch(coordinator, "TS61", "TS61"))
        entities.append(GroupedWattrouterSwitch(coordinator, ["TS41", "TS51", "TS61"], "TS-4-6"))

    for entity in entities:
        hass.data[DOMAIN]['entities'][entity.unique_id] = entity
    async_add_entities(entities, update_before_add=True)

