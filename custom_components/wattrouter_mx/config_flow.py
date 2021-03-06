
from .const import DOMAIN
from homeassistant.const import CONF_ADDRESS, CONF_PASSWORD, CONF_USERNAME
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from typing import Any, Optional, Dict

import voluptuous as vol


class WattrouterMxCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """WattrouterMx Custom config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            self.data = user_input
            return self.async_create_entry(title="Wattrouter MX", data=self.data, description=self.data[CONF_ADDRESS])
        else:
            user_input = {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS, default=user_input.get(CONF_ADDRESS, vol.UNDEFINED), msg="Address - http://ip"): cv.string,
                    vol.Required(CONF_USERNAME, default=user_input.get(CONF_ADDRESS, "admin"), msg="Username"): cv.string,
                    vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, vol.UNDEFINED), msg="Password"): cv.string,
                }
            ),
            errors=errors,
        )
