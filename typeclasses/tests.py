from mock import patch, Mock
import datetime

from evennia.commands.default.tests import CommandTest
from evennia import create_object
from typeclasses.characters import Character, CHARACTER_STAT_SETTINGS
from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from evennia.contrib import gendersub
from evennia.utils.test_resources import EvenniaTest
from world.rules import body, damage, actions
from commands import developer_cmds
from typeclasses.equipment.wieldable import Weapon
from utils.unit_test_resources import UniqueMudCmdTest


class TestObjects(CommandTest):
    """
    Used to test the character object
    stat modifiers unit tests are in world.rules.tests.TestRules.test_stat_modifiers

    CommandTest.call arguments
        cmdobj, args, msg=None, cmdset=None,
        noansi=True, caller=None, receiver=None, cmdstring=None,
        obj=None, inputs=None, raw_string=None,
    Objects in EvenniaTest
        self.obj1 = obj
        self.obj2 = "obj2"
        self.char1 = "char"
        self.char2 = "char2"
        self.exit = "out"
        self.room1 = "Room"
    """
    # account_typeclass = DefaultAccount
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    # script_typeclass = DefaultScript
    def test_objects(self):

        # test the character's gender and the abilit to run the @gender command
        #char = create_object(Human, key="Gendered", location=self.room1)
        self.sword = create_object(Weapon, key="a sword")
        self.sword.targetable = True
        self.sword.location = self.char1.location
        char = self.char1

        txt = "Test |p gender"
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test their gender")
        char.execute_cmd("gender male")
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test his gender")
        char.execute_cmd("gender female")
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test her gender")
        char.execute_cmd("sex neutral")
        self.assertEqual(gendersub._RE_GENDER_PRONOUN.sub(char._get_pronoun, txt), "Test its gender")

        # test Character stats
        for stat in (char.END, char.WILL, char.CHR, char.WIS, char.INT, char.SPD, char.AGI,
                     char.OBS, char.CON, char.STR, char.PERM):
            self.assertEqual(stat, 100)
            self.assertEqual(stat.max, CHARACTER_STAT_SETTINGS.get('max'))
            self.assertEqual(stat.min, CHARACTER_STAT_SETTINGS.get('min'))
            self.assertEqual(stat.breakpoint, CHARACTER_STAT_SETTINGS.get('breakpoint'))
            # test changing stat
            stat.set(99)
            self.assertEqual(stat, 99)
            self.assertEqual(char.attributes.get(f'{stat.name}_value'), 99)
            # test changing stats max
            self.assertFalse(char.attributes.has(f'{stat.name}_max'))
            stat.max = 101
            self.assertEqual(char.attributes.get(f'{stat.name}_max'), 101)
            stat.max = 100
            self.assertEqual(char.attributes.get(f'{stat.name}_max'), 100)
            # test changing stats min
            self.assertFalse(char.attributes.has(f'{stat.name}_min'))
            stat.min = -99
            self.assertEqual(char.attributes.get(f'{stat.name}_min'), -99)
            stat.min = -100
            self.assertEqual(char.attributes.get(f'{stat.name}_min'), -100)
            # test stat restoration
            stat.set(99)
            char.restore_stat(stat)
            self.assertTrue(stat == 100)

        # test basic attributes shared among all object types
        for attr_type in ('container', 'targetable'):
            for obj in (self.obj1, self.char1, self.exit, self.room1):
                # verify default values are in database if they should be
                def_attr_val = getattr(obj, attr_type)
                self.assertEqual(getattr(obj, attr_type), def_attr_val)
                self.assertEqual(obj.attributes.get(attr_type, False), def_attr_val)
                # set the test value and make certain in is recorded to the database
                test_attr_val = False if def_attr_val else True
                setattr(obj, attr_type, test_attr_val)
                self.assertEqual(getattr(obj, attr_type, False), test_attr_val)
                self.assertEqual(obj.attributes.get(attr_type, False), test_attr_val)
                # set the attribute back to default
                setattr(obj, attr_type, def_attr_val)
                self.assertEqual(getattr(obj, attr_type), def_attr_val)
                self.assertEqual(obj.attributes.get(attr_type, False), def_attr_val)

        # test hp restoration
        self.assertFalse(char.condition.dead)
        char.hp = 50
        # make certain the Character heals by some ammount
        self.assertEqual(char.hp, 50)
        char.heal()
        self.assertTrue(char.hp > 50)
        # heal now by a set ammount
        char.hp = 50
        self.assertEqual(char.hp, 50)
        char.heal(ammount=5)
        self.assertEqual(char.hp, 55)
        # verify the natural healing script works
        char.hp = 50
        self.assertEqual(char.hp, 50)
        nat_heal_script = char.scripts.get('Natural_Healing')
        nat_heal_script[0].at_repeat()
        self.assertTrue(char.hp > 50)
        # verify healing will wake an unconcious Character
        self.assertFalse(char.condition.unconscious)
        char.condition.unconscious = True
        self.assertTrue(char.condition.unconscious)
        char.heal()
        self.assertFalse(char.condition.unconscious)
        # test hp breakpoints
        self.assertFalse(char.condition.unconscious)
        char.hp = -1
        self.assertTrue(char.condition.unconscious)
        char.hp = 100
        self.assertFalse(char.condition.unconscious)

        # test usdesc
        self.assertEqual(char.usdesc, 'A normal person')
        self.assertEqual(self.room1.usdesc, 'Room')
        self.assertEqual(self.obj1.usdesc, 'Obj')
        self.assertEqual(self.exit.usdesc, 'out')
        # test setting usdesc
        char.usdesc = 'not_' + char.usdesc
        self.room1.usdesc = 'not_' + self.room1.usdesc
        self.obj1.usdesc = 'not_' + self.obj1.usdesc
        self.exit.usdesc = 'not_' + self.exit.usdesc
        self.assertEqual(char.usdesc, 'not_A normal person')
        self.assertEqual(self.room1.usdesc, 'not_Room')
        self.assertEqual(self.obj1.usdesc, 'not_Obj')
        self.assertEqual(self.exit.usdesc, 'not_out')
        char.usdesc = 'A normal person'
        self.room1.usdesc = 'Room'
        self.obj1.usdesc = 'Obj'
        self.exit.usdesc = 'out'

        # Test damage reduction dr & world.rules.damage.DamageElement
        # Test directly setting a damage reduction attribute
        self.assertFalse(char.attributes.has('dr_acd'))
        char.dr.ACD = 1
        self.assertEqual(char.attributes.get('dr_acd'), 1)
        char.dr.ACD = 0
        # tests all damage types
        from world.rules.damage import TYPES
        for type in TYPES:
            db_key = 'dr_'+type.lower()
            self.assertFalse(char.attributes.has(db_key))
            setattr(char.dr, type, 1)
            self.assertEqual(char.attributes.get(db_key), 1)
            # make certain setting to 0 removes the attr from database
            setattr(char.dr, type, 0)
            self.assertFalse(char.attributes.has(db_key))
            setattr(char.dr, type, 1)  # set to test dr.delete
        # test deleting a dr element
        self.assertEqual(char.attributes.get('dr_acd'), 1)
        char.dr.delete()
        for type in TYPES:
            db_key = 'dr_'+type.lower()
            self.assertFalse(char.attributes.has(db_key))
        self.assertEqual(char.dr.ACD, 0)

        # Test body parts
        # hand occuipied state is in commands.tests, as the get command is the easiest method to test this
        from world.rules.body import PART_STATUS, HUMANOID_BODY
        self.assertEqual(char.body.head.broke, 0)
        for part in HUMANOID_BODY:
            part_inst = getattr(char.body, part)
            for status in PART_STATUS:
                part_status_inst = getattr(part_inst, status)
                self.assertEqual(part_status_inst, 0)
        self.assertFalse(char.attributes.has('head_bleeding'))
        char.body.head.bleeding = True
        self.assertEqual(char.attributes.get('head_bleeding'), True)
        char.body.head.bleeding = False
        self.assertFalse(char.attributes.has('head_bleeding'))

        # test Character, Object, Exit; .get_part()
        body_part = self.char1.get_body_part()
        self.assertTrue(body_part.name in self.char1.body.parts)
        obj_part = self.obj1.get_body_part()  # this object has no parts
        self.assertFalse(obj_part)

        # test Caracter.position
        char.position = "standing"
        self.assertEqual(char.attributes.get('position'), "standing")
        self.assertEqual(char.position, "standing")
        char.position = 'sitting'
        self.assertEqual(char.attributes.get('position'), "sitting")
        self.assertEqual(char.position, "sitting")
        char.position = 'laying'
        self.assertEqual(char.attributes.get('position'), "laying")
        self.assertEqual(char.position, "laying")

        # test Character.condition
        for cond_name in body.CHARACTER_CONDITIONS:
            db_cond_name = 'condition_'+cond_name
            self.assertFalse(char.attributes.has(db_cond_name))
            self.assertEqual(getattr(char.condition, cond_name), 0)
            setattr(char.condition, cond_name, True)
            self.assertTrue(char.attributes.has(db_cond_name))
            self.assertTrue(char.attributes.get(db_cond_name))
            setattr(char.condition, cond_name, False)
            self.assertFalse(char.attributes.has(db_cond_name))
            self.assertEqual(getattr(char.condition, cond_name), 0)

        # test Character skills
        from world.rules import skills
        for skill_set_name, skill_names in skills.SKILLS.items():
            skill_set_inst = getattr(char.skills, skill_set_name)
            for skill_name in skill_names:
                if skill_name == 'skill_points':
                    continue
                skill_inst = skill_set_inst[skill_name]
                # humanoids have 1 rank in punch, kick and dodge
                if skill_name in ('punch', 'kick', 'dodge'):
                    self.assertEqual(skill_inst, 1)
                else:
                    self.assertEqual(skill_inst, 0)
        # verify skills save to database
        char.skills.unarmed.punch = 0
        self.assertFalse(char.attributes.has('unarmed_punch'))
        char.skills.unarmed.punch = 3
        self.assertEqual(char.attributes.get('unarmed_punch'), 3)
        char.skills.unarmed.punch = 0
        self.assertFalse(char.attributes.has('unarmed_punch'))
        char.skills.unarmed.punch = 1

        # test Character.evd_max
        # test flat foot "no evasion command active"
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 51"
        cmd_result = self.call(command(), arg, caller=char)
        self.assertRegex(cmd_result, wanted_message)
        # test with an active evasion command
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
        cmd_result = self.call(command(), arg, caller=char)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 52"
        cmd_result = self.call(command(), arg, caller=char)
        self.assertRegex(cmd_result, wanted_message)
        # change the evade max for dodge and test again
        char.evd_max.AGI = 53
        # flat footed
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 53"
        cmd_result = self.call(command(), arg, caller=char)
        self.assertRegex(cmd_result, wanted_message)
        # with dodge active
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
        cmd_result = self.call(command(), arg, caller=char)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 54"
        cmd_result = self.call(command(), arg, caller=char)
        self.assertRegex(cmd_result, wanted_message)
        # set back to default
        char.evd_max.AGI = actions.EVADE_MAX
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 51"
        cmd_result = self.call(command(), arg, caller=char)
        self.assertRegex(cmd_result, wanted_message)

        # test weapon dmg_types ListElement
        self.assertFalse(self.sword.attributes.has('dmg_types_acd'))
        self.sword.dmg_types.ACD = 1
        self.assertEqual(self.sword.attributes.get('dmg_types_acd'), 1)
        self.sword.dmg_types.ACD = 0
        # tests all damage types
        for type in damage.TYPES:
            db_key = 'dmg_types_'+type.lower()
            self.assertFalse(self.sword.attributes.has(db_key))
            setattr(self.sword.dmg_types, type, 1)
            self.assertEqual(self.sword.attributes.get(db_key), 1)
            # make certain setting to 0 removes the attr from database
            setattr(self.sword.dmg_types, type, 0)
            self.assertFalse(self.sword.attributes.has(db_key))
            setattr(self.sword.dmg_types, type, 1)  # set to test dmg_types.delete
        # test deleting a dmg_types element
        self.assertEqual(self.sword.attributes.get('dmg_types_acd'), 1)
        self.sword.dmg_types.delete()
        for type in TYPES:
            db_key = 'dmg_types_'+type.lower()
            self.assertFalse(self.sword.attributes.has(db_key))
        self.assertEqual(self.sword.dmg_types.ACD, 0)
        # test wieldable item attributes
        for type in ('dmg_max', 'act_roll_max_mod', 'evd_roll_max_mod'):
            db_key = type.lower()
            if db_key == 'dmg_max':
                def_value = 4
            elif db_key in ('act_roll_max_mod', 'evd_roll_max_mod'):
                def_value = 0
            self.assertFalse(self.sword.attributes.has(db_key))
            setattr(self.sword, type, 1)
            self.assertEqual(self.sword.attributes.get(db_key), 1)
        # test wieldable.evd_stats
        self.assertFalse(self.sword.attributes.has('evd_stats'))
        self.sword.evd_stats = ('STR',)
        self.assertEqual(self.sword.attributes.get('evd_stats'), ('STR',))
        del self.sword.evd_stats
        self.assertFalse(self.sword.attributes.has('evd_stats'))

    def test_learning(self):
        self.assertFalse(self.char1.learning)
        self.char1.learning = True
        self.assertTrue(self.char1.learning)
        del self.char1.learning
        self.assertFalse(self.char1.learning)
        self.char1.learning = 1
        self.assertEqual(self.char1.learning, 1)


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
        # rpsystem say command support removed.
        # self.call(rpsystem.CmdSay(), "Hello!", 'Char says, "Hello!"')
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



