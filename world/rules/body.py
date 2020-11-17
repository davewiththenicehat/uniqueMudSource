"""
Function and variable to represent Object and Character bodies.
"""

from evennia.utils.logger import log_info
from random import randint

# Used to track condition of body parts
PART_STATUS = (
    'broke',
    'bleeding',
    'missing',
)

# represents a standard humanoid's body.
HUMANOID_BODY = (
    'head',
    'shoulders',
    'chest',
    'waist',
    'right_arm',
    'left_arm',
    'right_hand',
    'left_hand',
    'right_leg',
    'left_leg',
    'right_foot',
    'left_foot'
)

# represents Character positions
POSITIONS = (
    'sitting',
    'standing',
    'laying',
)

# keep list of Character states
# do not add busy or stunned
# default state is falsely (0). Use negative condition names. IE: dead rather than alive
CHARACTER_CONDITIONS = (
    'unconscious',
    'dead',
    'poisoned',
    'sick',
)


def get_part(target, no_underscore=False, log=None):
    """
    Return the name of a body part that exists on target

    Arguments:
        target, an Object target for get_part to choose a body part from
        no_understore=False, if True underscores '_' will be removed from the returned part name.
        log=False, if True log the variables used

    Returns:
        str, in the form of a body part description.
            Example: "head" or "waist"
        False, if this object has no body parts to hit.
        None, the function failed on the python level.

    todo:
        option to return an instance.
            option to return a specific part
        option to target low middle or high
    """
    if hasattr(target, 'body'):
        if not hasattr(target.body, 'parts'):
            if log:
                log_info(f"world.rules.get_body_part, target.id: {target.id}; target.body missing target.body.parts list.")
            return False  # body parts list required
    else:
        if log:
            log_info(f"world.rules.get_body_part, target.id: {target.id}; target missing body instance.")
        return False  # target must have a body instance
    parts_count = len(target.body.parts)  # get a max key count
    parts_count -= 1  # because indexing starts at 0
    if parts_count < 1:  # return false is there are no body parts to hit
        if log:
            log_info(f"world.rules.get_body_part, target.id: {target.id}; parts_count: {parts_count}. No parts found on target.")
        return False
    parts_key = randint(0, parts_count)
    body_part = target.body.parts[parts_key]
    if no_underscore:
        body_part = body_part.replace('_', ' ')  # remove _ from the part's name
    if log:
        log_info(f"world.rules.get_body_part, target.id: {target.id}; body_part: {body_part} | parts_key: {parts_key}")
    return body_part
