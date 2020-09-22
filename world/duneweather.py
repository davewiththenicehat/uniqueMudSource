from typeclasses.scripts import Script
import random
from evennia.utils.search import search_tag
from random import randint
from evennia.prototypes.spawner import spawn
from world.prototypes import *

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


class DuneSpawner(Script):
    """
    Spawns monsters in Dune rooms
    """

    def at_script_creation(self):
        self.key = "dune_spawner_script"
        self.desc = "Spawns monsters in dune rooms"
        self.interval = 60  # every minute
        self.persistent = True  # will survive reload

    def at_repeat(self):
        "called every self.interval seconds."

        # decide the monster prototype
        rand = random.random()
        if rand <= 0.7:
            monster = WEAK_DUNE_RAT
        else:
            monster = STRONG_DUNE_RAT

        dune_rooms = search_tag(key="dune_room", category="location tags")
        for dune_room in dune_rooms:
            room_contents = dune_room.contents
            room_has_monster = False

            # does this room already have a monster in it?
            for room_object in room_contents:
                if room_object.db.is_monster:
                    room_has_monster = True

            # if there is no monster in this room spawn one.
            if not room_has_monster:
                monster['location'] = dune_room.dbref  # set spawn location to this room
                spawn(monster)
