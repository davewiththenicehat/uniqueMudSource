"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from evennia.contrib.rpsystem import ContribRPRoom
from typeclasses.mixins import ExitObjectAndRoomMixin


class Room(ExitObjectAndRoomMixin, ContribRPRoom):
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
            typeclasses.mixins.ExitObjectAndRoomMixin

        Attributes:
            inheirited from ExitObjectAndRoomMixin
                usdesc = self.key  # a property to easy get and set the short description on an object.
                    Use as if it were a stanard attribute.
                    usdesc = 'a happy tree'  # this will change the key of this object
                    caller.msg(f'You attack {target.usdesc}.')
    """

    pass
