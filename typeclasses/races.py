from typeclasses.characters import Character
from world.rules.body import HUMANOID_BODY, HUMANOID_HANDS


class Humanoid(Character):
    """
    Class to represent Humanoids.
    This is intended to be inheirited by other classes.
    """
    BODY_PARTS = HUMANOID_BODY
    HANDS = HUMANOID_HANDS

    def at_object_creation(self):
        # all humanoid objects should have access to these basic attacks
        self.skills.unarmed.punch = 1
        self.skills.unarmed.kick = 1
        self.skills.evasion.dodge = 1
        return super().at_object_creation()


class Human(Humanoid):
    """Class that represents humans."""
    pass
