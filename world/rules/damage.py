"""
contains functions and variables that interact with game damage.

Equation:
    Command.max_dmg is used to determine the max damage that command can randomly roll.
    item.max_dmg replaced Command.max_dmg if the command requires a wielded weapon.
        item.max_dmg defaults to 4
    damage.roll will roll a random number between 1 and command.max_dmg
        adding the Characters.TYPE_dmg_mod where TYPE is Command.dmg_mod_stat
            Default is 'STR'
            dmg_mod is option but is added by default.
            dmg_mod can be a negative number
    Command.dmg_types and item.dmg_types are merged, and their values are added together.
        The value of each damage type is added as a flat bonus to the damage.
    The Character receiving the damage has a corrisponding damage types in Character.dr.TYPE.
    damage.dmg_after_dr finds the Command.dmg_type that does the most damage and returns that number
        It has an option to instead return the least damaging attack.

Attributes:
    MAP_DICT = dict, a mapping of damage types and full names
        aliase: MAP
        in format: 'ACD': 'acid'
    TYPES = tuple, damage types to iterate through

Modules:
    roll, Get a damage roll adjusted by a character's damage stat modifier.
    get_dmg_after_dr, Get a command's damage dealt after the command's target's damage reduction
    restoration_roll, Get a number to restore health on an object

Notes
    A list of damage types:
        'ACD': 'acid',
        'BLG': 'bludgeoning',
        'CLD': 'cold',
        'FIR': 'fire',
        'ELC': 'electric',
        'MNT': 'mental',
        'PRC': 'piercing',
        'POI': 'poison',
        'RAD': 'radiation',
        'SLS': 'slashing'
"""

from random import randint
from evennia.utils.logger import log_info, log_warn
from utils.um_utils import error_report
from world.rules.stats import STATS, STAT_MAP_DICT

# a mapping of damage types and full names
MAP_DICT = {
    'ACD': 'acid',
    'BLG': 'bludgeoning',
    'CLD': 'cold',
    'FIR': 'fire',
    'ELC': 'electric',
    'MNT': 'mental',
    'PRC': 'piercing',
    'POI': 'poison',
    'RAD': 'radiation',
    'SLS': 'slashing'
}
MAP = MAP_DICT

# damage types to iterate through
TYPES = (
    'ACD',
    'BLG',
    'CLD',
    'FIR',
    'ELC',
    'MNT',
    'PRC',
    'POI',
    'RAD',
    'SLS'
)

# number of seconds Characters automatically heal
HEALING_INTERVAL = 120


def roll(command, use_mod=True, log=False):
    """
    Get a damage roll adjusted by a character's damage stat modifier.

    Arguments:
        command, the command that is manipulating damage
        use_mod=True,
        log=False, if True log the variables used

    Returns:
        random int between 1 and damage max plus character's stat damage modifier

    Equation:
        Each action can have it's own max damage.
            Default max damage is 4.
        Each action can have it's own stat used to modify damage
            Default stat used to modify damage is strength
        Damage manipulated is from 1 to max damage plus the stat's damage modifier.
    """
    dmg_max = 4
    dmg_mod_stat = 'STR'
    dmg_mod = 0
    caller = command.caller
    if hasattr(command, 'dmg_max'):  # if the command has a damage maximum use it instead
        dmg_max = getattr(command, 'dmg_max')
    # only get stat modifier if use_mod is True
    if use_mod:
        if hasattr(command, 'dmg_mod_stat'):  # if the command has a custom damage modifier stat use it instead
            dmg_mod_stat = getattr(command, 'dmg_mod_stat', False)
            # convert long stat names to short stat names.
            if dmg_mod_stat not in STATS:
                for sh_nm, ln_nm in STAT_MAP_DICT.items():
                    if dmg_mod_stat == ln_nm:
                        dmg_mod_stat = sh_nm
            dmg_mod_name = dmg_mod_stat+'_dmg_mod'
        if hasattr(caller, dmg_mod_name):  # if the caller of the command has the stat damage modifier use it.
            dmg_mod = getattr(caller, dmg_mod_name)
    return randint(1, dmg_max) + dmg_mod


