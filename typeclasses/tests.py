from evennia.commands.default.tests import CommandTest
from evennia import create_object
from typeclasses.characters import Character, CHARACTER_STAT_SETTINGS
from typeclasses.rooms import Room
from typeclasses.objects import Object
from evennia.contrib import gendersub
from evennia.utils.test_resources import EvenniaTest


class TestCharacter(CommandTest):
    """
    Used to test the character object
    stat modifiers unit tests are in world.rules.tests.TestRules.test_stat_modifiers
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
        self.assertEqual(char.STR.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.STR.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.STR.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.STR = 99
        self.assertEqual(char.attributes.get('strength_value'), 99)
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
        self.assertEqual(char.CON.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.CON.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.CON.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.CON = 99
        self.assertEqual(char.attributes.get('constitution_value'), 99)
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
        self.assertEqual(char.OBS.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.OBS.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.OBS.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.OBS = 99
        self.assertEqual(char.attributes.get('observation_value'), 99)
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
        self.assertEqual(char.AGI.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.AGI.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.AGI.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.AGI = 99
        self.assertEqual(char.attributes.get('agility_value'), 99)
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
        self.assertEqual(char.SPD.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.SPD.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.SPD.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.SPD = 99
        self.assertEqual(char.attributes.get('speed_value'), 99)
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
        self.assertEqual(char.INT.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.INT.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.INT.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.INT = 99
        self.assertEqual(char.attributes.get('intelligence_value'), 99)
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
        self.assertEqual(char.WIS.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.WIS.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.WIS.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.WIS = 99
        self.assertEqual(char.attributes.get('wisdom_value'), 99)
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
        # test charisma
        self.assertEqual(char.CHR, 100)
        self.assertEqual(char.CHR.max, CHARACTER_STAT_SETTINGS.get('max'))
        self.assertEqual(char.CHR.min, CHARACTER_STAT_SETTINGS.get('min'))
        self.assertEqual(char.CHR.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
        char.CHR = 99
        self.assertEqual(char.attributes.get('charisma_value'), 99)
        char.CHR = 100
        self.assertEqual(char.attributes.get('charisma_value'), 100)
        self.assertFalse(char.attributes.has('charisma_max'))
        char.CHR.max = 101
        self.assertEqual(char.attributes.get('charisma_max'), 101)
        char.CHR.max = 100
        self.assertEqual(char.attributes.get('charisma_max'), 100)
        self.assertFalse(char.attributes.has('charisma_min'))
        char.CHR.min = 101
        self.assertEqual(char.attributes.get('charisma_min'), 101)
        char.CHR.min = 100
        self.assertEqual(char.attributes.get('charisma_min'), 100)


# Testing of emoting / sdesc / recog system


from evennia.contrib import rpsystem

sdesc0 = "A nice sender of emotes"
sdesc1 = "The first receiver of emotes."
sdesc2 = "Another nice colliding sdesc-guy for tests"
recog01 = "Mr Receiver"
recog02 = "Mr Receiver2"
recog10 = "Mr Sender"
emote = 'With a flair, /me looks at /first and /colliding sdesc-guy. She says "This is a test."'


class TestRPSystem(EvenniaTest):
    maxDiff = None

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Location")
        self.speaker = create_object(Character, key="Sender", location=self.room)
        self.receiver1 = create_object(Character, key="Receiver1", location=self.room)
        self.receiver2 = create_object(Character, key="Receiver2", location=self.room)

    def test_ordered_permutation_regex(self):
        self.assertEqual(
            rpsystem.ordered_permutation_regex(sdesc0),
            "/[0-9]*-*A\\ nice\\ sender\\ of\\ emotes(?=\\W|$)+|"
            "/[0-9]*-*nice\\ sender\\ of\\ emotes(?=\\W|$)+|"
            "/[0-9]*-*A\\ nice\\ sender\\ of(?=\\W|$)+|"
            "/[0-9]*-*sender\\ of\\ emotes(?=\\W|$)+|"
            "/[0-9]*-*nice\\ sender\\ of(?=\\W|$)+|"
            "/[0-9]*-*A\\ nice\\ sender(?=\\W|$)+|"
            "/[0-9]*-*nice\\ sender(?=\\W|$)+|"
            "/[0-9]*-*of\\ emotes(?=\\W|$)+|"
            "/[0-9]*-*sender\\ of(?=\\W|$)+|"
            "/[0-9]*-*A\\ nice(?=\\W|$)+|"
            "/[0-9]*-*emotes(?=\\W|$)+|"
            "/[0-9]*-*sender(?=\\W|$)+|"
            "/[0-9]*-*nice(?=\\W|$)+|"
            "/[0-9]*-*of(?=\\W|$)+|"
            "/[0-9]*-*A(?=\\W|$)+",
        )

    def test_sdesc_handler(self):
        self.speaker.sdesc.add(sdesc0)
        self.assertEqual(self.speaker.sdesc.get(), sdesc0)
        self.speaker.sdesc.add("This is {#324} ignored")
        self.assertEqual(self.speaker.sdesc.get(), "This is 324 ignored")
        self.speaker.sdesc.add("Testing three words")
        self.assertEqual(
            self.speaker.sdesc.get_regex_tuple()[0].pattern,
            "/[0-9]*-*Testing\ three\ words(?=\W|$)+|"
            "/[0-9]*-*Testing\ three(?=\W|$)+|"
            "/[0-9]*-*three\ words(?=\W|$)+|"
            "/[0-9]*-*Testing(?=\W|$)+|"
            "/[0-9]*-*three(?=\W|$)+|"
            "/[0-9]*-*words(?=\W|$)+",
        )

    def test_recog_handler(self):
        self.speaker.sdesc.add(sdesc0)
        self.receiver1.sdesc.add(sdesc1)
        self.speaker.recog.add(self.receiver1, recog01)
        self.speaker.recog.add(self.receiver2, recog02)
        self.assertEqual(self.speaker.recog.get(self.receiver1), recog01)
        self.assertEqual(self.speaker.recog.get(self.receiver2), recog02)
        self.assertEqual(
            self.speaker.recog.get_regex_tuple(self.receiver1)[0].pattern,
            "/[0-9]*-*Mr\\ Receiver(?=\\W|$)+|/[0-9]*-*Receiver(?=\\W|$)+|/[0-9]*-*Mr(?=\\W|$)+",
        )
        self.speaker.recog.remove(self.receiver1)
        self.assertEqual(self.speaker.recog.get(self.receiver1), sdesc1)

        self.assertEqual(self.speaker.recog.all(), {"Mr Receiver2": self.receiver2})

    def test_parse_language(self):
        self.assertEqual(
            rpsystem.parse_language(self.speaker, emote),
            (
                "With a flair, /me looks at /first and /colliding sdesc-guy. She says {##0}",
                {"##0": (None, '"This is a test."')},
            ),
        )

    def parse_sdescs_and_recogs(self):
        speaker = self.speaker
        speaker.sdesc.add(sdesc0)
        self.receiver1.sdesc.add(sdesc1)
        self.receiver2.sdesc.add(sdesc2)
        candidates = (self.receiver1, self.receiver2)
        result = (
            'With a flair, {#9} looks at {#10} and {#11}. She says "This is a test."',
            {
                "#11": "Another nice colliding sdesc-guy for tests",
                "#10": "The first receiver of emotes.",
                "#9": "A nice sender of emotes",
            },
        )
        self.assertEqual(rpsystem.parse_sdescs_and_recogs(speaker, candidates, emote), result)
        self.speaker.recog.add(self.receiver1, recog01)
        self.assertEqual(rpsystem.parse_sdescs_and_recogs(speaker, candidates, emote), result)

    def test_send_emote(self):
        speaker = self.speaker
        receiver1 = self.receiver1
        receiver2 = self.receiver2
        receivers = [speaker, receiver1, receiver2]
        speaker.sdesc.add(sdesc0)
        receiver1.sdesc.add(sdesc1)
        receiver2.sdesc.add(sdesc2)
        speaker.msg = lambda text, **kwargs: setattr(self, "out0", text)
        receiver1.msg = lambda text, **kwargs: setattr(self, "out1", text)
        receiver2.msg = lambda text, **kwargs: setattr(self, "out2", text)
        rpsystem.send_emote(speaker, receivers, emote)
        self.assertEqual(
            self.out0,
            "With a flair, |bSender|n looks at |bThe first receiver of emotes.|n "
            'and |bAnother nice colliding sdesc-guy for tests|n. She says |w"This is a test."|n',
        )
        self.assertEqual(
            self.out1,
            "With a flair, |bA nice sender of emotes|n looks at |bReceiver1|n and "
            '|bAnother nice colliding sdesc-guy for tests|n. She says |w"This is a test."|n',
        )
        self.assertEqual(
            self.out2,
            "With a flair, |bA nice sender of emotes|n looks at |bThe first "
            'receiver of emotes.|n and |bReceiver2|n. She says |w"This is a test."|n',
        )

    def test_rpsearch(self):
        self.speaker.sdesc.add(sdesc0)
        self.receiver1.sdesc.add(sdesc1)
        self.receiver2.sdesc.add(sdesc2)
        self.speaker.msg = lambda text, **kwargs: setattr(self, "out0", text)
        self.assertEqual(self.speaker.search("receiver of emotes"), self.receiver1)
        self.assertEqual(self.speaker.search("colliding"), self.receiver2)


class TestRPSystemCommands(CommandTest):
    def setUp(self):
        super().setUp()
        self.char1.swap_typeclass(Character)
        self.char2.swap_typeclass(Character)

    def test_commands(self):

        self.call(
            rpsystem.CmdSdesc(), "Foobar Character", "Char's sdesc was set to 'Foobar Character'."
        )
        self.call(
            rpsystem.CmdSdesc(),
            "BarFoo Character",
            "Char2's sdesc was set to 'BarFoo Character'.",
            caller=self.char2,
        )
        self.call(rpsystem.CmdSay(), "Hello!", 'Char says, "Hello!"')
        self.call(rpsystem.CmdEmote(), "/me smiles to /barfoo.", "Char smiles to BarFoo Character")
        self.call(
            rpsystem.CmdPose(),
            "stands by the bar",
            "Pose will read 'Foobar Character stands by the bar.'.",
        )
        self.call(
            rpsystem.CmdRecog(),
            "barfoo as friend",
            "Char will now remember BarFoo Character as friend.",
        )
        self.call(
            rpsystem.CmdRecog(),
            "",
            "Currently recognized (use 'recog <sdesc> as <alias>' to add new "
            "and 'forget <alias>' to remove):\n friend  (BarFoo Character)",
        )
        self.call(
            rpsystem.CmdRecog(),
            "friend",
            "Char will now know them only as 'BarFoo Character'",
            cmdstring="forget",
        )
