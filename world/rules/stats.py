"""
Functions for working with stats as they relate to a Character.

stats.check will frequently be used. It is the the save or stat challenge function.

Contains all equations for stat modifiers.
All functions have been documented in their docstrings.
"""

from random import randint
import math
from evennia.utils.logger import log_info

# a mapping of stat type and full names
STAT_MAP_DICT = {
    'STR':  'strength',
    'CON':  'constitution',
    'OBS':  'observation',
    'AGI':  'agility',
    'SPD':  'speed',
    'INT':  'intelligence',
    'WIS':  'wisdom',
    'CHR':  'charisma'
}


def get_stat(caller, stat_type, function_name='?'):
    """
    This function removes the need to error checking getting a stat value from a Character.
        Verifies a stat_type argument is correct.
        Checks if the stat_type stat exists on the caller.
        Returns the value of the stat.
        Raises ValueErrors if anything is wrong.
    """
    if not _is_stat_type(stat_type):
        raise ValueError(f'Character id: {caller.id}, function {function_name}, received incorrect stat_type: {stat_type}')
    if hasattr(caller, stat_type):
        stat_value = getattr(caller, stat_type)
        if stat_value:
            return stat_value.get()
        else:
            raise ValueError(f'function rules.stats.check received stat_type {stat_type}. No Character.{stat_type} found.')
    else:
        raise ValueError(f'Character id: {caller.id}, function {function_name} received stat_type {stat_type}. No Character.{stat_type} found.')


def _is_stat_type(stat_type):
    """test if a stat_type argument is correct."""
    if not isinstance(stat_type, str):
        raise ValueError('stat_type argument must be a string.')
    if stat_type.upper() in STAT_MAP_DICT:
        return True
    return False


def stat_round(stat_value):
    """
    Returns a floored number if stat_value is positive.
    Returns a ceil number if stat_value is negative.
    Allows for proper rounding.
    """
    if stat_value >= 0:
        return math.floor(stat_value)
    else:
        return math.ceil(stat_value)


def check(caller, stat_type, fail_chance, return_result=False, log=False):
    """
    Tests if a stat check is a failure or success.
        Returns True on success
        Returns False on failure

    Arguments:
        caller, is the character rolling the stat check
        stat_type is the stat being used to check
        fail_chance is the chance the stat roll will fail
        return_result=False, if True return the resulting number rather than True or False
            result = roll + stat_modifier - fail_chance
        log=False, if True log the variables used

    Equation:
        There is a predetermined chance a check will fail.
            very easy: 25 or less, average strength 0, Character picking up a cinder block (40 pound object with handles)
            easy: 26 - 50, average strength 0 Character picking up a 40 pound small dresser with no hand holds
            moderate: 51 - 75, an average strength 0 Character picking up an 80 pound child with bot hands available
            hard: 76 - 100, an average strength 0 Character picking up a 180 pound person and carring them to safety
            daunting: 100 - 124, a body builder strength 100 Character picking up a 500 pound object with both hands
        The check rolls a random number between 1 and 100.
        For every 4 ranks in a stat the check's roll receives a 1 modifider
        For example:
            3 ranks provides 0 modifider
            -4 ranks proviudes a -1 modifier
            20 ranks provides a +5 modifier
            -20 ranks provides a -5 modifier
            33 ranks providues a +8 modifier
            If the stat is at the maximum 100 the roll receives a +25 modifier
        If roll + stat modifier is more than the fail chance the check is successfull
        If roll + stat modifier is less than the fail chance the check is failure
    """
    stat_value = get_stat(caller, stat_type, 'world.stats.check')
    stat_modifier = stat_value * .25
    stat_modifier = stat_round(stat_modifier)
    roll = randint(1, 100)
    result = roll + stat_modifier - fail_chance
    success = True if result >= 1 else False
    if log:
        log_info(f'world.stats.check | Character id: {caller.id} | stat_type: {stat_type} | stat_value: {stat_value} | fail_chance: {fail_chance} | stat_modifier: {stat_modifier} | roll: {roll} | result: {result} | success: {success}')
    if return_result:
        return result
    else:
        return success


