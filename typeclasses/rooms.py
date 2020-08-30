"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom, TICKER_HANDLER
import random


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def make_hangout(self):
        self.tags.add("hangout", category="location tags")

    def make_weather(self):
        TICKER_HANDLER.add(60, self.at_weather_update)

    def at_weather_update(self, *args, **kwargs):
        "ticked at regular intervals"
        ECHOES = [
            "The sky is clear.",
            "Clouds gather overhead.",
            "It's starting to drizzle.",
            "A breeze of wind is felt.",
            "The wind is picking up"
            ]
        echo = random.choice(ECHOES)
        self.msg_contents(echo)
