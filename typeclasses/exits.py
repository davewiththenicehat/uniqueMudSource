"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit


class Exit(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    UniqueMud:
        Attributes:
            usdesc = self.key  # a property to easy get and set the short description on an object.
                Use as if it were a stanard attribute.
                usdesc = 'a happy tree'  # this will change the key of this object
                caller.msg(f'You attack {target.udesc}.')
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