def evade_mod(caller, stat_type, log=False):
    """
    Get a stat evade modifier of a Character.

    Arguments:
        caller, is the character rolling the stat check
        stat_type, is the stat being used to check
        log=False, if True log the variables used

    Equation:
        Any stat can be used as a evade modifier.
        Most often Agility is used to modify an evade.
        For every 3 ranks in a stat a Character received a 1 modifier.
        For example:
            2 ranks provides 0 modifier
            -3 ranks provides a -1 modifier
            30 ranks provides a +10 modifier
            -30 ranks provides a -10 modifier
            100 ranks (stat max) provides a +33 modifier
    """
    stat_value = get_stat(caller, stat_type, 'world.stats.evade_mod')
    evade_modifier = stat_value * .33
    evade_modifier = stat_round(evade_modifier)
    if log:
        log_info(f'world.stats.evade_mod | Character id: {caller.id} | stat_type: {stat_type} | evade_modifier: {evade_modifier}')
    return evade_modifier


def action_mod(caller, stat_type, log=False):
    """
    Get a stat action modifier of a Character.
    Most game systems would term this as attack modifier

    Arguments:
        caller, is the character rolling the stat check
        stat_type, is the stat being used to check
        log=False, if True log the variables used

    Equation:
        Any stat can be used as a action modifier.
        Most game systems would use the term attack modifier.
        To example a physical attack.
            Both Observation and Agility would be used to modify an attack
        The termology was left open for to example stats could modifer actions other than attacks.
        For every 5 ranks in a stat a Character received a 1 modifier.
        For example:
            4 ranks provides 0 modifier
            -5 ranks provides a -1 modifier
            30 ranks provides a +6 modifier
            -30 ranks provides a -6 modifier
            100 ranks (stat max) provides a +20 modifier
    """
    stat_value = get_stat(caller, stat_type, 'world.stats.action_mod')
    action_modifier = stat_value * .2
    action_modifier = stat_round(action_modifier)
    if log:
        log_info(f'world.stats.action_mod | Character id: {caller.id} | stat_type: {stat_type} | action_modifier: {action_modifier}')
    return action_modifier


def attack_mod(caller, stat_type, log=False):
    """Forwards to world.rules.action_mod"""
    action_mod(caller, stat_type, log)


def action_cost_mod(caller, stat_type, log=False):
    """
    Returns a action cost modifier. It is in percent value.
    .25 is max and -.25 is min
    Allows for adjusting action costs by 25%

    Arguments:
        caller, is the Character whose max sanity mod is getting retreived.
        stat_type, is the stat being used to check.
        log=False, if True log the variables used.

    Equation:
        For every 4 ranks in a stat the action cost is reduced by 1%.
        For Example:
            1 rank provides a 0 modifier
            4 ranks provides a .01 modifer
            33 ranks provides a .08 modifer
            -2 ranks provides a -.01 modifer
            -33 ranks provides a -.08 modifier
            100 ranks (stat max) provides a .25 modifider
    """
    stat_value = get_stat(caller, stat_type, 'world.stats.action_cost_mod')
    action_cost_modifier = stat_value * .25
    action_cost_modifier = stat_round(action_cost_modifier)
    action_cost_modifier *= .01
    if log:
        log_info(f'world.stats.strength_max_mod | Character id: {caller.id} | stat_value: {stat_value} | action_cost_modifier: {action_cost_modifier}')
    return action_cost_modifier


