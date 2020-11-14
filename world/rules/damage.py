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
from utils.element import ListElement
from evennia.utils.logger import log_info

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


def get_dmg_after_dr(command, dmg_dealt=None, body_part_name=None, log=False):
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
        log=False, should this function log messages

    equation:
        Each action has a list of damage types they can manipulate.

        Action's damage is reduced by
            targets lowest dr value, that the action manipulates.

            If the action hit a body part.
            It is ALSO reduced by that body parts lowest dr value, that the action manipulates.
            Normally this would be the armor's dr value for that body part.

    Notes:
        unit tests for this are in commands.tests

    Returns:
        damage dealt after dr for the body part hit and the target
        The minimum value this function returns is 0.
    """
    target = command.target
    #
    if dmg_dealt is None:
        if hasattr(command, 'dmg_dealt'):
            dmg_dealt = command.dmg_dealt
        if dmg_dealt is None:
            dmg_dealt = roll(command)
    body_part_dr = 0
    body_part_inst = None
    body_part_dr_values = {}
    target_dr_values = {}
    # get an instance of the body part hit.
    if target.body.parts:
        if body_part_name:
            if body_part_name in target.body.parts:
                # bug this instance of target.body will not provide a full parts list
                # it displays the full list at command line
                # have attempted searching and getting a local instance of target
                body_part_inst = getattr(target.body, body_part_name)
    # find drs on the target and their body part hit
    if command.dmg_types:
        for dmg_type in command.dmg_types:
            # find the body part's dr values that match the commands damage types
            if hasattr(body_part_inst.dr, dmg_type):
                dr_value = getattr(body_part_inst.dr, dmg_type)
                if dr_value and dr_value > 0:
                    body_part_dr_values[dmg_type] = dr_value
            # find the targets dr values that match the commands damage types
            if hasattr(target.dr, dmg_type):
                dr_value = getattr(target.dr, dmg_type)
                if dr_value and dr_value > 0:
                    target_dr_values[dmg_type] = dr_value
    body_part_dr = None
    target_dr = None
    min_part_key = None
    min_target_key = None
    # find the lowest body part (armor) dr value among damage types this command can manipulate
    if len(body_part_dr_values) > 0:
        min_part_key = min(body_part_dr_values, key=body_part_dr_values.get)
        body_part_dr = body_part_dr_values[min_part_key]
    # find the lowest target dr value among damage types this command can manipulate
    if len(target_dr_values) > 0:
        min_target_key = min(target_dr_values, key=target_dr_values.get)
        target_dr = target_dr_values[min_target_key]
    # if target and body both have meaningful dr add them up
    damage_reduction = 0
    if body_part_dr:
        damage_reduction += body_part_dr
    if target_dr:
        damage_reduction += target_dr
    # damage is dmg_dealth - both the body part's and target's dr values
    result = dmg_dealt - damage_reduction
    if result < 0:
        result = 0
    if log:
        log_info(f"command {command.key}, Character id: {command.caller.id} | result: {result} | dmg_dealt {dmg_dealt} | body_part_name {body_part_name} | body_part_inst: {body_part_inst.name} | min_part_key {min_part_key} | min_target_key {min_target_key} | body_part_dr_values: {body_part_dr_values} | target_dr_values: {target_dr_values}")
    return result
