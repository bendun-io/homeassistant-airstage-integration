"""Constants for the Airstage Climate integration."""

DOMAIN = "airstage"
TIMEOUT = 30
VERSION = "0.9.54"
MIN_HA_VERSION = "2023.4.0"
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

DUMMY_DEVICE_TOKEN = "xxxxxxxxxxxxxxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_xxxxxxxxxxxxxxxxxxxxxxxx"

from datetime import timedelta
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)