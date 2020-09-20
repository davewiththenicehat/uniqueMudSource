"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom, TICKER_HANDLER
import random
from evennia import utils
from world.map import Map


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

    # Add this hook in any empty area within your Room class.
    def at_object_receive(self, obj, source_location):
        if utils.inherits_from(obj, 'typeclasses.npcs.NPC'):
            return
        elif utils.inherits_from(obj, 'typeclasses.characters.Character'):
            # A PC has entered.
            # Cause the player's character to look around.
            obj.execute_cmd('look')
            for item in self.contents:
                if utils.inherits_from(item, 'typeclasses.npcs.NPC'):
                    # An NPC is in the room
                    item.at_char_entered(obj)

    #updated following https://github.com/evennia/evennia/wiki/Dynamic-In-Game-Map
    def return_appearance(self, looker):
        string = "%s\n" % Map(looker).show_map()
        looker.msg((string, {"type": "map-pane"}))
        # Add all the normal stuff like room description,
        # contents, exits etc.
        string += "\n" + super().return_appearance(looker)
        return string
