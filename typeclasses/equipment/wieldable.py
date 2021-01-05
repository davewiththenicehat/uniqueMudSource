from evennia import CmdSet
from world.rules import damage
from typeclasses.objects import Object
from commands.command import Command
from utils.um_utils import error_report
from evennia import utils



# used to refer to the clothing class, to make this easier to create instances of
WIELDABLE_OBJECT_CLASS = "typeclasses.equipment.wieldable.Wieldable"


class Wieldable(Object):
    """
    Used to represent an object that can be equipped or wielded
    """
    def at_object_creation(self):
        """Runs when Object is created."""
        self.at_init()  # initialize self.
        self.targetable = True  # wieldable items can be targeted with commands
        return super().at_object_creation()


class Weapon(Wieldable):
    """
    dmg_types = None  # tuple or list of damage types this weapon deals
        list of types is in world.rules.damage.TYPES
        dmg_types = ('BLG') is not a tuple it is a string. dmg_types = ('BLG',), will return a tuple
    """
    dmg_types = None  # tuple or list of damage types this weapon can deal


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
