"""
Contains functions intended for use with combat commands
"""

from random import randint
from evennia.utils.logger import log_info, log_warn
from evennia.utils import inherits_from
from utils import um_utils
from world.rules import skills

SITTING_EVADE_PENALTY = 20
LAYING_EVADE_PENALTY = 50
EVADE_MIN = 5
EVADE_MAX = 51

COST_LEVELS = {
    'very easy': .01,
    'very_easy': .01,
    'easy': .1,
    'moderate': 1,
    'hard': 3,
    'daunting': 5
}

def targeted_action(char, target, status_type='busy', log=False):
    """
    Used to facilitate a standard action that has a target.

    Arguments:
        char, is the character commiting the action
        target, the target this command targets
        log=False, if True log the variables used

    Returns:
        action_result - evade_result  # the literal math result displayed
        action_result  # resulting roll of stats.action_roll
        evade_result  # resulting roll of stats.evade_roll

    Notes:
        Objects can not evade and have a evade result of 5
        An unconscious Character can not evade and has an evade result of 5
    """
    # get reference of the command creating the action
    action_cmd = char.get_cmd(status_type)

    # stop if there is not command deferred for the status type passed.
    if not action_cmd:
        if log:
            log_info(f"actions.targeted_action, char id {char.id}: char has no deferred actions.")
        char.msg('You no longer have an action waiting.')
        return


    action_result = action_roll(char, log)
    # only roll an evade if the target is a Character
    evade_result = EVADE_MIN  # default evade for non Character Objects
    if inherits_from(target, 'typeclasses.characters.Character'):
        evade_result = evade_roll(target, action_cmd.evade_mod_stat, log)
    if log:
        log_info(f'actions.targeted_action, char id {char.id}: ' \
                 f'action_result: {action_result} | evade_result {evade_result}')
    return action_result - evade_result, action_result, evade_result


