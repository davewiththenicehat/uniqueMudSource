"""
Room

Rooms are simple containers that has no location of their own.

"""

from collections import defaultdict

from evennia.contrib.rpsystem import ContribRPRoom
from evennia.contrib.extended_room import ExtendedRoom
from typeclasses.mixins import ExObjAndRoomMixin, AllObjectsMixin
from evennia.utils.utils import list_to_string, inherits_from


class Room(AllObjectsMixin, ExObjAndRoomMixin, ContribRPRoom, ExtendedRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.

    UniqueMud:

        Inherits:
            evennia.contrib.rpsystem.ContribRPRoom
                Roleplaying base system for Evennia
            evennia.contrib.extended_room.ExtendedRoom
                For seasons and details.
                Use commands.Command.detail_search, to search for a Room detail.
            typeclasses.mixins.ExObjAndRoomMixin
            typeclasses.mixins.AllObjectsMixin

        Attributes:
            inheirited from ExObjAndRoomMixin
                usdesc = self.key  # a property to easy get and set the short description on an object.
                    usdesc is intended for rare instance where the emote system can not apply a name to a second target.
                    Use the emote system or obj.get_display_name(receiver) first.
            inheirited from AllObjectsMixin
                targetable = False  # can this object be targeted with an action
                container = True  # Can the object contain other objects

    """

    def at_object_creation(self):
        """Runs when Character is created."""
        self.container = True  # Can the object contain other objects
        super().at_object_creation()

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""

        # update for seasons and time, IE: ExtendedRoom
        # ensures that our description is current based on time/season
        self.update_current_description()

        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker, pose=True)
            if con.destination:
                exits.append(key)
            elif inherits_from(con, "typeclasses.characters.Character"):
                users.append(key)
            else:
                # things can be pluralized
                things[key].append(con)

        # get description, build string
        string = ""
        desc = self.db.desc
        if desc:
            string += f"{desc.capitalize()}"
        else:
            string += "You are in a space devoid of description."
        if things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                else:
                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][0]
                thing_strings.append(key.strip())
            # floor description.
            if len(things) > 1:
                fl_plu = "are"
            else:
                fl_plu = "is"
            things_str = list_to_string(thing_strings)
            string += f"\nOn the ground {fl_plu} {things_str}."
        if users:
            string += f"\n{' '.join(users)}"
        if exits:
            exit_str = list_to_string(exits, endsep="or")
            string += "\n|wYou may leave by|n " + exit_str + "."
        return string