def dmg_mod(caller, stat_type, log=False):
    """
    Get a stat damage modifier of a Character.
    Used to adjust the damage a Character deals with an attack type.

    Arguments:
        caller, is the character rolling the stat check
        stat_type, is the stat being used to check
        log=False, if True log the variables used

    Equation:
        Any stat can be used as a damage modifier.
        Almost always that the will be Strength for melee and Agility for ranged.
        For example, other stats could be used for special abilities.
        For every 25 ranks in a stat a Character received a 1 modifier.
        For example:
            24 ranks provides 0 modifier
            -25 ranks provides a -1 modifier
            50 ranks provides a +2 modifier
            -50 ranks provides a -2 modifier
            100 ranks (stat max) provides a +4 modifier
    """
    stat_value = get_stat(caller, stat_type, 'world.stats.dmg_mod')
    damage_modifier = stat_value * .04
    damage_modifier = stat_round(damage_modifier)
    if log:
        log_info(f'world.stats.dmg_mod | Character id: {caller.id} | stat_type: {stat_type} | damage_modifier: {damage_modifier}')
    return damage_modifier


def hp_max_mod(caller, log=False):
    """
    Returns the Constitution modifier for a Character's max hp.

    Arguments:
        caller, is the Character whose hp max is getting retreived.
        log=False, if True log the variables used

    Equation:
        For every 3 ranks of Constitution a Character receives a 1 modifier.
        For Example:
            2 ranks of constituation provides a 0 modifier.
            3 ranks of constituation provides a +1 modifier.
            -3 ranks of constituation provides a -1 modifier.
            30 ranks of constituation provides +10 modifier.
            -30 ranks of constituation provides -10 modifier.
            100 ranks (stat max) of constituation provides a +33 modifier
    """
    con_value = get_stat(caller, 'CON', 'world.stats.hp_max_mod')
    hp_max_modifier = con_value * .33
    hp_max_modifier = stat_round(hp_max_modifier)
    if log:
        log_info(f'world.stats.hp_max_mod | Character id: {caller.id} | hp_max_modifier: {hp_max_modifier}')
    return hp_max_modifier


def endurance_max_mod(caller, log=False):
    """
    Returns the Constitution modifier for a Character's max endurance.

    Arguments:
        caller, is the Character whose max endurance mod is getting retreived.
        log=False, if True log the variables used

    Equation:
        For every 3 ranks of Constitution a Character receives a 1 modifier.
        For Example:
            2 ranks of constituation provides a 0 modifier.
            3 ranks of constituation provides a +1 modifier.
            -3 ranks of constituation provides a -1 modifier.
            30 ranks of constituation provides +10 modifier.
            -30 ranks of constituation provides -10 modifier.
            100 ranks (stat max) of constituation provides a +33 modifier
    """
    con_value = get_stat(caller, 'CON', 'world.stats.endurance_max_mod')
    endurance_max_modifier = con_value * .33
    endurance_max_modifier = stat_round(endurance_max_modifier)
    if log:
        log_info(f'world.stats.endurance_max_mod | Character id: {caller.id} | endurance_max_modifier: {endurance_max_modifier}')
    return endurance_max_modifier


def sanity_max_mod(caller, log=False):
    """
    Returns the Wisdom modifier for a Character's max sanity.

    Arguments:
        caller, is the Character whose max sanity mod is getting retreived.
        log=False, if True log the variables used

    Equation:
        For every 3 ranks of Wisdom a Character receives a 1 modifier.
        For Example:
            2 ranks of wisdom provides a 0 modifier.
            3 ranks of wisdom provides a +1 modifier.
            -3 ranks of wisdom provides a -1 modifier.
            30 ranks of wisdom provides +10 modifier.
            -30 ranks of wisdom provides -10 modifier.
            100 ranks (stat max) of wisdom provides a +33 modifier
    """
    wis_value = get_stat(caller, 'WIS', 'world.stats.sanity_max_mod')
    wisdom_max_modifier = wis_value * .33
    wisdom_max_modifier = stat_round(wisdom_max_modifier)
    if log:
        log_info(f'world.stats.wisdom_max_mod | Character id: {caller.id} | wis_value: {wis_value} | wisdom_max_modifier: {wisdom_max_modifier}')
    return wisdom_max_modifier


