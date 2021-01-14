from evennia import CmdSet
from commands.command import Command
from evennia import utils
from world.rules import damage
from typeclasses.objects import Object
from utils.um_utils import error_report
from utils.element import ListElement



# used to refer to the clothing class, to make this easier to create instances of
WIELDABLE_OBJECT_CLASS = "typeclasses.equipment.wieldable.Wieldable"


class Wieldable(Object):
    """
    Used to represent an object that can be equipped or wielded
    """

    @property
    def item_type(self):
        """
        Stores the type of item this object is.

        Forwards to the database with, self.db.item_type.
        """
        return self.db.item_type
    @item_type.setter
    def item_type(self, value):
        self.db.item_type = value
    @item_type.deleter
    def item_type(self):
        delattr(self.db, 'item_type')

    def at_object_creation(self):
        """Runs when Object is created."""
        self.at_init()  # initialize self.
        self.item_type = 'unset'  # initialize item type
        self.targetable = True  # wieldable items can be targeted with commands
        return super().at_object_creation()


class Weapon(Wieldable):
    """
    Object that can be used to add to attack action's damage.

    dmg_types = ListElement  # ListElement of damage types this weapon can manipulate.
        If a weapon has no dmg_types, attack actions will only use their base dmg_types attribute.
        value is a flat bonus this weapon will add to attack actions of that dmg_type.
    """

    @property
    def dmg_types(self):
        """
        Track types and strength of damage this weapon does.

        ListElement will track it in the database as dmg_types_TYPE
            dmg_types_blg for example
        """
        try:
            if self._dmg_types:
                pass
        except AttributeError:
            self._dmg_types = ListElement(self, damage.TYPES)
            self._dmg_types.verify()
        return self._dmg_types
    @dmg_types.setter
    def dmg_types(self, value):
        self._dmg_types.set(value)
    @dmg_types.deleter
    def dmg_types(self):
        self._dmg_types.delete()

    @property
    def dmg_max(self):
        """
        Stores the max damage this weapon can roll
        This property auto initializes to 4.

        Forwards to the database with, self.db.dmg_max.
        """
        value = getattr(self.db, 'dmg_max', False)
        if value:
            return value
        else:
            self.db.dmg_max = 4
            return 4
    @dmg_max.setter
    def dmg_max(self, value):
        self.db.dmg_max = value
    @dmg_max.deleter
    def dmg_max(self):
        delattr(self.db, 'dmg_max')

    def get_dmg_mods(self):
        """
        Returns a dictionary that represents the Weapon's damage modifiers.
        """
        dmg_mods = {}
        dmg_types = self.dmg_types.el_list
        for dmg_type in dmg_types:
            modifier = getattr(self.dmg_types, dmg_type, 0)
            if modifier:
                dmg_mods.update({dmg_type: modifier})
        return dmg_mods


class OneHandedWeapon(Weapon):
    """
    Objects used for the one_handed skill and command sets.

    Inherits typeclasses.equipment.wieldable.Weapon
    """
    def at_object_creation(self):
        """Runs when Object is created."""
        at_object_creation_return = super().at_object_creation()
        self.item_type = 'one_handed'  # initialize item type
        return at_object_creation_return


class WieldableCmdSet(CmdSet):
    """Command set for wielding items."""

    def at_cmdset_creation(self):
        """Create wieldable command set."""
        self.add(CmdWield)
        self.add(CmdUnwield)


class CmdWield(Command):
    """
    Equip a weapon or item in hand.
    """
    key = "wield"
    aliases = ["equip",]
    can_not_target_self = True  # if True this command will end with a message if the Character targets themself
    target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
    search_caller_only = False  # if True the command will only search the caller for targets
    # a tuple, position 0 string of a class type, position 1 is a string to show on mismatch
    target_inherits_from = (WIELDABLE_OBJECT_CLASS, 'weapon')
    target_in_hand = True  # if True the target of the command must be in the Characters hand to complete successfully

    def func(self):
        """
        equip the item
        """
        caller = self.caller
        target = self.target
        holding_hand = False
        # if the Character is already wielding an object of the same type stop the command
        # also get a reference of the hand holding the object to wield
        hands_state = caller.hands()
        if not hands_state:
            err_msg = f"Command wield, caller: {caller.id} | " \
                       f"failed to find hands."
            error_report(err_msg, caller)
        for hand in hands_state:
            if hand.wielding:  # if hand is wielding something
                wield_obj_inst = caller.search(hand.wielding, quiet=True)
                if wield_obj_inst:
                    wield_obj_inst = wield_obj_inst[0]
                    if type(target) == type(wield_obj_inst):
                        stop_msg = f"You are already wielding {wield_obj_inst.usdesc}. " \
                                    "You can not wield two objects of the same type."
                        caller.msg(stop_msg)
                        return
            if hand.occupied:
                if hand.occupied == target.dbref:
                    holding_hand = hand
                    holding_hand.wielding = target.dbref
                    caller.msg(f"You wield {target.usdesc} in your {holding_hand.name}.")
                    room_message = f"{caller.usdesc} wields {target.usdesc}."
                    caller.location.msg_contents(room_message, exclude=caller)
                    break



class CmdUnwield(Command):
    """
    Unwield an item in hand
    """
    key = "unwield"
    aliases = ["unequip",]
    can_not_target_self = True  # if True this command will end with a message if the Character targets themself
    target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
    search_caller_only = False  # if True the command will only search the caller for targets
    # a tuple, position 0 string of a class type, position 1 is a string to show on mismatch
    target_inherits_from = (WIELDABLE_OBJECT_CLASS, 'weapon')
    target_in_hand = True  # if True the target of the command must be in the Characters hand to complete successfully

    def func(self):
        """
        unequip the item
        """
        caller = self.caller
        target = self.target

        wielding_hand = caller.is_wielding(target)
        if wielding_hand:
            wielding_hand.wielding = 0
            caller.msg(f"You stop wielding {target.usdesc}.")
            room_message = f"{caller.usdesc} stops wielding {target.usdesc}."
            caller.location.msg_contents(room_message, exclude=caller)
        else:
            caller.msg(f"You are not wielding {target.usdesc}.")
