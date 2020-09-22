"""
This file contains the GLOBAL_SCRIPTS dictionary
It will be imported into settings.py file
"""


def get_global_scripts():
    global_scripts = {
        "dune_weather_script": {
            "typeclass": "world.duneweather.DunWeather"
        },
        "dune_spawner_script": {
            "typeclass": "world.duneweather.DuneSpawner"
        }
    }
    return global_scripts