# Testing clothing from UM
from typeclasses.equipment import clothing
from commands.standard_cmds import CmdDrop, CmdInventory


class TestClothingFunc(EvenniaTest):
    def test_clothingfunctions(self):
        wearer = create_object(Human, key="Wearer")
        room = create_object(Room, key="room")
        wearer.location = room
        # Make a test hat
        test_hat = create_object(clothing.UMClothing, key="test hat")
        test_hat.db.clothing_type = "hat"
        test_hat.location = wearer
        # Make a test shirt
        test_shirt = create_object(clothing.UMClothing, key="test shirt")
        test_shirt.db.clothing_type = "top"
        test_shirt.location = wearer
        # Make a test pants
        test_pants = create_object(clothing.UMClothing, key="test pants")
        test_pants.db.clothing_type = "bottom"
        test_pants.location = wearer

        #test_hat.wear(wearer, "on the head")
        #self.assertEqual(test_hat.db.worn, "on the head")

        test_hat.remove(wearer)
        self.assertEqual(test_hat.db.worn, False)

        test_hat.worn = True
        test_hat.at_get(wearer)
        self.assertEqual(test_hat.db.worn, False)

        clothes_list = [test_shirt, test_hat, test_pants]
        self.assertEqual(
            clothing.order_clothes_list(clothes_list), [test_hat, test_shirt, test_pants]
        )

        test_hat.wear(wearer, True)
        test_pants.wear(wearer, True)
        self.assertEqual(clothing.get_worn_clothes(wearer), [test_hat, test_pants])

        self.assertEqual(
            clothing.clothing_type_count(clothes_list), {"hat": 1, "top": 1, "bottom": 1}
        )

        self.assertEqual(clothing.single_type_count(clothes_list, "hat"), 1)


