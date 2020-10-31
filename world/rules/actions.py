"""
Contains functions intended for use with combat commands
"""

from random import randint
from evennia.utils.logger import log_info, log_warn


def targeted_action(caller, target, log=False):
    """
    Used to facilitate a standard action that has a target.

    Arguments:
        caller, is the character commiting the action
        target, the target this command targets
        log=False, if True log the variables used

    Returns:
        action_result - dodge_result  # the literal math result displayed
        action_result  # resulting roll of stats.action_roll
        dodge_result  $ resulting roll of stats.dodge_roll
    """
    # get reference of the command creating the action
    action_cmd = caller.nattributes.get('deffered_command')
    if not action_cmd:
        caller.msg('You no longer have an action waiting.')
        return
    action_result = action_roll(caller, log)
    dodge_result = dodge_roll(target, action_cmd.dodge_mod_stat, log)
    if log:
        log_info(f'caller id {caller.id}: action_result: {action_result} | dodge_result {dodge_result}')
    return action_result - dodge_result, action_result, dodge_result


def dodge_roll(char, dodge_mod_stat, log=False):
    """
    dodge roll is  a random roll between 1 and the dodge's max roll.
        Plus the dodge's stat modifier
        Default max is 50
    dodge_roll will check if the evading Character's active command is an evasion command that is compatible with the action being used against the evader.
    dodge_roll will display a message if the evasion command is used

    Arguments:
        char, is the character commiting the dodge
        dodge_mod_stat, the stat required to evade the action
            dodge_roll was called to evade
        log=False, if True log the variables used

    Returns:
        random int between 1 and roll max plus character's stat dodge modifier

    Equation:
        Each dodge action can have its own max action roll.
            Default max is 50.
        Each action can have its own stat used to modify the action roll.
        dodge roll is a random number from 1 to the dodge roll's max plus the stat's dodge modifier.
        If no dodge command is active the default is used.
        An active evasion command must have the same dodge_mod_stat as the
            action for the evasion commands's roll_max to be used.
    """
    roll_max = 50  # default max roll for dodge rolls
    dodge_mod = 0
    # get reference of the command creating the action
    dodge_cmd = char.nattributes.get('deffered_command')
    if dodge_cmd:  # if there is an active dodge command
        if hasattr(dodge_cmd, 'cmd_type'):  # if the command is an evasion command
            cmd_type = getattr(dodge_cmd, 'cmd_type')
            if log:
                log_info(f'Character ID: {char.id} | cmd_type: {cmd_type} | {dodge_cmd.dodge_mod_stat}')
            # If the command is an evasion command and it's dodge type is the same as the action
            if cmd_type == 'evasion' and dodge_cmd.dodge_mod_stat == dodge_mod_stat:
                if log:
                    log_info(f'Character ID: {char.id}: dodge_roll found a deffered command.')
                if hasattr(dodge_cmd, 'roll_max'):  # if the dodge command has a roll max use it instead of default
                    roll_max = getattr(dodge_cmd, 'roll_max')
                dodge_cmd.stop_forced()  # stop the deffered evasion command
                # inform characters in room this Character is using an evasion command.
                room_msg = f'{char.name} tries '+dodge_cmd.evade_msg
                char.location.msg_contents(room_msg, exclude=(char))
                char.msg('You try '+dodge_cmd.evade_msg)
        if hasattr(dodge_cmd, 'dodge_mod_stat'):  # if the dodge command has a dodge mod stat use it instead of default
            dodge_mod_stat = getattr(dodge_cmd, 'dodge_mod_stat')
    dodge_mod_name = dodge_mod_stat+'_dodge_mod'  # assemble name of dodge modifier
    if hasattr(char, dodge_mod_name):  # if the character has a dodge modifier for this stat.
        dodge_mod = getattr(char, dodge_mod_name)
    else:
        log_warn(f'Character ID: {char.id} missing stat modifier cache: {dodge_mod_name}')
    if log:
        log_info(f'stats.dodge_roll | Character ID: {char.id} | roll_max: {roll_max} | dodge_mod: {dodge_mod} | dodge_mod_stat: {dodge_mod_stat } | dodge_mod_name: {dodge_mod_name}')
    return randint(1, roll_max) + dodge_mod


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
    if hasattr(char, action_mod_name):  # if exists use the dodge modifier on the Character
        action_mod = getattr(char, action_mod_name)
    else:
        log_warn(f'Character ID: {char.id}: missing stat modifier cache: {action_mod_name}')
    if log:
        log_info(f'Character ID: {char.id}: action_mod: {action_mod}| action_mod_stat: {action_mod_stat} | dodge_mod_name: {action_mod_name}')
    return randint(1, roll_max) + action_mod


def dmg_roll(command, log=False):
    """
    Get a damage roll adjusted by a character's damage stat modifier.

    Arguments:
        command, the command that is manipulating damage
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
    if hasattr(command, 'dmg_mod_stat'):  # if the command has a custom damage modifier stat use it instead
        dmg_mod_stat = getattr(command, 'dmg_mod_stat')
    dmg_mod_name = dmg_mod_stat+'_dmg_mod'
    if hasattr(caller, dmg_mod_name):  # if the caller of the command has the stat damage modifier use it.
        dmg_mod = getattr(caller, dmg_mod_name)
    return randint(1, dmg_max) + dmg_mod
