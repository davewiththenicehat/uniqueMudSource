"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""

from collections import defaultdict

from evennia.contrib.rpsystem import ContribRPObject
from evennia.utils import inherits_from, list_to_string
from typeclasses.mixins import CharExAndObjMixin, AllObjectsMixin, ExObjAndRoomMixin

from utils.um_utils import error_report


class Object(ExObjAndRoomMixin, AllObjectsMixin, CharExAndObjMixin, ContribRPObject):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, account=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_before_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_traverse(traversing_object, source_loc) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_after_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

    Unique Mud:
        INHERITS:
            evennia.contrib.rpsystem.ContribRPObject
                Roleplaying base system for Evennia
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

    def at_after_move(self, source_location, **kwargs):
        """
        Called after move has completed, regardless of quiet mode or
        not.  Allows changes to the object due to the location it is
        now in.

        Args:
            source_location (Object): Where we came from. This may be `None`.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            UM overridden to automatically remove objects from Characters hands
            when they are no longer holding them.
        """
        # here to support possible future upgrades to parent classes.
        at_after_move_return = super().at_after_move(source_location, **kwargs)

        # if item was removed from a Character, remove it from hand if it was in one.
        if source_location:
            # only check hand state on Characters
            if inherits_from(source_location, "typeclasses.characters.Character"):
                hand_state = source_location.hands()
                for hand in hand_state:
                    if hand.occupied == self.dbref:  # if the moved item was in a Character's hand
                        hand.occupied = 0  # record that the item is no longer held
                    if hand.wielding == self.dbref:  # if the moved item was being wielded by a Character
                        hand.wielding = 0  # record that the item is not longer wielded

        # here to support possible future upgrades to parent classes.
        return at_after_move_return

    def at_before_move(self, destination, **kwargs):
        """
        Called just before starting to move this object to
        destination.

        Args:
            destination (Object): The object we are moving to
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            shouldmove (bool): If we should move or not.

        Notes:
            If this method returns False/None, the move is cancelled
            before it is even started.

        """
        # return has_perm(self, destination, "can_move")

        # adding support for possible future updates to evennia.
        move_allowed = super().at_before_move(destination, **kwargs)
        if not move_allowed:  # inherited object found reason to not move.
            return False
        # only allow movement if this object is moving into a container
        if destination.container:
            return True
        else:
            return False

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
        """
        string = ""
        if not looker:
            return ""

        # get description, build string
        desc = self.db.desc
        if desc:
            string += f"{desc.capitalize()}"
        else:
            string += f"{self.get_display_name(looker)} is devoid of description."
        if self.container and self.access(looker, "view"):  # this object is a container.
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
            string += "\nIt contains "
            if things or users:
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
                    string += f"{list_to_string(thing_strings)}"
                if users:
                    string += f"\n{' '.join(users)}"
                string += "."
            else:
                string += "nothing."
        return string
