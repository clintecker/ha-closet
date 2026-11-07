"""Constants shared by the thin Closet adapter."""

DOMAIN = "closet"
CONF_BACKEND_URL = "backend_url"
CONF_TOKEN = "token"
CONF_ADDON_SLUG = "addon_slug"
# Sync wraps the up-to-1-MiB catalog in an envelope, matching Rust's route cap.
MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 30

DEFAULT_BACKEND_URL = ""
