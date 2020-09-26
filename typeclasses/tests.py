from evennia.commands.default.tests import CommandTest
from evennia import create_object
from typeclasses.characters import Character
from evennia.contrib import gendersub


class TestCharacter(CommandTest):
    """
    Used to test the character object
    """
    def test_character(self):

        # test the character's gender and the abilit to run the @gender command
        char = create_object(Character, key="Gendered", location=self.room1)
        txt = "Test |p gender"
        self.assertEqual(
            gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test their gender"
        )
        char.execute_cmd("gender male")
        self.assertEqual(
            gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test his gender"
        )
        char.execute_cmd("gender female")
        self.assertEqual(
            gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test her gender"
        )
        char.execute_cmd("sex neutral")
        self.assertEqual(
            gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test its gender"
        )
