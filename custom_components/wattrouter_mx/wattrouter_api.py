import logging

import async_timeout
import aiohttp

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class WattrouterApi:
    def __init__(self, session: aiohttp.ClientSession, url: str, username: str, password: str):
        self._url = url
        self.username = username
        self.password = password
        self._session = session

    async def set_config(self, data) -> bool:
        async with async_timeout.timeout(10):
            response = await self._session.post(
                self._url + "/conf.xml",
                data=data,
                headers={"Content-Type": "text/xml"}
            )
            if response.status != 200:
                raise ValueError("Invalid response")
            text_response = await response.text()
            _LOGGER.debug("Response from wattrouter: %s", text_response)
            return text_response.__contains__("<Accept>0</Accept>")

    async def get_config(self):
        return await self._session.get(self._url + "/conf.xml")
