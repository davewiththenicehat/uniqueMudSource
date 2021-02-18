"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from evennia.contrib.rpsystem import ContribRPRoom
from typeclasses.mixins import ExObjAndRoomMixin, AllObjectsMixin


class Room(AllObjectsMixin, ExObjAndRoomMixin, ContribRPRoom):
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
            typeclasses.mixins.ExObjAndRoomMixin
            typeclasses.mixins.AllObjectsMixin

        Attributes:
            inheirited from ExObjAndRoomMixin
                usdesc = self.key  # a property to easy get and set the short description on an object.
                    Use as if it were a stanard attribute.
                    usdesc = 'a happy tree'  # this will change the key of this object
                    caller.msg(f'You attack {target.usdesc}.')
            inheirited from AllObjectsMixin
                targetable = False  # can this object be targeted with an action
                container = True  # Can the object contain other objects
    """

    def at_object_creation(self):
        """Runs when Character is created."""
        self.container = True
        super().at_object_creation()
