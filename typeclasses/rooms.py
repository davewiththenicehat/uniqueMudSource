"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from evennia.contrib.rpsystem import ContribRPRoom


class Room(ContribRPRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.

    UniqueMud:

        INHERITS:
            evennia.contrib.rpsystem.ContribRPRoom
                Roleplaying base system for Evennia

        Attributes:
            usdesc = self.key  # a property to easy get and set the short description on an object.
                Use as if it were a stanard attribute.
                usdesc = 'a happy tree'  # this will change the key of this object
                caller.msg(f'You attack {target.usdesc}.')
    """

    @property
    def usdesc(self):
        """
        Universal method to get and set an object's description.
        Universal Short Description

        A usdesc exists on each evennia object type Object, Character, Room and Exit

        usdesc refers to self.key on Exits, Objects and rooms
        usdesc refers to self.sdesc on Characters

        Usage:
        caller.msg(f'You attack {target.usdesc}.)  # to get
        target.usdesc = 'a happy tree'  # to set
        """
        return self.key

    @usdesc.setter
    def usdesc(self, value):
        """Setter property for usdesc"""
        self.key = value
