"""Poll the service's aggregate state without storing a second inventory."""

import logging
from datetime import timedelta

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import ClosetClient, ResponseTooLarge
from .const import DOMAIN
from .models import ClosetSummary

_LOGGER = logging.getLogger(__name__)


class ClosetCoordinator(DataUpdateCoordinator[ClosetSummary]):
    """One shared session and one entry-owned polling lifecycle."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: ClosetClient,
        integration_version: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=60),
        )
        self.client = client
        self.integration_version = integration_version

    async def _async_update_data(self) -> ClosetSummary:
        try:
            response = await self.client.request("GET", "/v1/system")
            if response.status in {401, 403}:
                raise ConfigEntryAuthFailed("The Closet credential was rejected")
            if response.status != 200:
                raise UpdateFailed("Closet is unavailable")
            summary = ClosetSummary.parse(response.json())
            if summary.role != "integration":
                raise ConfigEntryAuthFailed("Use Closet's integration credential")
        except (ClientError, TimeoutError, ResponseTooLarge, ValueError) as err:
            raise UpdateFailed("Cannot read Closet") from err
        if summary.version != self.integration_version:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                "version_mismatch",
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key="version_mismatch",
                translation_placeholders={
                    "app_version": summary.version,
                    "integration_version": self.integration_version,
                },
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, "version_mismatch")
        return summary
