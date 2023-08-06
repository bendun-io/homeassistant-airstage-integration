"""Easee Charger constants."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    Platform,
    UnitOfTemperature,
)
from homeassistant.helpers.entity import EntityCategory

DOMAIN = "airstage"
TIMEOUT = 30
VERSION = "0.9.54"
MIN_HA_VERSION = "2023.4.0"
CONF_MONITORED_SITES = "monitored_sites"
MANUFACTURER = "Fujitsu"
MODEL_CHARGING_ROBOT = "Charging Robot"
PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]
LISTENER_FN_CLOSE = "update_listener_close_fn"

weeklyScheduleStartDays = {
    0: "MondayStartTime",
    1: "TuesdayStartTime",
    2: "WednesdayStartTime",
    3: "ThursdayStartTime",
    4: "FridayStartTime",
    5: "SaturdayStartTime",
    6: "SundayStartTime",
}

weeklyScheduleStopDays = {
    0: "MondayStopTime",
    1: "TuesdayStopTime",
    2: "WednesdayStopTime",
    3: "ThursdayStopTime",
    4: "FridayStopTime",
    5: "SaturdayStopTime",
    6: "SundayStopTime",
}

MANDATORY_EASEE_ENTITIES = {
    "status": {
        "key": "state.chargerOpMode",
        "attrs": [
            "config.phaseMode",
            "state.outputPhase",
            "state.ledMode",
            "state.cableRating",
            "config.authorizationRequired",
            "config.localNodeType",
            "config.localAuthorizationRequired",
            "config.ledStripBrightness",
            "site.id",
            "site.name",
            "site.siteKey",
            "site.ratedCurrent",
            "circuit.id",
            "circuit.ratedCurrent",
        ],
        "units": None,
        "convert_units_func": "map_charger_status",
        "device_class": None,
        # "device_class": "easee__status",
        "icon": "mdi:ev-station",
        "translation_key": "easee_status",
    },
}
