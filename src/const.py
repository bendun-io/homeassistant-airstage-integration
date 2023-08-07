"""Constants for the Airstage Climate integration."""

DOMAIN = "airstage"
TIMEOUT = 30
VERSION = "0.9.54"
MIN_HA_VERSION = "2023.4.0"
CONF_MONITORED_SITES = "monitored_sites"
MANUFACTURER = "Fujitsu"

# CONF_POSITION = "position"
CONF_BASEURL = "baseUrl"
CONF_BASEURL_SELECTOR = {
    "select": {
        "options": [
            {
                "label": "Australia",
                "value": "https://bke.au.airstagelight.com/apiv1"
            },
            {
                "label": "Europe",
                "value": "https://bke.euro.airstagelight.com/apiv1"
            },
            {
                "label": "Japan",
                "value": "https://bke.jp.airstagelight.com/apiv1"
            },
            {
                "label": "US",
                "value": "https://bke.us.airstagelight.com/apiv1"
            },
        ],
        "mode": "dropdown"
    }
}

# ATTR_STATUS = "status"
# ATTR_VANE_HORIZONTAL = "vane_horizontal"
# ATTR_VANE_HORIZONTAL_POSITIONS = "vane_horizontal_positions"
# ATTR_VANE_VERTICAL = "vane_vertical"
# ATTR_VANE_VERTICAL_POSITIONS = "vane_vertical_positions"

# SERVICE_SET_VANE_HORIZONTAL = "set_vane_horizontal"
# SERVICE_SET_VANE_VERTICAL = "set_vane_vertical"

# PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]
# LISTENER_FN_CLOSE = "update_listener_close_fn"
