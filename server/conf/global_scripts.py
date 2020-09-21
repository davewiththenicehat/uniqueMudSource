"""
This file contains the GLOBAL_SCRIPTS dictionary
It will be imported into settings.py file
"""


def get_global_scripts():
    global_scripts = {
        "dune_weather_script": {
            "typeclass": "world.duneweather.DunWeather"
        }
    }
    return global_scripts
