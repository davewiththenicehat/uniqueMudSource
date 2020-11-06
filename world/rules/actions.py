"""
Contains functions intended for use with combat commands
"""

from random import randint
from evennia.utils.logger import log_info, log_warn
from evennia.utils import inherits_from


def targeted_action(caller, target, log=False):
    """
    Used to facilitate a standard action that has a target.

    Arguments:
        caller, is the character commiting the action
        target, the target this command targets
        log=False, if True log the variables used

    Returns:
        action_result - evade_result  # the literal math result displayed
        action_result  # resulting roll of stats.action_roll
        evade_result  # resulting roll of stats.evade_roll
    """
    # get reference of the command creating the action
    action_cmd = caller.nattributes.get('deffered_command')
    if not action_cmd:
        caller.msg('You no longer have an action waiting.')
        return
    action_result = action_roll(caller, log)
    # only roll an evade if the target is a Character
    evade_result = 5
    if inherits_from(target, 'typeclasses.characters.Character'):
        evade_result = evade_roll(target, action_cmd.evade_mod_stat, log)
    if log:
        log_info(f'caller id {caller.id}: action_result: {action_result} | evade_result {evade_result}')
    return action_result - evade_result, action_result, evade_result


def evade_roll(char, evade_mod_stat, log=False):
    """
    evade roll is  a random roll between 1 and the evade's max roll.
        Plus the evade's stat modifier
        Default max is 50
    evade_roll will check if the evading Character's active command is an evasion command that is compatible with the action being used against the evader.
    evade_roll will display a message if the evasion command is used

    Arguments:
        char, is the character commiting the evade
        evade_mod_stat, the stat required to evade the action
            evade_roll was called to evade
        log=False, if True log the variables used

    Returns:
        random int between 1 and roll max plus character's stat evade modifier

    Equation:
        Each evade action can have its own max action roll.
            Default max is 50.
        Each action can have its own stat used to modify the action roll.
        evade roll is a random number from 1 to the evade roll's max plus the stat's evade modifier.
        If no evade command is active the default is used.
        An active evasion command must have the same evade_mod_stat as the
            action for the evasion commands's roll_max to be used.
    """
    roll_max = 50  # default max roll for evade rolls
    evade_mod = 0
    # get reference of the command creating the action
    evade_cmd = char.nattributes.get('deffered_command')
    if evade_cmd:  # if there is an active evade command
        if hasattr(evade_cmd, 'cmd_type'):  # if the command is an evasion command
            cmd_type = getattr(evade_cmd, 'cmd_type')
            if log:
                log_info(f'Character ID: {char.id} | cmd_type: {cmd_type} | {evade_cmd.evade_mod_stat}')
            # If the command is an evasion command and it's evade type is the same as the action
            if cmd_type == 'evasion' and evade_cmd.evade_mod_stat == evade_mod_stat:
                if log:
                    log_info(f'Character ID: {char.id}: evade_roll found a deffered command.')
                if hasattr(evade_cmd, 'roll_max'):  # if the evade command has a roll max use it instead of default
                    roll_max = getattr(evade_cmd, 'roll_max')
                evade_cmd.stop_forced()  # stop the deffered evasion command
                # inform characters in room this Character is using an evasion command.
                room_msg = f'{char.name} tries '+evade_cmd.evade_msg
                char.location.msg_contents(room_msg, exclude=(char))
                char.msg('You try '+evade_cmd.evade_msg)
        if hasattr(evade_cmd, 'evade_mod_stat'):  # if the evade command has a evade mod stat use it instead of default
            evade_mod_stat = getattr(evade_cmd, 'evade_mod_stat')
    evade_mod_name = evade_mod_stat+'_evade_mod'  # assemble name of evade modifier
    if hasattr(char, evade_mod_name):  # if the character has a evade modifier for this stat.
        evade_mod = getattr(char, evade_mod_name)
    else:
        log_warn(f'Character ID: {char.id} missing stat modifier cache: {evade_mod_name}')
    if log:
        log_info(f'stats.evade_roll | Character ID: {char.id} | roll_max: {roll_max} | evade_mod: {evade_mod} | evade_mod_stat: {evade_mod_stat } | evade_mod_name: {evade_mod_name}')
    return randint(1, roll_max) + evade_mod


def action_roll(char, log=False):
    """
    action roll is  a random roll between 1 and the action's max roll.
        Plus the action's stat modifier

    Arguments:
        char, is the character commiting the action
        log=False, if True log the variables used

    Returns:
        random int between 1 and roll max plus character's stat action modifier

    Equation:
        Each action can have its own max action roll.
            Default max is 50.
        Each action can have its own stat used to modify the action roll.
            Default stat is observation.
        Action roll is a random number from 1 to the action roll's max plus the stat's action modifier.
    """
    roll_max = 50
    action_mod_stat = 'OBS'
    action_mod = 0
    # get reference of the command creating the action
    action_cmd = char.nattributes.get('deffered_command')
    if action_cmd:  # if there is an active command
        if log:
            log_info(f'Character ID: {char.id}: action_roll found a deffered command.')
        if hasattr(action_cmd, 'roll_max'):  # if exists use the roll_max from the command instead of default
            roll_max = getattr(action_cmd, 'roll_max')
        if hasattr(action_cmd, 'action_mod_stat'):  # if exists use the stat modifier from the command instead of default
            action_mod_stat = getattr(action_cmd, 'action_mod_stat')
    action_mod_name = action_mod_stat+'_action_mod'  # assemble the name of the action modifier
    if hasattr(char, action_mod_name):  # if exists use the evade modifier on the Character
        action_mod = getattr(char, action_mod_name)
    else:
        log_warn(f'Character ID: {char.id}: missing stat modifier cache: {action_mod_name}')
    if log:
        log_info(f'Character ID: {char.id}: action_mod: {action_mod}| action_mod_stat: {action_mod_stat} | evade_mod_name: {action_mod_name}')
    return randint(1, roll_max) + action_mod
