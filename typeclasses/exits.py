"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit
from typeclasses.mixins import ObjectBaseMixin, ExitAndObjectMixin, ExitObjectAndRoomMixin

# A tuple of standard exit names
STANDARD_EXITS = ('north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest')

class Exit(ExitObjectAndRoomMixin, ExitAndObjectMixin, ObjectBaseMixin, DefaultExit):
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
        INHERITS:
            typeclasses.mixins.ObjectBaseMixin
                Creates basic attributes that exist on all typeclasses.objects.Objects and typeclasses.characters.Character objects.
            typeclasses.mixins.ExitObjectAndRoomMixin
            typeclasses.mixins.ExitAndObjectMixin

        Attributes:
            inheirited from ExitAndObjectMixin
                targetable = False  # can this exit be targeted with an action
            inheirited from ExitObjectAndRoomMixin
                usdesc = self.key  # a property to easy get and set the short description on an object.
                    Use as if it were a stanard attribute.
                    usdesc = 'a happy tree'  # this will change the key of this object
                    caller.msg(f'You attack {target.usdesc}.')
            Inheirited from ObjectBaseMixin:
                self.hp is an Element, objects's hitpoints.
    """
    pass
