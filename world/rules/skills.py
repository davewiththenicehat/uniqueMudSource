import math

"""
Variables used to describe UM skills.

Skills are grouped into skill sets.

Each skill set that has one or more actions in it should have a matching
command set.
    For example the evasion skill set has a corrisponding evasion command set.
    Every command in that command set has to have it's class attribute cmd_type
    set to the name of the command or skill set.
        For example CmdDodge.cmd_type='evasion', for the dodge action.

Each skill set has skills (commands, actions or abilities) it grants access to learn.
    For example 'unarned' grants access to the 'punch' and 'kick' actions.
    Without the parent skill set those commands can not be learned.

    Each skill has a learning dificulty.
    This is used to adjust how difficult it is to learn it.

    Each skill has a completion difficulty.
    This is used to represent how difficult it is to complete the action.
    This should have no effect on flat abilities that have no corrisponding
    command.
    The equation for completion difficulty is:
        Minus 20% for each step of the action's completion difficulty past 'very easy'
            'very easy': 100% of skill ranks, rounded up
            'easy': 80% of skill ranks, rounded up
            'moderate', 60% of skill ranks, rounded up
            'hard', 40% of skill ranks, rounded up
            'daunting', 20% of skill ranks, rounded up

    Difficulty levels are:
        'very easy': 1
        'easy': 2
        'moderate': 3
        'hard': 4
        'daunting': 5
"""

DIFFICULTY_LEVELS = {
    1: 'very easy',
    2: 'easy',
    3: 'moderate',
    4: 'hard',
    5: 'daunting'
}

EVASION = ('dodge',)

UNARMED = ('punch', 'kick')

ONE_HANDED = ('stab',)

SKILLS = {
    'evasion': tuple(EVASION)+('skill_points',),
    'unarmed': tuple(UNARMED)+('skill_points',),
    'one_handed': tuple(ONE_HANDED)+('skill_points',)
}

def cmd_diff_mod(cmd_comp_diff, skill_ranks):
    """
    Arguments:
        cmd_comp_diff=int(), Command.comp_diff or the completion difficulty of the command.
        skill_ranks=int(), char.skills.SKILL_SET_NAME.SKILL_NAME, or ranks in a skill

    Returns:
        The skill rank modifier after the commands difficulty adjustment.

    Equation:
        Minus 20% for each step of the action's completion difficulty past 'very easy'
            'very easy': 100% of skill ranks, rounded up
            'easy': 80% of skill ranks, rounded up
            'moderate', 60% of skill ranks, rounded up
            'hard', 40% of skill ranks, rounded up
            'daunting', 20% of skill ranks, rounded up
    """
    diff_mod = (6 - cmd_comp_diff) * .2 * skill_ranks
    return math.ceil(diff_mod)

def evd_max_mod(command):
    """
    Return the skill based evade modifer for a Character's current evade command.

    Arguments:
        command=Command, an instance of a command

    Returns:
        int, comand.caller skill based evade modifier
            (6 - command.comp_diff) * .2 * caller.skills.SET_NAME.SKILL_NAME
            returns 0 if
                command is not an evasion command
                character has no ranks in the skill

    Notes:
        MUST return a number. It will be directly used without further testing in equations.

    Equation:
        Evade action's roll max is modified by ranks in the skill.
        Minus 20% for each step of the action's completion difficulty past 'very easy'
            'very easy': 100% of skill ranks, rounded up
            'easy': 80% of skill ranks, rounded up
            'moderate', 60% of skill ranks, rounded up
            'hard', 40% of skill ranks, rounded up
            'daunting', 20% of skill ranks, rounded up
    """
    # this is not a evasion
    if not command.cmd_type == 'evasion':
        return 0
    caller = command.caller
    evade_type = command.cmd_type
    evade_inst = getattr(caller.skills, evade_type)
    skill_name = command.skill_name
    # get ranks in skill or 0 if the skill is unknown
    skill_ranks = getattr(evade_inst, skill_name, 0)
    skill_ranks = int(skill_ranks)
    # return skill rank modifier after command difficulty modifier
    return cmd_diff_mod(command.comp_diff, skill_ranks)


def act_max_mod(command):
    """
    Return the skill based action modifer for a Character's current action command.

    Arguments:
        command=Command, an instance of a command

    Returns:
        int, comand.caller skill based action modifier
            (6 - command.comp_diff) * .2 * caller.skills.SET_NAME.SKILL_NAME
            returns 0 if
                character has no ranks in the skill

    Notes:
        MUST return a number. It will be directly used without further testing in equations.

    Equation:
        Action's roll max is modified by ranks in the skill.
        Minus 20% for each step of the action's completion difficulty past 'very easy'
            'very easy': 100% of skill ranks, rounded up
            'easy': 80% of skill ranks, rounded up
            'moderate', 60% of skill ranks, rounded up
            'hard', 40% of skill ranks, rounded up
            'daunting', 20% of skill ranks, rounded up
    """
    caller = command.caller
    action_type = command.cmd_type
    action_inst = getattr(caller.skills, action_type)
    skill_name = command.skill_name
    # get ranks in skill or 0 if the skill is unknown
    skill_ranks = getattr(action_inst, skill_name, 0)
    skill_ranks = int(skill_ranks)
    result = cmd_diff_mod(command.comp_diff, skill_ranks)
    return result