def load_max_mod(caller, log=False):
    """
    Returns the strength modifier for a Character's max sanity.

    Arguments:
        caller, is the Character whose max sanity mod is getting retreived.
        log=False, if True log the variables used

    Equation:
        For every ranks of Wisdom a Character receives a 1 modifier.
        For Example:
            1 ranks of strength provides a 1 modifier.
            3 ranks of strength provides a +3 modifier.
            -3 ranks of strength provides a -3 modifier.
            30 ranks of strength provides +30 modifier.
            -30 ranks of strength provides -30 modifier.
            100 ranks (stat max) of strength provides a +100 modifier
    """
    str_value = get_stat(caller, 'STR', 'world.stats.load_max_mod')
    strength_max_modifier = str_value
    strength_max_modifier = stat_round(strength_max_modifier)
    if log:
        log_info(f'world.stats.strength_max_mod | Character id: {caller.id} | str_value: {str_value} | strength_max_modifier: {strength_max_modifier}')
    return strength_max_modifier


def busy_mod(caller, log=False):
    """
    Returns a busy modifier. It is in percent value.
    .25 is max and -.25 is min
    Allows speed to adjust busy actions by 25%

    Arguments:
        caller, is the Character whose max sanity mod is getting retreived.
        log=False, if True log the variables used

    Equation:
        For every 4 ranks in speed the busy time is reduced by 1%.
        For Example:
            1 rank provides a 0 modifier
            4 ranks provides a .01 modifer
            33 ranks provides a .08 modifer
            -2 ranks provides a -.01 modifer
            -33 ranks provides a -.08 modifier
            100 ranks (speed max) provides a .25 modifider
    """
    spd_value = get_stat(caller, 'SPD', 'world.stats.busy_mod')
    busy_modifier = spd_value * .25
    busy_modifier = stat_round(busy_modifier)
    busy_modifier *= .01
    if log:
        log_info(f'world.stats.strength_max_mod | Character id: {caller.id} | spd_value: {spd_value} | busy_modifier: {busy_modifier}')
    return busy_modifier


def stunned_mod(caller, log=False):
    """
    Returns a stunned modifier. It is in percent value.
    .25 is max and -.25 is min
    Allows for adjusting stunned time by 25%

    Arguments:
        caller, is the Character whose max sanity mod is getting retreived.
        log=False, if True log the variables used

    Equation:
        For every 4 ranks in wisdom the stunned time is reduced by 1%.
        For Example:
            1 rank provides a 0 modifier
            4 ranks provides a .01 modifer
            33 ranks provides a .08 modifer
            -2 ranks provides a -.01 modifer
            -33 ranks provides a -.08 modifier
            100 ranks (wisdom max) provides a .25 modifider
    """
    wis_value = get_stat(caller, 'WIS', 'world.stats.stunned_mod')
    stunned_modifier = wis_value * .25
    stunned_modifier = stat_round(stunned_modifier)
    stunned_modifier *= .01
    if log:
        log_info(f'world.stats.strength_max_mod | Character id: {caller.id} | wis_value: {wis_value} | stunned_modifier: {stunned_modifier}')
    return stunned_modifier


def purchase_mod(caller, log=False):
    """
    Returns a purchase modifier. It is in percent value.
    .25 is max and -.25 is min
    Allows for adjusting purchase costs by 25%

    Arguments:
        caller, is the Character whose max sanity mod is getting retreived.
        log=False, if True log the variables used

    Equation:
        For every 4 ranks in wisdom the stunned time is reduced by 1%.
        For Example:
            1 rank provides a 0 modifier
            4 ranks provides a .01 modifer
            33 ranks provides a .08 modifer
            -2 ranks provides a -.01 modifer
            -33 ranks provides a -.08 modifier
            100 ranks (wisdom max) provides a .25 modifider
    """
    chr_value = get_stat(caller, 'CHR', 'world.stats.purchase_mod')
    purchase_modifier = chr_value * .25
    purchase_modifier = stat_round(purchase_modifier)
    purchase_modifier *= .01
    if log:
        log_info(f'world.stats.strength_max_mod | Character id: {caller.id} | chr_value: {chr_value} | purchase_modifier: {purchase_modifier}')
    return purchase_modifier