def get_dmg_after_dr(command, dmg_dealt=None, max_defense=False, body_part=None, target=None, log=False):
    """
    Get damage dealt after damage reduction.
    Minimum return value is 0.

    Arguments
        command, the command that is manipulating damage
        dmg_dealt=None, the damage the command dealt
            If None is provided get_dmg_after_dr will use self.dmg_dealt
            if self.dmg_dealt does not exist a random roll will be processed.
                using standard rules: dmg_dealt = damage.roll(self)
                where self.dmg_max is the max damage possible and self.dmg_mod_stat modifies the damage
        max_defense=False, if true the attack's least damaging dmg_type is used.
        body_part=None, the body part the command is manipulating.
            Leave blank if you want to ignore dr for armor.
            Can be an instance of the body part, or the parts string name.
        target=None, instance of the target that would receive the damage.
        log=False, should this function log messages

    Notes:
        If the command has requires_wielding is set.
            The required item's dmg_types are added to the command's
            A key is only updated if it has a value other than 0.
            When a key is updated. If their was an existing key in the command.
                The command's and the item's dmg_type values are added together, before the
                command's dmg_types key is updated.

    Unit Tests:
        in commands.test.TestCommands.test_dmg

    Returns:
        damage dealt after dr for the body part hit after the targets damage reduction.
        Default the highest possible damage is returned.
        pass max_defense=True, to return the lowest possible damage.
        The minimum value this function returns is 0.

    Equation:
        Each action has a list of damage types it can manipulate.
        By default the damage type that does the most damage is chosen.
        Some actions instead choose the least possible damage.

        An actions's damage is increase by
            A wielded item that is required for the action.
            The item's list of damage types is added to the actions.
        An action's damage is reduced by
            targets dr value
            If the action hit a body part.
            That body part's dr value is also used to reduce damage.
                Normally this would be the armor's dr value for that body part.
    """
    if not target:
        target = command.target
    if dmg_dealt is None:
        if hasattr(command, 'dmg_dealt'):
            dmg_dealt = command.dmg_dealt
        if dmg_dealt is None:
            dmg_dealt = roll(command)  # get a random damage roll, none was provided
    # decalare default variable values
    dmg_type_mods = {}
    dmg_types = {}
    result = 0
    dmg_red_type = 'no type'
    # If the body_part is a string, get an instance of the part
    if body_part:
        if isinstance(body_part, str):
            if target.body.parts:
                if body_part in target.body.parts:
                    body_part = target.get_body_part(body_part)
            # failed to find an instance throw a soft error
            if isinstance(body_part, str):
                err_msg = f"command: {command.key} | caller: {command.caller.id} | " \
                          f"Failed to find body part instance for {body_part}."
                error_report(err_msg, command.caller)
                body_part = None  # keep the function from erroring futher
        # if body_part is an instance, make certain it is not from an incorrect target
        elif type(body_part) == "<class 'utils.element.ListElement'>":
            test_part = target.get_body_part(body_part.name)
            if test_part is not body_part:
                err_msg = f"command: {command.key} | caller: {command.caller.id} | " \
                          f"{body_part}."
                error_report(err_msg, command.caller)
                body_part = None  # keep the function from erroring futher
        elif body_part == True:
            pass
    # Get defense values vs action's dmg_types if any
    if command.dmg_types:
        # Collect, into dictionary dmg_type_mods
        #   target.dr.dmg_type value
        #   + armor.dr.dmg_type value (on part hit if any)
        #   - command.dmg_type value

        # add a wielded item's damage modifier's to the command's
        if command.requires_wielding:  # if the command requires a wielded item
            item_dmg_types = command.caller_weapon.get_dmg_mods()  # dictionay of item dmg_types
            # add the wielded item's damage modifiers to the command's
            for item_dmg_type, item_dmg_mod in item_dmg_types.items():
                if item_dmg_mod:  # do not add 0 values to the Command.dmg_types dictionary
                    cmd_dmg_mod = command.dmg_types.get(item_dmg_type)
                    if cmd_dmg_mod:
                        cmd_dmg_mod += item_dmg_mod
                    else:  # if the key did not exist or value was 0
                        cmd_dmg_mod = item_dmg_mod
                    command.dmg_types.update({item_dmg_type: cmd_dmg_mod})
        # collect the command's damage types and modifiers into a dictionary
        for dmg_type, cmd_dmg_mod in command.dmg_types.items():
            body_part_dr_value = 0
            if body_part:  # if the object had that body part
                body_part_dr_value = getattr(body_part.dr, dmg_type, 0)
            # find the targets dr values that match the commands damage types
            target_dr_value = 0
            if hasattr(target.dr, dmg_type):
                target_dr_value = getattr(target.dr, dmg_type, 0)
            # calculate than record the damage type modifider value
            dmg_type_mod_value = target_dr_value + body_part_dr_value - cmd_dmg_mod
            if not dmg_type_mod_value == 0:  # only record if it would have an effect
                dmg_type_mods.update({dmg_type: dmg_type_mod_value})
        # get the lowest or highest damage after damage reduction
        if len(dmg_type_mods) > 0:  # Only check if defenses would make a difference
            if max_defense:  # get targets highest defense type against this action's dmg_types
                dmg_red_type = max(dmg_type_mods, key=dmg_type_mods.get)
            else:  # get the targets lowest defense type against this action's dmg_types
                dmg_red_type = min(dmg_type_mods, key=dmg_type_mods.get)
    # calculate damage after damage reduction
    damage_reduction = dmg_type_mods.get(dmg_red_type, 0)
    result = dmg_dealt - damage_reduction
    if result < 0:  # do not allow damage to be less than 0
        result = 0
    if log:
        log_msg = f"command {command.key}, Character id: {command.caller.id} | " \
                  f"result: {result} | dmg_dealt {dmg_dealt} | body_part {body_part} | " \
                  f"dmg_red_type: {dmg_red_type} | damage_reduction: {damage_reduction}"
        log_info(log_msg)
        # command.caller.msg(log_msg)  # uncomment to see log to screen.
    return result


def restoration_roll(restoration_modifier=0):
    """
    Get a number to restore health on an object

    Argument:
        restoration_modifie=0, gets added to the max number that can be rolled

    Equation:
        Returns a random number between:
            4 + restoration_modifier
            The number can not be less than 1
    """
    restoration_max = 4 + restoration_modifier
    if restoration_max < 1:  # restoration max can not be less than 1
        restoration_max = 1
    return randint(1, restoration_max)
