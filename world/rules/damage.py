"""
contains functions and variables that interact with game damage.

Attributes:
    MAP_DICT = dict, a mapping of damage types and full names
        aliase: MAP
        in format: 'ACD': 'acid'
    TYPES = tuple, damage types to iterate through

Modules:
    roll, Get a damage roll adjusted by a character's damage stat modifier.

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
            dmg_mod_stat = getattr(command, 'dmg_mod_stat')
        dmg_mod_name = dmg_mod_stat+'_dmg_mod'
        if hasattr(caller, dmg_mod_name):  # if the caller of the command has the stat damage modifier use it.
            dmg_mod = getattr(caller, dmg_mod_name)
    return randint(1, dmg_max) + dmg_mod


def get_dmg_after_dr(command, dmg_dealt=None, body_part_name=None, max_defense=False, log=False):
    """
    Get damage dealt after damage reduction.
    Minimum return value is 0.

    Arguments
        command, the command that is manipulating damage
        dmg_dealt=None, the damage the command dealth
            If None is provided get_dmg_after_dr will use self.dmg_dealt
            if self.dmg_dealt does not exist a random roll will be processed.
                using standard rules: dmg_dealt = damage.roll(self)
                where self.dmg_max is the max damage possible and self.dmg_mod_stat modifies the damage
        body_part_name=None, the body part the command is manipulating.
            Leave blank if you want to ignore dr for armor
        max_defense=False, if true the attack's least damaging dmg_type is used.
        log=False, should this function log messages

    Notes:
        unit tests for this are in commands.tests

    Returns:
        damage dealt after dr for the body part hit and the target
        The minimum value this function returns is 0.

    equation:
        Each action has a list of damage types they can manipulate.
        By default the damage type that does the most damage is chosen.
        If argument max_defense is True, the type that does the least damage is chosen.

        Action's damage is reduced by
            targets dr value
            If the action hit a body part.
            That body part's dr value is also used to reduce damage.
                Normally this would be the armor's dr value for that body part.
    """
    target = command.target
    if dmg_dealt is None:
        if hasattr(command, 'dmg_dealt'):
            dmg_dealt = command.dmg_dealt
        if dmg_dealt is None:
            dmg_dealt = roll(command)  # get a random damage roll, none was provided
    # decalare default variable values
    body_part_inst = None
    dmg_type_mods = {}
    result = 0
    dmg_red_type = 'no type'
    # get an instance of the body part hit.
    if body_part_name:
        if target.body.parts:
            if body_part_name in target.body.parts:
                body_part_inst = getattr(target.body, body_part_name)
                if not body_part_inst:
                    log_warn(f"command {command.key}, Character id: {command.caller.id} | " \
                             "failed to get body_part_inst after finding it in target.body.parts")
    # Get defense values vs action's dmg_types if any
    if command.dmg_types:
        # Collect, into dictionary dmg_type_mods
        #   target.dr.dmg_type value
        #   + armor.dr.dmg_type value (on part hit if any)
        #   - command.dmg_type value
        for dmg_type, cmd_dmg_mod in command.dmg_types.items():
            body_part_dr_value = 0
            if body_part_inst:  # if the object had that body part
                body_part_dr_value = getattr(body_part_inst.dr, dmg_type, 0)
            elif body_part_name:
                err_msg = f"command: {command.key} | caller: {command.caller.id} | " \
                          f"Failed to find body part instance {body_part_name}."
                error_report(err_msg, command.caller)
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
                  f"result: {result} | dmg_dealt {dmg_dealt} | body_part_name {body_part_name} | " \
                  f"dmg_red_type: {dmg_red_type} | damage_reduction: {damage_reduction}"
        log_info(log_msg)
        # command.caller.msg(log_msg)  # uncomment to see log to screen.
    return result


def restoration_roll(restoration_modifier=0):
    """
    Get a number to restore health on an object

    Argument:
        restoration_modifie=0, gets added to the max number that can be returned

    Equation:
        Returns a random number between:
            4 + restoration_modifier
            The number can not e less than 1
    """
    restoration_max = 4 + restoration_modifier
    if restoration_max < 1:  # restoration max can not be less than 1
        restoration_max = 1
    return randint(1, restoration_max)
