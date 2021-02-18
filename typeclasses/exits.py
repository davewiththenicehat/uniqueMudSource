"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit
from evennia.commands import command
from typeclasses.mixins import CharExAndObjMixin, AllObjectsMixin, ExObjAndRoomMixin

# A tuple of standard exit names
STANDARD_EXITS = ('north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest')


class UMExitCommand(command.Command):
    """
    This is a command that simply cause the caller to traverse
    the object it is attached to.

    UM:
        Overidden to stop movement if character is not ready, or is in a prone position.
    """

    obj = None

    def func(self):
        """
        Default exit traverse if no syscommand is defined.
        """
        caller = self.caller
        if not caller.ready():  # Character must be in ready status to move.
            return
        # a prone Character can not move.
        if caller.position == 'sitting' or caller.position == 'laying':
            caller.msg("You must stand up first.")
            return

        if self.obj.access(self.caller, "traverse"):
            # we may traverse the exit.
            self.obj.at_traverse(self.caller, self.obj.destination)
        else:
            # exit is locked
            if self.obj.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(self.obj.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.obj.at_failed_traverse(self.caller)

    def get_extra_info(self, caller, **kwargs):
        """
        Shows a bit of information on where the exit leads.

        Args:
            caller (Object): The object (usually a character) that entered an ambiguous command.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            A string with identifying information to disambiguate the command, conventionally with a preceding space.
        """
        if self.obj.destination:
            return " (exit to %s)" % self.obj.destination.get_display_name(caller)
        else:
            return " (%s)" % self.obj.get_display_name(caller)

class Exit(ExObjAndRoomMixin, AllObjectsMixin, CharExAndObjMixin, DefaultExit):
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
            typeclasses.mixins.CharExAndObjMixin
                Creates basic attributes that exist on all typeclasses.objects.Objects and typeclasses.characters.Character objects.
            typeclasses.mixins.ExObjAndRoomMixin
            typeclasses.mixins.AllObjectsMixin

        Attributes:
            inheirited from AllObjectsMixin
                targetable = False  # can this object be targeted with an action
                container = False  # Can the object contain other objects
            inheirited from ExObjAndRoomMixin
                usdesc = self.key  # a property to easy get and set the short description on an object.
                    Use as if it were a stanard attribute.
                    usdesc = 'a happy tree'  # this will change the key of this object
                    caller.msg(f'You attack {target.usdesc}.')
            Inheirited from CharExAndObjMixin:
                A large number of attributes are inheirited from CharExAndObjMixin.
                refer to CharExAndObjMixin doc string for full details.
                Nearly all variables that are used in combat are inheiried from CharExAndObjMixin.
                There are several methods inherited also.
    """

    exit_command = UMExitCommand

    pass
