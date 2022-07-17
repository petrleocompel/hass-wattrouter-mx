from datetime import timedelta
import logging

import async_timeout
import xmltodict

from homeassistant.components.light import LightEntity
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)


from .wattrouter_api import WattrouterApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


SCAN_INTERVAL = timedelta(seconds=60)


class WattrouterCoordinator(DataUpdateCoordinator):

    """My custom coordinator."""
    wattrouter_api = None

    def __init__(self, hass, wattrouter_api: WattrouterApi):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Wattrouter Coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
        )
        self.api = wattrouter_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            with async_timeout.timeout(5):
                resp = await self.api.get_config()
            if resp.status != 200:
                self._available = False
                _LOGGER.error("%s returned %s", resp.url, resp.status)
                return

            return xmltodict.parse(await resp.text())
        except Exception as err:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from Wattrouter"
            )
            raise UpdateFailed(f"Error communicating with API: {err}")