# Testing of ExtendedRoom contrib

from django.conf import settings
from commands.standard_cmds import CmdExtendedRoomDesc, CmdExtendedRoomDetail, CmdExtendedRoomGameTime


class ForceUTCDatetime(datetime.datetime):

    """Force UTC datetime."""

    @classmethod
    def fromtimestamp(cls, timestamp):
        """Force fromtimestamp to run with naive datetimes."""
        return datetime.datetime.utcfromtimestamp(timestamp)


@patch("evennia.contrib.extended_room.datetime.datetime", ForceUTCDatetime)
# mock gametime to return April 9, 2064, at 21:06 (spring evening)
@patch("evennia.utils.gametime.gametime", new=Mock(return_value=2975000766))
class TestExtendedRoom(CommandTest):
    """
    todo:
        command to test the changes to desc command
            test bad target message
        Test for <timeslot> usesage.
    """
    # account_typeclass = DefaultAccount
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    DETAIL_DESC = "A test detail."
    SPRING_DESC = "A spring description."
    OLD_DESC = "Old description."
    settings.TIME_ZONE = "UTC"

    def setUp(self):
        super().setUp()
        self.room1.ndb.last_timeslot = "afternoon"
        self.room1.ndb.last_season = "winter"
        self.room1.db.details = {"testdetail": self.DETAIL_DESC}
        self.room1.db.spring_desc = self.SPRING_DESC
        self.room1.db.desc = self.OLD_DESC

    def test_return_appearance(self):
        curr_season, curr_timeslot = self.room1.get_time_and_season()
        self.assertTrue("A spring description." in self.room1.return_appearance(self.char1))
        self.assertEqual("spring", self.room1.ndb.last_season)
        self.assertEqual("evening", self.room1.ndb.last_timeslot)

    def test_return_detail(self):
        self.assertEqual(self.DETAIL_DESC, self.room1.return_detail("testdetail"))

    #def test_cmdextendedlook(self):
    #    rid = self.room1.id
    #    self.call(
    #        extended_room.CmdExtendedRoomLook(),
    #        "here",
    #        "Room(#{})\n{}".format(rid, self.SPRING_DESC),
    #    )
    #    self.call(extended_room.CmdExtendedRoomLook(), "testdetail", self.DETAIL_DESC)
    #    self.call(
    #        extended_room.CmdExtendedRoomLook(), "nonexistent", "Could not find 'nonexistent'."
    #    )

    def test_cmd_detail(self):
        command = CmdExtendedRoomDetail
        self.call(command(), "", "Details on Room")
        self.call(
            command(),
            "thingie = newdetail with spaces",
            "Detail set 'thingie': 'newdetail with spaces'",
        )
        self.call(command(), "thingie", "Detail 'thingie' on Room:\n")
        self.call(
            command(),
            "/del thingie",
            "Detail thingie deleted, if it existed.",
            cmdstring="detail",
        )
        self.call(command(), "thingie", "Detail 'thingie' not found.")

        # Test with aliases
        self.call(command(), "", "Details on Room")
        self.call(
            command(),
            "thingie;other;stuff = newdetail with spaces",
            "Detail set 'thingie;other;stuff': 'newdetail with spaces'",
        )
        self.call(command(), "thingie", "Detail 'thingie' on Room:\n")
        self.call(command(), "other", "Detail 'other' on Room:\n")
        self.call(command(), "stuff", "Detail 'stuff' on Room:\n")
        self.call(
            command(),
            "/del other;stuff",
            "Detail other;stuff deleted, if it existed.",
        )
        self.call(command(), "other", "Detail 'other' not found.")
        self.call(command(), "stuff", "Detail 'stuff' not found.")

    def test_cmdgametime(self):

        command = CmdExtendedRoomGameTime

        self.call(command(), "", "It's a spring day, in the evening.")


