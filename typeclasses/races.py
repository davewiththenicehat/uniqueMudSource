from typeclasses.characters import Character
from world.rules.body import HUMANOID_BODY


class Humanoid(Character):
    """
    Class to represent Humanoids.
    This is intended to be inheirited by other classes.
    """
    BODY_PARTS = HUMANOID_BODY


class Human(Humanoid):
    """Class that represents humans."""
    pass
