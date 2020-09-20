from typeclasses.scripts import Script
import random
from evennia.utils.search import search_tag


class DunWeather(Script):
    """
    Displays a weather message in Dune rooms
    Add dune tag with:
    py self.location.tags.add("dune_room", category="location tags")
    """

    def at_script_creation(self):
        self.key = "dune_weather_script"
        self.desc = "Gives random weather messages in dune rooms."
        self.interval = 60  # every minute
        self.persistent = True  # will survive reload

    def at_repeat(self):
        "called every self.interval seconds."
        rand = random.random()
        if rand < 0.5:
            weather = "A gentle breeze blow sand among your feet."
        elif rand < 0.7:
            weather = "A great gust of wind pelts you with sand."
        else:
            weather = "You hear a fait hiss of sand gently blowing across the dunes."
        # send this message to everyone inside the object this
        # script is attached to (likely a room)
        dune_rooms = search_tag(key="dune_room", category="location tags")
        for dune_room in dune_rooms:
            dune_room.msg_contents(weather)
