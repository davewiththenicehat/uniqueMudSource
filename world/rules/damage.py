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
from world.rules.obj_lists import DAMAGE_TYPES

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
TYPES = DAMAGE_TYPES


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


class DamageElement(ListElement):
    """
    A child of ListElement used to represent damage.
    It uses list (tuple) world.rules.obj_lists.DamageTypes
    """
    pass
