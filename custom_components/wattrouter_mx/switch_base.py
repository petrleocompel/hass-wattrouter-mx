"""Wattrouter Switches"""
import xmltodict
import dicttoxml
import logging
import async_timeout
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

from .coordinator import WattrouterCoordinator


logging.getLogger('dicttoxml').setLevel(logging.CRITICAL)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class BaseWattrouterSwitch():
    coordinator: WattrouterCoordinator

    async def get_config(self) -> dict:
        with async_timeout.timeout(5):
            resp = await self.coordinator.api.get_config()
        if resp.status != 200:
            _LOGGER.error("%s returned %s", resp.url, resp.status)
            raise Exception("Error in getting data")

        _LOGGER.debug("async_update: %s", resp.text)

        text_config = await resp.text()
        config = xmltodict.parse(text_config)
        self.coordinator.async_set_updated_data(config)
        return config

    async def set_config(self, config: dict):
        config["conf"]["UN"] = self.coordinator.api.username
        config["conf"]["UP"] = self.coordinator.api.password
        new_config = dicttoxml.dicttoxml(config, attr_type=False, root=False).decode("utf-8")

        data = "\n" + "\n" + new_config
        _LOGGER.debug("MX request: %s", data)
        res = await self.coordinator.api.set_config(data)
        _LOGGER.debug("MX response: %s", res)
        if res:
            self.coordinator.async_set_updated_data(config)
        return res
