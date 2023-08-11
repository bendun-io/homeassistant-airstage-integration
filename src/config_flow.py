"""Config flow for the MELCloud platform."""
from __future__ import annotations

import asyncio
from http import HTTPStatus

from aiohttp import ClientError, ClientResponseError
from async_timeout import timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_TOKEN, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.issue_registry import async_create_issue
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    selector
)

import uuid
from .const import DOMAIN, CONF_BASEURL, CONF_BASEURL_SELECTOR, DUMMY_DEVICE_TOKEN
from . import airstagecommands

import logging
_LOGGER = logging.getLogger(__name__)


class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def _create_entry(self, username: str, baseurl:str, thePassword:str, token: str):
        """Register new entry."""
        await self.async_set_unique_id(username)
        
        self._abort_if_unique_id_configured({CONF_TOKEN: token})
        
        return self.async_create_entry(
            title=username, data={CONF_USERNAME: username, CONF_BASEURL: baseurl, CONF_PASSWORD: thePassword, CONF_TOKEN: token}
        )

    async def _create_client(
        self,
        username: str,
        *,
        password: str | None = None,
        token: str | None = None,
        baseurl: str | None = None,
    ):
        """Create client."""
        try:
            async with timeout(10):
                if (acquired_token := token) is None:
                    acquired_token = await airstagecommands.login(
                        baseurl, username, password, "Germany", "de", # TODO parameters, Germany and de
                        requestModule=async_get_clientsession(self.hass)
                    )
                # airstagecommands.getDevices(baseurl, acquired_token)
        except ClientResponseError as err:
            if err.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                async_create_issue(
                    self.hass, self.context["source"], "invalid_auth"
                )
                return self.async_abort(reason="invalid_auth")
            await async_create_issue(
                self.hass, self.context["source"], "cannot_connect"
            )
            return self.async_abort(reason="cannot_connect")
        except (asyncio.TimeoutError, ClientError):
            await async_create_issue(
                self.hass, self.context["source"], "cannot_connect"
            )
            return self.async_abort(reason="cannot_connect")

        return await self._create_entry(username, baseurl, password, acquired_token)

    async def async_step_user(self, user_input=None):
        """User initiated config flow."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_BASEURL, default="https://bke.euro.airstagelight.com/apiv1"): selector(CONF_BASEURL_SELECTOR),
                        vol.Required(CONF_USERNAME): TextSelector(
                            TextSelectorConfig(
                                prefix="E-Mail",
                                type=TextSelectorType.EMAIL, autocomplete="username")
                        ),
                        vol.Required(CONF_PASSWORD): TextSelector(
                            TextSelectorConfig(
                                prefix="Password",
                                type=TextSelectorType.PASSWORD, autocomplete="current-password"
                            )
                        ),
                    }
                ),
            )

        # User input is given
        username = user_input[CONF_USERNAME]
        return await self._create_client(username, password=user_input[CONF_PASSWORD], baseurl=user_input[CONF_BASEURL])