def evade_roll(char=None, evade_mod_stat=None, log=False, unit_test=False):
    """evade roll is  a random roll between 1 and the evade's max roll.
        Plus the evade's stat modifier
        Default max is 51
    evade_roll will check if the evading Character's active command is an
        evasion command that is compatible with the action being used against
        the evader.
    evade_roll will add all wielded item.evd_roll_max_mod to the roll_max
        If an evade command is used.
        If evade_mod_stat is in the item.evd_stats tuple
    evade_roll will display a message if the evasion command is used

    Equation,
        Each attack action has a stat used to evade it.
            Physical attack usually require Agility to evade.
            Mental attacks usually require Wisdom to evade.
            Most attacks are physical.
        evade roll is a random number from 1 to the Characters evade roll max.
            Plus the Character's evade stat modifier.
        Each Character has an evade roll max for each stat.
            Default evade roll max for each stat is 51.
            Changing Character's evade roll max has a strong affect to combat.
        If no evade action is active the Character's default roll max is used.
        If a Character has an evade action active.
            Ranks in the evade action's skill will modifify the roll max.
            All wielded items that can modify the max roll will.
        If a Character is sitting or laying they will suffer a penalty.
            Sitting provides a 20 penalty
            Laying provides a 50 penalty
        If a Character is unconscious they always roll a 5 for Evade Rolls.
        An evade roll result can not be less than 5.

    Args:
        char (Character): is the character commiting the evade
        evade_mod_stat (str): the stat required to evade the action
        log (bool): If True log the variables used. Defaul False
        unit_test (bool): If True evade_roll will display variables to screen. Default is False

    Returns:
        evade_rull (int): random int between 1 and roll max plus character's stat evade modifier
            Minimum is 5

    """
    if not char:
        raise ValueError("world.rules.actions.evade_roll, argument 1 char required. " \
                         "Argument 1 is an instance of a Character.")
    elif not evade_mod_stat:
        raise ValueError("world.rules.actions.evade_roll, " \
                         "argument 2 evade_mod_stat required. " \
                         "Argument 2 is a string example of a Character stat." \
                         "Example: 'AGI'.")
    # collected roll_max from character, use default if character does not have one.
    roll_max = getattr(char.evd_max, evade_mod_stat, EVADE_MAX)
    evade_mod = 0
    # if the Character is unconscious they can not dodge.
    if char.condition.unconscious:
        return EVADE_MIN
    if char.position == 'sitting':
        evade_mod -= SITTING_EVADE_PENALTY
    if char.position == 'laying':
        evade_mod -= LAYING_EVADE_PENALTY
    # get reference of the command creating the action
    evade_cmd = char.get_cmd()
    if evade_cmd:  # if there is an active command
        cmd_type = getattr(evade_cmd, 'cmd_type', False)
        if cmd_type:  # verify cmd_type existance
            if log:
                log_info(f"Character ID: {char.id} | cmd_type: {cmd_type} | " \
                         f"evade_cmd.evade_mod_stat: {evade_cmd.evade_mod_stat} | " \
                         f"evade_mod_stat: {evade_mod_stat}")
            # If the command is an evasion command and
            # it's evade type is the same as the attack action's
            if cmd_type == 'evasion' and evade_cmd.evade_mod_stat == evade_mod_stat:
                if log:
                    log_info(f'Character ID: {char.id}: evade_roll found a deferred command.')
                # get Character's skill bonus modifier
                roll_max += skills.evd_max_mod(evade_cmd)
                # check if any wielded items will assist with this evasion
                wielded_items = char.wielding()
                if wielded_items:  # target is wielding item(s)
                    for item in wielded_items:
                        # if the item can assist with this dodge type
                        if evade_mod_stat in item.evd_stats:
                            roll_max += item.evd_roll_max_mod
                            if log:
                                msg = f"Character ID: {char.id} | item {item.dbref} " \
                                      f"added {item.evd_roll_max_mod} to evasion."
                                log_info(msg)
                evade_cmd.stop_forced()  # stop the deffered evasion command
                evade_cmd.def_act_comp()  # run command completion tasks
                # message target and room of the evade action.
                room_msg = f'/Me tries '+evade_cmd.evade_msg
                char.location.emote_contents(room_msg, char, exclude=(char))
                char.msg('You try '+evade_cmd.evade_msg)
        # if the evade command has a evade mod stat use it instead of default
        evade_mod_stat = getattr(evade_cmd, 'evade_mod_stat', evade_mod_stat)
    evade_mod_name = evade_mod_stat+'_evade_mod'  # assemble name of evade modifier
    if hasattr(char, evade_mod_name):  # if the character has a evade modifier for this stat.
        stat_mod = getattr(char, evade_mod_name)
        evade_mod += stat_mod
    else:
        log_warn(f'Character ID: {char.id} missing stat modifier cache: {evade_mod_name}')
    result = randint(1, roll_max) + evade_mod
    # An evade result can not be lower than evades lowest possible minimum
    if result < EVADE_MIN:
        result = EVADE_MIN
    if log:
        msg = f'actions.evade_roll, Character ID: {char.id} | result {result} " \
              f"| roll_max: {roll_max} | evade_mod: {evade_mod} | " \
              f"evade_mod_stat: {evade_mod_stat } | evade_mod_name: {evade_mod_name}'
        log_info(msg)
    if unit_test:
        msg = f"roll_max: {roll_max} | evade_mod: {evade_mod} | " \
              f"evade_mod_stat: {evade_mod_stat } | evade_mod_name: " \
              f"{evade_mod_name}"
        char.msg(msg)
    return result

