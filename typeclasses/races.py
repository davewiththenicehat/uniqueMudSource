from typeclasses.characters import Character
from world.rules.body import HUMANOID_BODY, HUMANOID_HANDS


class Humanoid(Character):
    """
    Class to represent Humanoids.
    This is intended to be inheirited by other classes.
    """
    BODY_PARTS = HUMANOID_BODY
    HANDS = HUMANOID_HANDS


class Human(Humanoid):
    """Class that represents humans."""
    pass
