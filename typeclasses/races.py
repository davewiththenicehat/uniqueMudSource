from typeclasses.characters import Character
from world.rules.body import HUMANOID_BODY, HUMANOID_HANDS

"""
When adding a new race.

If it's body differs from a base  type already tested
Add it to the looped tests in commands.tests.CommandTests.test_wear_remove.
To do this
    add a parts and hands list to world.rules.body
        Use those lists in the race class in this module as in Humanoid
    Add a RaceArmor to typeclasses.equipment.clothing
        Use HumanoidArmor as an example
    add the race to commands.tests.CommandTest.test_wear_remove.race_list
"""

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
        self.skills.unarmed.punch_msg = True
        self.skills.unarmed.kick = 1
        self.skills.unarmed.kick_msg = True
        self.skills.evasion.dodge = 1
        self.skills.unarmed.dodge = True
        return super().at_object_creation()


class Human(Humanoid):
    """Class that represents humans."""
    pass
