from evennia.commands.default.tests import CommandTest
from evennia import create_object
from typeclasses.characters import Character, ATTRIBUTE_SETTINGS
from evennia.contrib import gendersub


class TestCharacter(CommandTest):
    """
    Used to test the character object
    """
    def test_character(self):

        # test the character's gender and the abilit to run the @gender command
        char = create_object(Character, key="Gendered", location=self.room1)
        txt = "Test |p gender"
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test their gender")
        char.execute_cmd("gender male")
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test his gender")
        char.execute_cmd("gender female")
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test her gender")
        char.execute_cmd("sex neutral")
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test its gender")

        # hp is tested in the utils unit test

        # test stats
        # test strength
        self.assertEqual(char.STR, 100)
        self.assertEqual(char.STR.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.STR.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.STR.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.STR = 101
        self.assertEqual(char.attributes.get('strength_value'), 101)
        char.STR = 100
        self.assertEqual(char.attributes.get('strength_value'), 100)
        self.assertFalse(char.attributes.has('strength_max'))
        char.STR.max = 101
        self.assertEqual(char.attributes.get('strength_max'), 101)
        char.STR.max = 100
        self.assertEqual(char.attributes.get('strength_max'), 100)
        self.assertFalse(char.attributes.has('strength_min'))
        char.STR.min = 101
        self.assertEqual(char.attributes.get('strength_min'), 101)
        char.STR.min = 100
        self.assertEqual(char.attributes.get('strength_min'), 100)
        # test constitution
        self.assertEqual(char.CON, 100)
        self.assertEqual(char.CON.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.CON.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.CON.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.CON = 101
        self.assertEqual(char.attributes.get('constitution_value'), 101)
        char.CON = 100
        self.assertEqual(char.attributes.get('constitution_value'), 100)
        self.assertFalse(char.attributes.has('constitution_max'))
        char.CON.max = 101
        self.assertEqual(char.attributes.get('constitution_max'), 101)
        char.CON.max = 100
        self.assertEqual(char.attributes.get('constitution_max'), 100)
        self.assertFalse(char.attributes.has('constitution_min'))
        char.CON.min = 101
        self.assertEqual(char.attributes.get('constitution_min'), 101)
        char.CON.min = 100
        self.assertEqual(char.attributes.get('constitution_min'), 100)
        # test observation
        self.assertEqual(char.OBS, 100)
        self.assertEqual(char.OBS.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.OBS.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.OBS.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.OBS = 101
        self.assertEqual(char.attributes.get('observation_value'), 101)
        char.OBS = 100
        self.assertEqual(char.attributes.get('observation_value'), 100)
        self.assertFalse(char.attributes.has('observation_max'))
        char.OBS.max = 101
        self.assertEqual(char.attributes.get('observation_max'), 101)
        char.OBS.max = 100
        self.assertEqual(char.attributes.get('observation_max'), 100)
        self.assertFalse(char.attributes.has('observation_min'))
        char.OBS.min = 101
        self.assertEqual(char.attributes.get('observation_min'), 101)
        char.OBS.min = 100
        self.assertEqual(char.attributes.get('observation_min'), 100)
        # test agility
        self.assertEqual(char.AGI, 100)
        self.assertEqual(char.AGI.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.AGI.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.AGI.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.AGI = 101
        self.assertEqual(char.attributes.get('agility_value'), 101)
        char.AGI = 100
        self.assertEqual(char.attributes.get('agility_value'), 100)
        self.assertFalse(char.attributes.has('agility_max'))
        char.AGI.max = 101
        self.assertEqual(char.attributes.get('agility_max'), 101)
        char.AGI.max = 100
        self.assertEqual(char.attributes.get('agility_max'), 100)
        self.assertFalse(char.attributes.has('agility_min'))
        char.AGI.min = 101
        self.assertEqual(char.attributes.get('agility_min'), 101)
        char.AGI.min = 100
        self.assertEqual(char.attributes.get('agility_min'), 100)
        # test speed
        self.assertEqual(char.SPD, 100)
        self.assertEqual(char.SPD.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.SPD.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.SPD.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.SPD = 101
        self.assertEqual(char.attributes.get('speed_value'), 101)
        char.SPD = 100
        self.assertEqual(char.attributes.get('speed_value'), 100)
        self.assertFalse(char.attributes.has('speed_max'))
        char.SPD.max = 101
        self.assertEqual(char.attributes.get('speed_max'), 101)
        char.SPD.max = 100
        self.assertEqual(char.attributes.get('speed_max'), 100)
        self.assertFalse(char.attributes.has('speed_min'))
        char.SPD.min = 101
        self.assertEqual(char.attributes.get('speed_min'), 101)
        char.SPD.min = 100
        self.assertEqual(char.attributes.get('speed_min'), 100)
        # test intelligence
        self.assertEqual(char.INT, 100)
        self.assertEqual(char.INT.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.INT.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.INT.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.INT = 101
        self.assertEqual(char.attributes.get('intelligence_value'), 101)
        char.INT = 100
        self.assertEqual(char.attributes.get('intelligence_value'), 100)
        self.assertFalse(char.attributes.has('intelligence_max'))
        char.INT.max = 101
        self.assertEqual(char.attributes.get('intelligence_max'), 101)
        char.INT.max = 100
        self.assertEqual(char.attributes.get('intelligence_max'), 100)
        self.assertFalse(char.attributes.has('intelligence_min'))
        char.INT.min = 101
        self.assertEqual(char.attributes.get('intelligence_min'), 101)
        char.INT.min = 100
        self.assertEqual(char.attributes.get('intelligence_min'), 100)
        # test wisdom
        self.assertEqual(char.WIS, 100)
        self.assertEqual(char.WIS.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.WIS.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.WIS.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.WIS = 101
        self.assertEqual(char.attributes.get('wisdom_value'), 101)
        char.WIS = 100
        self.assertEqual(char.attributes.get('wisdom_value'), 100)
        self.assertFalse(char.attributes.has('wisdom_max'))
        char.WIS.max = 101
        self.assertEqual(char.attributes.get('wisdom_max'), 101)
        char.WIS.max = 100
        self.assertEqual(char.attributes.get('wisdom_max'), 100)
        self.assertFalse(char.attributes.has('wisdom_min'))
        char.WIS.min = 101
        self.assertEqual(char.attributes.get('wisdom_min'), 101)
        char.WIS.min = 100
        self.assertEqual(char.attributes.get('wisdom_min'), 100)
        # test renown
        self.assertEqual(char.REN, 100)
        self.assertEqual(char.REN.max, ATTRIBUTE_SETTINGS.get('max'))
        self.assertEqual(char.REN.min, ATTRIBUTE_SETTINGS.get('min'))
        self.assertEqual(char.REN.breakpoint, ATTRIBUTE_SETTINGS.get('breakpoint'))
        char.REN = 101
        self.assertEqual(char.attributes.get('renown_value'), 101)
        char.REN = 100
        self.assertEqual(char.attributes.get('renown_value'), 100)
        self.assertFalse(char.attributes.has('renown_max'))
        char.REN.max = 101
        self.assertEqual(char.attributes.get('renown_max'), 101)
        char.REN.max = 100
        self.assertEqual(char.attributes.get('renown_max'), 100)
        self.assertFalse(char.attributes.has('renown_min'))
        char.REN.min = 101
        self.assertEqual(char.attributes.get('renown_min'), 101)
        char.REN.min = 100
        self.assertEqual(char.attributes.get('renown_min'), 100)
