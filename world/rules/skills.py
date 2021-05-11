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
    For example 'unarmed' grants access to the 'punch' and 'kick' actions.
    Without the parent skill set those commands can not be learned.

    Each skill has a rank and experience tracker on the Character.
    This is represented as a ListElement in Character.skills.skill_set_name.
    The rank tracker is an intiger with the name of the skill.
        IE: char.skills.unarmed.punch
    The experience tracker is an intiger with the name of the skill+'_exp'.
        IE: char.skills.unarmed.punch_exp
        The experience tracker is a direct reflection of the time the Character has used
        the represented skill.
        This tracker does not set to zero when a rank is increased.
        This tracker increases if the Character succeds or fails with the action.
            This occurs when status_functions.status_delay_stop calls the
            command's deferred_action method.
        This tracker does not increase if the Character stops the action.
    Refer to utils.element.ListElement, for full usage. The function simular dictionaries.

    Each skill has a learning dificulty.
    This is used to adjust how difficult it is to learn it.
    This is represented in the corrispinding command for the skill. As an instance
        attribute named 'learn_diff' and is an int.
    Each rank has a required time investment to unlock that rank. The number for these are
        as of yet undetermined. The place holder for now will be 5 minutes for each rank.
    The equation for learning difficulty is:
        Plus 25% exp for each step of the action's learning difficulty past 'very easy'
            'very easy': 100% of skill ranks, rounded up
            'easy': 125% of skill ranks, rounded up
            'moderate', 150% of skill ranks, rounded up
            'hard', 175% of skill ranks, rounded up
            'daunting', 200% of skill ranks, rounded up

    Each skill has a completion difficulty.
    This is used to represent how difficult it is to complete the action.
    This should have no effect on flat abilities that have no corrisponding
    command.
    This is represented in the corrispinding command for the skill. As an instance
        attribute named 'comp_diff' and is an int.
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

# used to convert difficulty levels to numbers
DIFFICULTY_LEVELS = {
    1: 'very easy',
    2: 'easy',
    3: 'moderate',
    4: 'hard',
    5: 'daunting'
}

# lists of each command or action type, reference above docstring
EVASION = ('dodge',)

UNARMED = ('punch', 'kick')

ONE_HANDED = ('stab',)

# a dictionary of skill sets.
SKILLS = {
    'evasion': tuple(EVASION)+('skill_points',),
    'unarmed': tuple(UNARMED)+('skill_points',),
    'one_handed': tuple(ONE_HANDED)+('skill_points',)
}

# this is created in function rank_requirement
# It is added to as rank requirements are requested.
_RANK_REQUIREMENTS = {
    1: [0, 300],
    2: [0, 375],
    3: [0, 450],
    4: [0, 525],
    5: [0, 600],
    'very easy': [0, 300],
    'easy': [0, 375],
    'moderate': [0, 450],
    'hard': [0, 525],
    'daunting': [0, 600]
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


def rank_requirement(rank, learn_diff):
    """Get the expereince required for a rank.

    The equation for learning difficulty is:
        Plus 25% exp for each step of the action's learning difficulty past 'very easy'
            'very easy': 100% of skill ranks, rounded up
            'easy': 125% of skill ranks, rounded up
            'moderate', 150% of skill ranks, rounded up
            'hard', 175% of skill ranks, rounded up
            'daunting', 200% of skill ranks, rounded up
        A rank 1 very easy skill required 300 experience.

    Args:
        rank (int): The skill rank you would like to get the required expereince
            for.
        learn_diff (str): The learning difficulty you would like to get the
            required expereince for.
            Acceptable strings: 'very easy', 'easy', 'moderate', 'hard' or
                'daunting'.

    Returns:
        exp_req (int): The experience required for this rank, and learning
            difficulty.
    """
    # add ranks to the global dictionary if they are not there.
    if rank not in _RANK_REQUIREMENTS[learn_diff]:
        array_size = len(_RANK_REQUIREMENTS[learn_diff])
        diff_array = _RANK_REQUIREMENTS[learn_diff]
        for _ in range(array_size, rank+1):
            diff_array.append(diff_array[(-1)] + diff_array[1])
    return _RANK_REQUIREMENTS[learn_diff][rank]


def learn_time(char, skill_name=False, rank=False, learn_diff=False):
    """Get time it takes to learn a new rank in a skill.

    This function assumes you have verified skill_name is in Character.skills.

    Args:
        char (Character): A instance of a Character that is requesting the increase time.
        skill_name (str, optional): A name of a skill to increase.
        rank (int, optional): Ignore Character's ranks and calculate for rank instead.
            False by default.
            Required if skill_name is not passed.
        learn_diff (int or str, optional): The learn difficulty for a skill.
            False by default.
            Overrides skill_name if both skill_name and learn_diff are passed.

    Returns:
        time_required (int): Time required to learn a new rank in skill_name.

    Equation:
        experience required for the rank multiplied
        ranks 1 - 9, exp required * 3
        ranks 10 - 19, exp required * 5
        ranks 20 - 29, exp required * 10
        ranks 30 - 39, exp required * 20
        ranks 40 - 49, exp required * 40
        ranks 50+, exp required * rank

    """
    if skill_name:
        # get an instance of the skill set the skill is in.
        for skill_set_name in char.skills.skills:
            skill_set = getattr(char.skills, skill_set_name, False)
            if skill_name in skill_set:
                break
        # get an instance of the command
        for cmd_set in char.cmdset.get():
            cmd_inst = cmd_set.get(skill_name)
            if cmd_inst:
                continue
    rank = rank if rank else skill_set[skill_name] + 1
    # get base exp required by rank and learning difficulty
    if learn_diff:
        exp_required = rank_requirement(rank, learn_diff)
    else:
        exp_required = rank_requirement(rank, cmd_inst.learn_diff)
    # calculate the learning time required
    if rank < 10:
        time_required = exp_required * 3
    elif rank < 20:
        time_required = exp_required * 5
    elif rank < 30:
        time_required = exp_required * 10
    elif rank < 40:
        time_required = exp_required * 20
    elif rank < 50:
        time_required = exp_required * 40
    else:
        time_required = exp_required * rank
    return time_required


def learn(char_id, skill_name):
    """Cause a Character to learn a new skil rank.

    Made to survive serialization into database.

    Args:
        char_id (str): the db_ref of the Character learning a new skill rank.
        skill_name (str): The skill the Character is learning.
    """