#action_roll(target, log, unit_test)
def action_roll(char, log=False, unit_test=False):
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
        If an action requires a wielded item that item can adjust the actions max roll.
        Action roll is a random number from 1 to the action roll's max plus the stat's action modifier.
    """
    roll_max = 50
    action_mod_stat = 'OBS'
    action_mod = 0
    # get reference of the command creating the action
    action_cmd = char.get_cmd('busy')
    if action_cmd:  # if there is an active command
        if log:
            msg = f'Character ID: {char.id}: action_roll found a deffered command.'
            log_info(msg)
        # if exists use the roll_max from the command instead of default
        # this has already been adjusted by wielded items
        roll_max = getattr(action_cmd, 'roll_max', roll_max)
        # adjust the max roll by skill ranks
        roll_max += skills.act_max_mod(action_cmd)
        # if exists use the stat modifier from the command instead of default
        action_mod_stat = getattr(action_cmd, 'action_mod_stat', action_mod_stat)
    action_mod_name = action_mod_stat+'_action_mod'  # assemble action modifer name
    # if exists use the action modifier on the Character
    if hasattr(char, action_mod_name):
        action_mod = getattr(char, action_mod_name, action_mod)
    else:
        log_warn(f'Character ID: {char.id}: missing stat modifier cache: ' \
                 f'{action_mod_name}')
    result = randint(1, roll_max) + action_mod
    if log:
        msg = f'actions.action_roll, Character ID: {char.id}: result ' \
              f'{result} | roll_max: {roll_max} | action_mod: {action_mod}| ' \
              f'action_mod_stat: {action_mod_stat} | evade_mod_name: ' \
              f'{action_mod_name}'
        log_info(msg)
    if unit_test:
        msg = f'actions.action_roll, Character ID: {char.id}: result ' \
              f'{result} | roll_max: {roll_max} | action_mod: {action_mod}| ' \
              f'action_mod_stat: {action_mod_stat} | evade_mod_name: ' \
              f'{action_mod_name}'
        char.msg(msg)
    return result


def action_cost(char, cost_level=None, cost_stat=None, subt_cost=True, log=False):
    """Action cost will calculate the cost of an action.
    remove that cost from the Character and return a numerical value of the cost.

    Unit test for this function is in commands.tests.TestCommands.test_methods

    Equation, cost - (cost * stat_action_cost_mod)

    Args:
        char (Character), is the character commiting the action
        cost_stat (str), The Character stat this function will use for this action.
            If falsley action cost will attempt to collect it from a deferred command.
            If passed a Falsey argument and no deferred command is available or cost_stat
                is falsey on the deferred. Function returns 0.
        cost_level (str), level this action should cost.
            Accepts: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number or an integer
            If a number, the cost is that number.
            If falsley action cost will attempt to collect it from a deferred command.
            If passed a Falsey argument and no deferred command is available or cost_level
                is falsey on the deferred. Function returns 0.
        subt_cost=True, if True, the cost will be subtracted from the cost_stat.
        log=False, if True log the variables used

    Returns:
        cost (int): the numrical value that the stat will be drained.

    todo:
        make a cache for the equation: https://docs.python.org/3/library/functools.html
    """
    action_cmd = char.nattributes.get('deffered_command')
    if not cost_level or not cost_stat:  # this command does not have a cost
        if action_cmd:
            if not cost_stat:
                # if the command has a cost_stat, use it
                cost_stat = getattr(action_cmd, 'cost_stat', None)
            if not cost_level:
                # if the command has a cost_level, use it
                cost_level = getattr(action_cmd, 'cost_level', None)
        else:
            return 0
    if not cost_level:
        return 0
    if not cost_stat:
        return 0
    # get the stat modifier for this action, IE char.CON_action_cost_mod
    cost_stat_instance = getattr(char, cost_stat, False)
    if cost_stat_instance:
        # each cost attribute (END, will) has a modifier_stat.
        # types are stats WIS, CON so on
        # base stats CON, WIS so on will use themselves as the cost modifider
        cost_mod_stat = getattr(cost_stat_instance, 'modifier_stat', cost_stat)
    else:  # an instance of the stat is required
        err_msg = f"rules.action.cost, character: {char.id}, "
        if action_cmd:
            err_msg += f"action: {action_cmd.key}, "
        err_msg += f"Failed to find an instance of stat {cost_stat} on " \
                   "character. Find acceptable stats in world.rules.stats.STATS."
        um_utils.error_report(err_msg, char)
        return False
    stat_action_cost_mod = getattr(char, f"{cost_mod_stat}_action_cost_mod", 0)
    # set the base cost for the cost
    if isinstance(cost_level, str):
        base_cost = COST_LEVELS.get(cost_level, False)
        if not base_cost:
            err_msg = f"rules.action.cost, character: {char.id} | "
            if action_cmd:
                err_msg += f"action: {action_cmd.key} | "
            err_msg += "cost_level argument must equal 'very easy', 'easy', " \
                       "'moderate' 'hard', 'daunting' or a number."
            um_utils.error_report(err_msg, char)
            return 0
    # if the cost level is a number, use it as base cost
    elif isinstance(cost_level, (int, float)):
        base_cost = cost_level
    else:
        err_msg = f"rules.action.cost, character: {char.id} | "
        if action_cmd:
            err_msg += f"action: {action_cmd.key} | "
        err_msg += "cost_level argument must equal 'very easy', 'easy', " \
                   "'moderate' 'hard', 'daunting' or a number."
        um_utils.error_report(err_msg, char)
        return 0
    # adjust the action cost by the stat action cost modifier
    cost = base_cost - (base_cost * stat_action_cost_mod)
    if log:
        log_msg = f"rules.action_cost, character: {char.id} | "
        if action_cmd:
            log_msg += f"action: {action_cmd.key} "
        log_msg += f"| cost: {cost} | cost_stat: {cost_stat} | " \
                   f"base_cost: {base_cost} | {cost_mod_stat}_action_cost_mod: " \
                   f"{stat_action_cost_mod} | cost_stat_instance.name: " \
                   f"{cost_stat_instance.name} | cost_mod_stat: {cost_mod_stat}"
        log_info(log_msg)
    if subt_cost:  # subtract the cost
        cost_stat_instance.set(cost_stat_instance - cost)
    return cost
