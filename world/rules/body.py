"""
Function and variable to represent Object and Character bodies.

Some character races many have many hands or hands with odd names.
Avoid using right_hand left_hand logic.

For a full reference on how the body functions on objects refer to:
    typeclasses.mixins.CharExAndObjMixin

Rooms do not have bodies.
"""

from evennia.utils.logger import log_info
from random import randint

# Used to track condition of body parts
PART_STATUS = (
    'broke',
    'bleeding',
    'missing',
    'occupied',
    'wielding',
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
    'learning'
)

# BELOW lists specific to species of Characters

# represents a standard humanoid's body.
HUMANOID_BODY = (
    'head',
    'shoulders',
    'chest',
    'waist',
    'back',
    'right_arm',
    'left_arm',
    'right_hand',
    'left_hand',
    'right_leg',
    'left_leg',
    'right_foot',
    'left_foot'
)

# represents the appendage a humanoid Character uses to hold objects
HUMANOID_HANDS = (
    'right_hand',
    'left_hand'
)


def get_part(target, part_name=None, log=False):
    """Return a randon or specified instance of a part on the object's body.

    Body part instances are ListElements. List Elements function very simular
        to python's dict object.
        ref: utils.element.ListElement
        Created using keys: world.rules.body.PART_STATUS:
            ('broke', 'bleeding', 'missing', 'occupied', 'wielding',)
    Body parts retain python's standard attribute format.
    The name attribute is the name of the body part.
    As it is an instance of an object spaces are replaced with _.
    Get a parts name with:
        part = body.body_part()
        part_name = part.name.replace('_', ' ')  # replace _ with spaces

    Unit Tests:
        commands.test.TestCommands.test_get_body_part
        world.tests.test_rules
        commands.test.TestCommands.test_wear_remove

    Args:
        target (Object), an evennia Object for get_part to choose a body part from
        part_name (bool, optional), String name of a body part. Defaults to None.
            Example: 'left_leg'
        log (bool, optional), Should variables be logged. Defaults to False.

    Returns:
        body_part (ListElement): Functions very simular to python dict.
            ref: utils.element.ListElement
            Created using keys: world.rules.body.PART_STATUS:
                ('broke', 'bleeding', 'missing', 'occupied', 'wielding',)

    Todo:
        option to target low middle or high
    """

    # if the target has no body or parts stop the method
    if hasattr(target, 'body'):
        if not hasattr(target.body, 'parts'):
            if log:
                log_info(f"world.rules.get_body_part, target.id: {target.id}; target.body missing target.body.parts list.")
            return False  # body parts list required
    else:
        if log:
            log_info(f"world.rules.get_body_part, target.id: {target.id}; target missing body instance.")
        return False  # target must have a body instance

    # collect a part name if none was passed.
    if not part_name:
        parts_count = len(target.body.parts)  # get a max key count
        parts_count -= 1  # because indexing starts at 0
        if parts_count < 1:  # return false is there are no body parts to hit
            if log:
                log_info(f"world.rules.get_body_part, target.id: {target.id}; parts_count: {parts_count}. No parts found on target.")
            return False
        parts_key = randint(0, parts_count)
        part_name = target.body.parts[parts_key]
        if log:
            log_info(f"world.rules.get_body_part, target.id: {target.id}; body_part: {part_name} | parts_key: {parts_key}")

    # return the body part, or false if a part was not found
    return getattr(target.body, part_name, False)