from evennia.utils import eveditor

class TestCmdDesc(UniqueMudCmdTest):

    def tearDown(self):
        # make certain chaced variables are not retained.
        for character in (self.char1, self.char2):
            for attr_name in ('desc_editing_target', 'desc_editing_seasons'):
                self.assertFalse(character.attributes.has(attr_name))

    def test_args_edit(self):
        """Test chaging description via arguments only."""

        command = CmdExtendedRoomDesc

        for season in ('spring', 'summer', 'autumn', 'winter', 'general'):
            # make certain command runs without issue.
            args = f'/{season} here = This is a {season} description.'
            expected_desc = f'This is a {season} description.'
            wnt_msg = f'Room {season} description is now:\n{expected_desc}'
            self.call(command(), args, wnt_msg)
            # verify attribute is correct
            season_desc = self.room1.attributes.get(f'{season}_desc', False)
            self.assertEqual(expected_desc, season_desc)

    def test_multi_season_args_edit(self):
        """Test editing multiple seasons via arguments only."""

        # verification var
        description = 'This is a multi season description.'

        # test the command
        command = CmdExtendedRoomDesc
        args = f'/spring/winter here = {description}'
        wnt_msg = f'Room spring description is now:\n{description}|' \
                  f'Room winter description is now:\n{description}'
        self.call(command(), args, wnt_msg)

        # verify that the attribues have changed
        self.assertEqual(description, self.room1.attributes.get('spring_desc'))
        self.assertEqual(description, self.room1.attributes.get('winter_desc'))


    def test_args_with_no_rhs(self):
        """Test argument edit where no rhs is provided."""
        command = CmdExtendedRoomDesc
        args = 'here'
        wnt_msg = 'If the edit swtich is not used, an = than a description is required at the ' \
                  'end of the command.\nFor example: desc here = Is a small room.\n' \
                  'Would change the description of the current room to "Is a small room."\n' \
                  'Use help desc for a further details.'
        self.call(command(), args, wnt_msg)


    def test_no_args(self):
        """Test desc with no arguments."""
        command = CmdExtendedRoomDesc

        # make description changes
        args = f'/spring/winter here = This is a multi season description.'
        self.call(command(), args)

        # now test the output of desc with no arguments
        args = ''
        cmd_result = self.call(command(), args)
        wanted_message = 'spring: This is a multi season description'
        self.assertRegex(cmd_result, wanted_message)
        wanted_message = 'winter: This is a multi season description'
        self.assertRegex(cmd_result, wanted_message)

    def test_bad_target(self):
        """Test error handle for bad target."""
        command = CmdExtendedRoomDesc
        args = 'intentional fail = This is a description.'
        wnt_msg = 'You could not find intentional fail.'
        self.call(command(), args, wnt_msg)

    def test_access_control(self):
        """Verify access control functions."""

        command = CmdExtendedRoomDesc

        # make char 2 a builder, to grant access to desc
        self.char2.permissions.add("Builders")

        # test using arguments
        args = 'here = This is a description.'
        wnt_msg = "You don't have permission to edit the description of Room."
        self.call(command(), args, wnt_msg, caller=self.char2)

        # test again using the edit switch
        args = '/edit here'
        wnt_msg = "You don't have permission to edit the description of Room."
        self.call(command(), args, wnt_msg, caller=self.char2)

    def builders_only(self):
        """Only builders can acces desc command."""
        command = developer_cmds.CmdMultiCmd
        args = '= desc'
        wnt_msg = "Command 'desc' is not available."
        self.call(command(), args, wnt_msg, caller=self.char2)

    def test_general_overrides_desc(self):
        """Verify Room.general_desc overrides Room.desc."""

        command = CmdExtendedRoomDesc
        description = 'This is a room description.'

        # change the general description
        args = f'/general here = {description}'
        self.call(command(), args)

        # verify the general description is being used
        self.assertTrue(description in self.room1.return_appearance(self.char1))

    def test_evedit(self):
        """Test editing via the edit switch."""

        description = "This is a room description."

        # start the editor
        args = '/general/edit here'
        wanted_message = r'Editing Room.'
        cmd_result = self.call(CmdExtendedRoomDesc(), args, wanted_message)

        # verify editor messages
        wanted_message = 'seasons general'
        self.assertRegex(cmd_result, wanted_message)
        wanted_message = 'Line Editor \[desc\]'
        self.assertRegex(cmd_result, wanted_message)

        # change the description
        command = developer_cmds.CmdMultiCmd
        # change the general description
        wanted_message = '01This is a room description.'
        self.call(command(), f'= {description}', wanted_message)
        # write the changes
        cmd_result = self.call(command(), '=:wq')
        wanted_message = 'Saved.\nRoom general description is now:\nThis is a room description.\n' \
                         'Exited editor.'
        self.assertEqual(cmd_result, wanted_message)

        # verify the result
        self.assertTrue(description in self.room1.return_appearance(self.char1))
