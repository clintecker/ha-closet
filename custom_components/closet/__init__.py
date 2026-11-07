"""A thin Home Assistant adapter for the JSON-backed Closet service."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from .client import ClosetClient
from .const import CONF_BACKEND_URL, CONF_TOKEN, DOMAIN
from .coordinator import ClosetCoordinator
from .http import ClosetView

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = [Platform.SENSOR]
type ClosetConfigEntry = ConfigEntry[ClosetCoordinator]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register one authenticated bridge, independent of entry reloads."""
    hass.http.register_view(ClosetView(hass))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ClosetConfigEntry) -> bool:
    """Validate the connection before publishing any entity."""
    client = ClosetClient(
        async_get_clientsession(hass),
        entry.data[CONF_BACKEND_URL],
        entry.data[CONF_TOKEN],
    )
    integration = await async_get_integration(hass, "closet")
    coordinator = ClosetCoordinator(hass, entry, client, str(integration.version))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ClosetConfigEntry) -> bool:
    """Unload entities and their polling; the shared HTTP session belongs to HA."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
