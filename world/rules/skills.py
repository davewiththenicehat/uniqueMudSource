"""
Variables used to describe UM skills.

Skills are grouped into skill sets.

Each skill set that has one or more actions in it should have a matching
command set.
    For example the evasion skill set has a corrisponding evasion command set.
    Every command in that command set has to have it's class attribute cmd_type
    set to the name of the command or skill set.
        For example CmdDodge.cmd_type='evasion', for the dodge action.

Each skill set has skills (actions or abilities) it grants access to learn.
    For example 'unarned' grants access to the 'punch' and 'kick' actions.
    Without the parent skill set those commands can not be learned.

    Each skill has a learning dificulty.
    This is used to adjust how difficult it is to learn it.

    Each skill has a completion difficulty.
    This is used to represent how difficult it is to complete the action.
    This should have no effect on flat abilities that have no corrisponding
    command.

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

EVASION = {
    'dodge': {
        'learn_diff': 1,
        'comp_diff': 2,
    }
}

UNARMED = {
    'punch': {
        'learn_diff': 1,
        'comp_diff': 2,
    },
    'kick': {
        'learn_diff': 2,
        'comp_diff': 2,
    }
}

SKILLS = {
    'evasion': tuple(EVASION.keys()),
    'unarmed': tuple(UNARMED.keys())
}
