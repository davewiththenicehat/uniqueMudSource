import time

from evennia import create_object
from evennia.utils import create

from typeclasses.objects import Object
from typeclasses.equipment import clothing
from commands import standard_cmds, developer_cmds
from utils.unit_test_resources import UniqueMudCmdTest
from utils.um_utils import replace_cap
from world.rules.stats import STATS, STAT_MAP_DICT
from world.rules.body import HUMANOID_BODY
from world.rules.actions import COST_LEVELS
from utils.element import Element

ANSI_RED = "\033[1m" + "\033[31m"
ANSI_NORMAL = "\033[0m"
ANSI_BLUE = "\033[1m" + "\033[34m"


class TestCommands(UniqueMudCmdTest):
    """
    CommandTest.call arguments
    call(cmdobj, args, msg=None, cmdset=None,
        noansi=True, caller=None, receiver=None, cmdstring=None,
        obj=None, inputs=None, raw_string=None,
    ):
    Objects in EvenniaTest
        self.obj1 = obj
        self.obj2 = "obj2"
        self.char1 = "char"
        self.char2 = "char2"
        self.exit = "out"
    """

    def test_inv(self):
        """
            Test inventory command
        """
        # test character with empty inventory
        command = developer_cmds.CmdMultiCmd
        arg = "= inv"
        receivers = {
            self.char1: "You are not carrying or wearing anything.",
            self.char2: ''
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers)
        wnt_msg = "^You are not carrying or wearing anything\.$"
        self.assertRegex(cmd_result, wnt_msg)

        # get an object
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early"
        wnt_msg = "You pick up obj\(#4\)\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj1))
        # Get the hat
        command = developer_cmds.CmdMultiCmd
        arg = "= get hat, complete_cmd_early"
        wnt_msg = "You pick up test hat"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # wear the test hat
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second\.|You begin to put on test hat.|You wear test hat\(#9\)\.|You are no longer busy\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain the hat is no longer in hand
        self.assertFalse(self.char1.is_holding(self.test_hat))

        # test inv with an object in hand and one worn
        command = developer_cmds.CmdMultiCmd
        arg = "= inv, complete_cmd_early"
        receivers = {
            self.char1: None,
            self.char2: 'Char begings to quickly look through theirs ' \
                        'possessions.|Char completes theirs search.'
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers)
        # make certain command takes time to complete
        wnt_msg = "^You will be busy for "
        self.assertRegex(cmd_result, wnt_msg)
        # make certain command start message echos
        wnt_msg = "You rummage through your possessions, taking inventory."
        self.assertRegex(cmd_result, wnt_msg)
        # check command carring and wearing items.
        wnt_msg = "You are carrying:\n Obj   \r\nYou are wearing:\n test hat"

        # Get a second item to wear
        command = developer_cmds.CmdMultiCmd
        arg = "= get shirt, complete_cmd_early"
        wnt_msg = "You pick up test shirt"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # wear the test shirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear shirt, complete_cmd_early"
        self.call(command(), arg)
        self.assertTrue(self.test_shirt.db.worn)
        # get a second object
        arg = "= get Obj2, complete_cmd_early"
        wnt_msg = "You pick up obj2\(#5\)\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))

        # test inv with two objects in hand and multiple items in hand
        command = developer_cmds.CmdMultiCmd
        arg = "= inv, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1)
        # make certain command takes time to complete
        wnt_msg = "^You will be busy for "
        self.assertRegex(cmd_result, wnt_msg)
        # make certain command start message echos
        wnt_msg = "You rummage through your possessions, taking inventory."
        self.assertRegex(cmd_result, wnt_msg)
        # check command carring and wearing items.
        wnt_msg = "You are carrying:\n Obj    \n Obj2   \r\nYou are wearing:\n test hat     \n test shirt"
        self.assertRegex(cmd_result, wnt_msg)

    def test_cmd_struct(self):
        """
            test the Command defer system and Character Status
        """
    # test deffering a command
        # defer a command and complete it
        # tests self.defer_teme, by recording secods of defferal.
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, complete_cmd_early"
        wnt_msg = "You will be busy for 5 seconds.|Char is testing deferring a command.|Defered command ran successfully.|You are no longer busy."
        self.call(command(), arg, wnt_msg)
        # request a deffered command to stop
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd, y"
        wnt_msg = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wnt_msg)
        # you can not fullow up a busy command with another busy command
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, defer_cmd"
        wnt_msg = "You will be busy for 5 seconds.|Char is testing deferring a command.|You will be busy for 5 seconds."
        self.call(command(), arg, wnt_msg)
        # force a deffered command to stop, a deffered command was left open on 'char' from the test above
        # self.stop_forced
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_cmd/test_cmd"
        wnt_msg = "You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wnt_msg)
        # request the stop of a deffered command on self when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd"
        wnt_msg = "You may want to test_cmd.|You are not commited to an action."
        self.call(command(), arg, wnt_msg)
        # complete a command early when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= complete_cmd_early"
        wnt_msg = "You are not commited to an action."
        self.call(command(), arg, wnt_msg)
        # request the stop of a deffered command on a target that has no deffered command
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd Char2, l"
        wnt_msg = "Char2 is not commited to an action."
        self.call(command(), arg, wnt_msg)
        # request target to stop a deffered comamnd
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd, y"
        wnt_msg = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wnt_msg)
        # force a target other than self to stop a command
        # self.stop_forced
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char"
        wnt_msg = "You will be busy for 3 seconds."
        self.call(command(), arg, wnt_msg, caller=self.char2)
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_cmd Char2"
        wnt_msg = "You are no longer busy.|Char stopped your punch command with their stop_cmd."
        self.call(command(), arg, wnt_msg, receiver=self.char2)
    # test stun
        # stun a character and stop it early
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, stop_stun"
        wnt_msg = "You will be stunned for 3 seconds.|You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wnt_msg)
        # stun locks out busy commands
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, defer_cmd"
        wnt_msg = "You will be stunned for 3 seconds.|You will be stunned for 3 seconds."
        self.call(command(), arg, wnt_msg)
        # stop a stun on self when there is no stun
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_stun"
        wnt_msg = "You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wnt_msg)  # stop the stun above
        wnt_msg = "You are not currently stunned."
        self.call(command(), arg, wnt_msg)
    # test unconscious
        # test actions against an unconscious characer
        # the evade roll should be 5.
        self.char1.set_unconscious()
        self.assertFalse(self.char1.ready())
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other Char2=punch Char, complete_cmd_early Char2"
        wnt_msg = r"\nevade 5 VS punch"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdMultiCmd
        arg = "= out"
        wnt_msg = r"You can not do that while unconscious."
        cmd_result = self.call(command(), arg, wnt_msg,  caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        # make certain Character's pose shows unconscious
        arg = "= l"
        wnt_msg = r"Char is unconscious here"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # wake the character up
        self.char1.set_unconscious(False)
        # make certain Character is in laying position after waking up.
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wnt_msg = r"Char is laying here"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # stand self.char1 up
        wnt_msg = "You will be busy for 3 seconds.|You move to stand up.|You stand up."
        self.call(command(), '= stand, complete_cmd_early', wnt_msg)
    # test self.requires_ready
        # commands that should work when the user is busy
        # defer a command and complete it
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd"
        wnt_msg = "You will be busy for 5 seconds.|Char is testing deferring a command."
        self.call(command(), arg, wnt_msg)
        # commands that should work when the Character is busy
        command = developer_cmds.CmdMultiCmd
        not_req_ready_commands = ('look', 'drop', 'help', 'stat', 'say')
        for non_ready_cmd in not_req_ready_commands:
            arg = f"= {non_ready_cmd}"
            cmd_result = self.call(command(), arg, caller=self.char1)
            self.assertFalse(cmd_result.startswith('You will be busy for'))
        # commands that should not work when the Character is busy
        command = developer_cmds.CmdMultiCmd
        req_ready_commands = ('punch', 'inv', 'out', 'sit', 'lay',
                              'get', 'wear', 'remove', 'whisper', 'kick',
                              'dodge', 'put', 'stab', 'kick', 'wield',
                              'unwield', 'emote')
        for ready_cmd in req_ready_commands:
            arg = f"= {ready_cmd}"
            cmd_result = self.call(command(), arg, caller=self.char1)
            self.assertRegex(cmd_result, '^You will be busy for')
        # test stands ready state
        self.char1.position = 'laying'
        self.call(command(), '= stand', 'You will be busy for')
        self.char1.position = 'standing'
        # comlete self.char1's deffered command
        command = developer_cmds.CmdMultiCmd
        arg = "= complete_cmd_early"
        wnt_msg = "Defered command ran successfully.|You are no longer busy."
        self.call(command(), arg, wnt_msg)
    # test Character.condition.unconscious
        self.char1.set_unconscious()
        # test character posing.
        self.assertEqual(self.char1.db.pose, 'is unconscious here.')
        self.assertFalse(self.char1.ready())
        # Test commands a character should not be able to do while unconscious.
        command = developer_cmds.CmdMultiCmd
        unconscious_commands = ('punch char2', 'punch not here',
                                'out', 'inv', 'sit', 'stand', 'lay', 'get',
                                'wear', 'remove', 'say', 'drop', 'look', 'stab',
                                'wield', 'whisper', 'dodge', 'unwield', 'recog',
                                'emote', 'put')
        for uncon_cmd in unconscious_commands:
            arg = f"= {uncon_cmd}"
            wnt_msg = r"You can not do that while unconscious."
            cmd_result = self.call(command(), arg, wnt_msg)
            self.assertEqual(wnt_msg, cmd_result)
        # test commands that should work while character is unconscious
        cmds_work_while_uncon = ('stat', 'help')
        for uncon_cmd in cmds_work_while_uncon:
            arg = f"= {uncon_cmd}"
            unwnt_msg = r"You can not do that while unconscious."
            cmd_result = self.call(command(), arg)
            self.assertFalse(unwnt_msg == cmd_result)
        # wake char back up
        self.char1.set_unconscious(False)
        self.assertTrue(self.char1.ready())
        self.assertEqual(self.char1.db.pose, 'is laying here.')

    def test_targeting(self):
        """
            Test Command target system.
            Additional targeting tests in self.test_get_put_drop()
        """
        # test Command.can_not_target_self
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char"
        wnt_msg = 'You can not punch yourself.'
        cmd_result = self.call(command(), arg, wnt_msg)
        # test targeting an exit that is not targetable
        command = developer_cmds.CmdMultiCmd
        arg = "= punch out"
        wnt_msg = 'You can not punch out(#3).'
        cmd_result = self.call(command(), arg, wnt_msg)
        # test targeting a targetable exit
        self.exit.targetable = True
        command = developer_cmds.CmdMultiCmd
        arg = "= punch out, complete_cmd_early"
        wnt_msg = "You will be busy for 3 seconds.|Facing out(#3) you pull your hand back preparing an attack.|punch"
        cmd_result = self.call(command(), arg, wnt_msg)

        self.exit.targetable = False
        # test attacking a basic Object, defense should be 5
        # test a targeted command that has a stop_request against an object
        # to make certain the stop request to an object causes no issues
        command = developer_cmds.CmdMultiCmd
        arg = "= kick Obj, complete_cmd_early"
        wnt_msg = "evade 5:"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test a target leaving melee range
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char2, control_other Char2=out, complete_cmd_early"
        wnt_msg = "Char2\(#7\) is not in range\.\nYou are no longer busy\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # get Char2 back into the room.
        self.char2.location = self.room1
        self.assertEqual(self.char2.location, self.room1)
        # test self.target_required
        command = developer_cmds.CmdMultiCmd
        arg = "= get not_real_name"
        wnt_msg = "You can not find not_real_name."
        self.call(command(), arg, wnt_msg)
        # test self.target_in_hand. Offers a suggestion to get the target.
        arg = "= drop Obj"
        wnt_msg = "Try picking it up first with get Obj."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test self.search_caller_only
        command = developer_cmds.CmdMultiCmd
        arg = "= wear Obj"
        wnt_msg = "Try picking it up first with get Obj."
        self.call(command(), arg, wnt_msg)
        # make certain commands can have a numbered target
        test_object1 = create_object(Object, key="object one")
        test_object1.location = self.char1.location
        test_object2 = create_object(Object, key="object two")
        test_object2.location = self.char1.location
        command = developer_cmds.CmdMultiCmd
        arg = "= punch object"
        wnt_msg = "You can not punch object one"
        self.call(command(), arg, wnt_msg)
        arg = "= punch 2 object"
        wnt_msg = "You can not punch object two"
        self.call(command(), arg, wnt_msg)
        # test numbered targets and say to commad
        test_object1.targetable = True
        test_object2.targetable = True
        command = standard_cmds.CmdSay
        arg = 'to 2 object "test message'
        wnt_msg = r'You say to object two(#13), "test message".'
        cmd_result = self.call(command(), arg, wnt_msg)
        # make certain saying to the first object works after saying to the second
        # this makes certain the Command.target is not a global variable
        arg = 'to object "test message'
        wnt_msg = r'You say to object one(#12), "test message".'
        cmd_result = self.call(command(), arg, wnt_msg)
        # add unit test for drop after get has been updated to use UM targetting system.
        # test for multiple targets using &
        command = standard_cmds.CmdSay
        arg = 'to object & 2 object "test message'
        wnt_msg = r'You say to object one(#12) and object two(#13), "test message".'
        cmd_result = self.call(command(), arg, wnt_msg)
        # test for multiple targets using " and "
        command = standard_cmds.CmdSay
        arg = 'to object and 2 object "test message'
        wnt_msg = r'You say to object one(#12) and object two(#13), "test message".'
        cmd_result = self.call(command(), arg, wnt_msg)

    def test_get_put_drop(self):
        """
        test caller specified target location searching
           example put obj in container, container is the caller
           specified location
        test get command
        test put command
        test drop command
        """
        command = developer_cmds.CmdMultiCmd
        # get an object
        arg = "= get Obj, complete_cmd_early"
        wnt_msg = "You pick up obj\(#4\)\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj1))
        # test getting an object already in possession
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj"
        wnt_msg = "You are already carrying obj(#4)."
        cmd_result = self.call(command(), arg, wnt_msg)
        # get a second object
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj2, complete_cmd_early"
        wnt_msg = "You pick up Obj2\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        # put object 2 in object 1
        # this does NOT test self.sl_split
        self.obj1.container = True
        arg = "= put Obj2 in Obj, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1)
        wnt_msg = "You put obj2\(#5\) into obj\(#4\)\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You begin to put obj2\(#5\) into obj\(#4\)\."
        self.assertRegex(cmd_result, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj2))
        self.assertEqual(self.obj2.location, self.obj1)
        self.obj1.container = False
        # make certrain caller specified locations works with multi target cmds
        # tests self.sl_split
        arg = '= say to Char2 and Obj2 in Obj "Hello'
        wnt_msg = 'You say to Char2 and Obj2, "Hello"'
        self.call(command(), arg, caller=self.char1)
        # now get object 2 from object 1
        # tests self.sl_split
        arg = "= get Obj2 from Obj, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1)
        wnt_msg = r"You reach into obj"
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You get obj2\(#5\) from Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # test putting an object into a non container object.
        # this does NOT use self.sl_split
        arg = "= put Obj2 in Obj"
        wnt_msg = '^Obj\(#4\) is not a container\.$'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # test CmdPut the error catching in deffered action
        self.obj1.container = True
        arg = "= put Obj2 in Obj"
        wnt_msg = "You begin to put obj2\(#5\) into obj\(#4\)\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        self.obj1.container = False
        arg = "= complete_cmd_early"
        wnt_msg = "Obj(#4) is not a container.|You are no longer busy."
        cmd_result = self.call(command(), arg, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # drop the first object
        arg = "= drop Obj"
        wnt_msg = "You drop obj(#4)."
        cmd_result = self.call(command(), arg, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj1))
        # try putting obj2 into a container that does not exist
        arg = "= put Obj2 in fake container"
        wnt_msg = "^You did not find fake container among your possesions or near by\.$"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # test help message for put when no container is supplied.
        arg = "= put Obj2"
        wnt_msg = 'You must specify a container to place obj2(#5) into.\nFor a full help use: Help put'
        cmd_result = self.call(command(), arg, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # put obj2 in obj1 while obj1 is on the ground
        self.obj1.container = True
        arg = "= put Obj2 in Obj, complete_cmd_early"
        wnt_msg = "You put obj2\(#5\) into obj\(#4\)\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj2))
        self.obj1.container = False
        # get obj2 from obj1 while obj1 is on the ground
        # tests self.sl_split
        arg = "= get Obj2 from Obj, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1)
        wnt_msg = r"You reach into obj\(#4\)\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You get obj2\(#5\) from Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # drop the second object
        arg = "= drop Obj2"
        wnt_msg = "You drop obj2(#5)."
        cmd_result = self.call(command(), arg, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj2))
    # make certain room message is correct
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early"
        wnt_msg = "Char picks up obj\."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # get second object
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj2, complete_cmd_early"
        wnt_msg = "Char picks up obj2\."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # put object 2 in object 1
        self.obj1.container = True
        arg = "= put Obj2 in Obj, complete_cmd_early"
        wnt_msg = "Char begins to put obj2 into Obj.|Char puts obj2 into Obj."
        cmd_result = self.call(command(), arg, wnt_msg, receiver=self.char2)
        self.obj1.container = False
        # get object 2 from object 1
        arg = "= get Obj2 from Obj, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        wnt_msg = "Char gets obj2 from Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = "Char reaches into obj\."
        self.assertRegex(cmd_result, wnt_msg)
        # test getting a third object when hands are full
        self.obj3 = create_object(Object, key="Obj3")
        self.obj3.targetable = True
        self.obj3.location = self.char1.location
        self.assertRegex(cmd_result, wnt_msg)
        arg = "= get Obj3"
        wnt_msg = "^Your hands are full\.$"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # drop object 1
        arg = "= drop Obj, complete_cmd_early"
        wnt_msg = "Char drops obj."
        cmd_result = self.call(command(), arg, wnt_msg, receiver=self.char2)
        # drop object 2
        arg = "= drop Obj2, complete_cmd_early"
        wnt_msg = "Char drops obj2."
        cmd_result = self.call(command(), arg, wnt_msg, receiver=self.char2)
    # test get command failures
        # get an object from a location that does not exist
        # test self.target_required when self.sl_split found
        arg = "= get Obj from fake location"
        wnt_msg = "You could not find fake location to search for Obj."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test getting fake object from a location that exists.
        # test target_required when sl_split found
        arg = "= get fake item from Obj"
        wnt_msg = "You could not find fake item in Obj(#4)."
        self.call(command(), arg, wnt_msg)
        # test getting an object that does not exist
        # test target_required
        arg = "= get fake item"
        wnt_msg = "You can not find fake item."
        self.call(command(), arg, wnt_msg, caller=self.char1)
    # test drop command failures
        # drop an object already on the ground
        arg = "= drop Obj"
        wnt_msg = "Try picking it up first with get Obj."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # drop an object that does not exist
        # test target_required search_caller_only
        arg = "= drop fake item"
        wnt_msg = "fake item is not among your possesions."
        self.call(command(), arg, wnt_msg, caller=self.char1)

    def test_requirements(self):
        """
        Test command requiring
            skills
            wielded item
        Status requirments tested in test_cmd_struct
        """
        # test Command.can_not_target_self
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char"
        wnt_msg = 'You can not punch yourself.'
        cmd_result = self.call(command(), arg, wnt_msg)
        # test Command.target_inherits_from
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early, wear Obj, drop Obj"
        wnt_msg = "You can only wear clothing and armor\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test Command.target_in_hand
        self.test_shirt.location = self.char1
        command = developer_cmds.CmdMultiCmd
        arg = "= wear shirt"
        wnt_msg = "You have to hold an object you want to wear.\r\nTry getting it with get test shirt(#10)."
        cmd_result = self.call(command(), arg, wnt_msg)
        self.test_shirt.location = self.room1
        # test using one_handed skillset
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wnt_msg = "You pick up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        arg = "= wield sword"
        wnt_msg = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test command.require_ranks
        # humanoids should have 1 rank in dodge, test this with command.skill_ranks
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r skill_ranks, self, cmd_type:evasion, skill_name:dodge = False"
        wnt_msg = r"skill_ranks returned: 1"
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test that commands required_ranks will stop the command.
        command = developer_cmds.CmdMultiCmd
        arg = "= stab char2, complete_cmd_early"
        wnt_msg = 'You must have 1 or more ranks in stab to stab.'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test the stab command
        self.char1.skills.one_handed.stab = 1
        command = developer_cmds.CmdMultiCmd
        arg = "= stab char2, complete_cmd_early"
        wnt_msg = "You will be busy for 3 seconds.|Facing char2(#7) you raise a sword preparing an attack.|stab"
        cmd_result = self.call(command(), arg, wnt_msg)
        arg = "= drop sword"
        wnt_msg = "You drop a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test self.requires_wielding
        command = developer_cmds.CmdMultiCmd
        self.call(command(), '= stab char2', 'You must be wielding a one handed')
        self.char1.skills.one_handed.stab = 0

    def test_wear_remove(self):
        """
            test commands wear and remove.
            Makes certain their misk affects are applied.
            Wearing an article of clothing
                removes it from hand
                provides dr if item allows
            removing item reverses these changes
        """
        # Create additional clothing to test with
        self.test_helmet.location = self.room1
        # give the helmet an armor rating
        self.test_helmet.dr.PRC = 2
        self.test_helmet.dr.ACD = 3
        self.assertEqual(self.test_helmet.attributes.get('dr_PRC'), 2)
        self.assertEqual(self.test_helmet.dr.PRC, 2)
        # Make a second helmet
        self.test_helmet2 = create_object(clothing.HumanoidArmor, key="second helmet")
        self.test_helmet2.db.clothing_type = "head"
        self.test_helmet2.location = self.room1
        # make an undershirt
        test_undershirt = create_object(clothing.Clothing, key="test undershirt")
        test_undershirt.db.clothing_type = "undershirt"
        test_undershirt.location = self.room1

        # Test wearing an item, test removing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= get hat, complete_cmd_early"
        wnt_msg = "You pick up test hat"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.|You begin to put on test hat(#9).|You wear test hat(#9).|You are no longer busy."
        self.call(command(), arg, wnt_msg)
        # make certain the hat is no longer in hand
        self.assertFalse(self.char1.is_holding(self.test_hat))
        # make certain the hat is worn
        self.assertTrue(self.test_hat.db.worn)
        # test tring to wear an item that is not clothing, also tests target_inherits_from
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early"
        wnt_msg = "You pick up obj\(#4\)\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain hands are occupied with the object picked up
        self.assertTrue(self.char1.is_holding(self.obj1))
        arg = "= wear Obj"
        wnt_msg = "You can only wear clothing and armor."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        arg = "= drop Obj"
        wnt_msg = "You drop obj(#4)."
        cmd_result = self.call(command(), arg,  wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj1))
        # test removing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= remove hat, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.|You begin to remove test hat(#9).|You remove test hat(#9).|You are no longer busy."
        self.call(command(), arg, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.test_hat))
        # Put the hat back on to test covering
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wnt_msg = 'You will be busy for 1 second.|You begin to put on test hat(#9).|You wear test hat(#9).|You are no longer busy.'
        self.call(command(), arg, wnt_msg)
        # Test wearing a peace of armor
        command = developer_cmds.CmdMultiCmd
        arg = "= get helmet, complete_cmd_early, wear helmet, complete_cmd_early"
        wnt_msg = "You begin to put on test helmet\(#11\)\.\nYou wear test helmet\(#11\), covering test hat\.\nYou are no longer busy\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain the helmet is worn
        self.assertTrue(self.test_helmet.db.worn)
        # make certain clothing attributes are working with commands.
        self.assertEqual(self.test_hat.db.worn, True)
        self.assertEqual(self.test_hat.db.clothing_type, 'hat')
        self.assertEqual(self.test_helmet.db.clothing_type, "head")
        self.assertTrue('head' in self.test_helmet.type_limit)
        # Make certain return_appearance is working
        self.assertEqual(self.char1.return_appearance(self.char1), "You are wearing test helmet.")
        # Test now with the look command
        command = developer_cmds.CmdMultiCmd
        arg = "= l me"
        wnt_msg = "You are wearing test helmet."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test clothing covering.
        # Test wearing the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= get undershirt, complete_cmd_early, wear undershirt, complete_cmd_early"
        wnt_msg = "You begin to put on test undershirt\(#13\)\.\nYou wear test undershirt\(#13\)\.\nYou are no longer busy\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # get the test shirt
        command = developer_cmds.CmdMultiCmd
        arg = "= get shirt, complete_cmd_early"
        wnt_msg = "You pick up test shirt."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # Test wearing the shirt covering the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear shirt, complete_cmd_early"
        receivers = {
            self.char1: "You will be busy for 1 second.|You begin to put on test shirt(#10).|You wear test shirt(#10), covering test undershirt.|You are no longer busy.",
            self.char2: "Char begins to put on test shirt.|Char wears test shirt, covering test undershirt."
        }
        self.call_multi_receivers(command(), arg, receivers)
        self.assertEqual(test_undershirt.db.covered_by, self.test_shirt)
        #verify that the helmet's armor rating has been cached in the wearer
        self.assertEqual(self.char1.body.head.dr.PRC, 2)
        self.assertEqual(self.char1.body.head.dr.ACD, 3)
        self.assertEqual(self.char1.body.head.dr.BLG, 0)
        # test reveailing articles on removing a covering article
        command = developer_cmds.CmdMultiCmd
        arg = "= remove shirt, complete_cmd_early"
        receivers = {
            self.char1: "You will be busy for 1 second.|You begin to remove test shirt(#10).|You remove test shirt(#10), revealing test undershirt.|You are no longer busy.",
            self.char2: "Char begins to remove test shirt.|Char removes test shirt, revealing test undershirt."
        }
        self.call_multi_receivers(command(), arg, receivers)
        self.assertFalse(test_undershirt.db.covered_by)
        self.assertTrue(self.char1.is_holding(self.test_shirt))

        # test wear command errors
        # Test wear with no arguments.
        command = developer_cmds.CmdMultiCmd
        arg = "= wear"
        wnt_msg = "What would you like to wear?|If you need help try help wear."
        self.call(command(), arg,  wnt_msg)
        # test dropping a worn item
        arg = "= drop undershirt"
        wnt_msg = 'You must remove test undershirt(#13) to drop it.\nTry command remove test undershirt(#13) to remove it.'
        self.call(command(), arg, wnt_msg)
        # test wearing a peace of clothing when the slot is occupied
        command = developer_cmds.CmdMultiCmd
        arg = "= get second helmet, complete_cmd_early, wear second helmet"
        wnt_msg = "You are wearing test helmet\(#11\) on your head\. You will need to remove it first, try remove test helmet\(#11\)\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test wearing an article already worn.
        command = developer_cmds.CmdMultiCmd
        arg = "= wear test helmet"
        wnt_msg = "You are already wearing test helmet(#11)."
        cmd_result = self.call(command(), arg, wnt_msg)
        # test wearing an article that the caller has no body part for
        self.test_helmet2.db.clothing_type = "intentional_fail"
        command = developer_cmds.CmdMultiCmd
        arg = "= wear second helmet, drop second helmet"
        wnt_msg = "You do not have a intentional_fail to equip second helmet(#12) to."
        cmd_result = self.call(command(), arg, wnt_msg)
        self.test_helmet2.db.clothing_type = "head"
        # test wearing an item on person, not in hand and not worn
        # this should not trigger
        command = developer_cmds.CmdMultiCmd
        arg = "= drop shirt"
        self.call(command(), arg)
        self.assertEqual(self.test_shirt.location, self.room1)
        self.test_shirt.location = self.char1
        arg = "= wear shirt"
        wnt_msg = "You have to hold an object you want to wear\.\r\nTry getting it with get test shirt\(#10\)\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.test_shirt.location = self.room1

        # test remove command errors
        command = developer_cmds.CmdMultiCmd
        arg = "= remove"
        wnt_msg = "What would you like to remove?|If you need help try help remove."
        self.call(command(), arg, wnt_msg)
        # remove can not target self
        command = developer_cmds.CmdMultiCmd
        arg = "= remove self"
        wnt_msg = "You can not remove yourself."
        self.call(command(), arg, wnt_msg)
        # a Character can not wear an item that is not clothing
        # test tring to wear an item that is not clothing, also tests target_inherits_from
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early, remove Obj, drop Obj"
        wnt_msg = "You can only remove clothing and armor\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertEqual(self.obj1.location, self.room1)
        # try to remove clothing that is not worn.
        command = developer_cmds.CmdMultiCmd
        arg = "= get second helmet, complete_cmd_early, remove second helmet, drop second helmet"
        wnt_msg = "You are not wearing second helmet."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test search caller only
        command = developer_cmds.CmdMultiCmd
        arg = "= remove Obj"
        wnt_msg = "Try picking it up first with get Obj."
        self.call(command(), arg, wnt_msg)
        # test removing an object covered by another
        command = developer_cmds.CmdMultiCmd
        arg = "= remove hat"
        wnt_msg = "You are wearing test helmet(#11) over test hat(#9). Try removing test helmet(#11) first with remove test helmet(#11)."
        self.call(command(), arg, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.test_hat))

        # remove helmet and hat for the next tests
        command = developer_cmds.CmdMultiCmd
        arg = "= remove helmet, complete_cmd_early, drop helmet, remove hat, complete_cmd_early, drop hat, remove test shirt, complete_cmd_early, drop test shirt, remove test undershirt, complete_cmd_early, drop test undershirt"
        self.call(command(), arg)
        self.assertEqual(self.test_helmet.location, self.room1)
        self.assertEqual(self.test_hat.location, self.room1)
        self.assertEqual(test_undershirt.location, self.room1)
        self.assertEqual(self.test_shirt.location, self.room1)

        # test wearing articles of clothing. NOT armor, armor is below
        worn_list = list()
        for type in clothing.CLOTHING_TYPE_ORDER:
            setattr(self, type, create_object(clothing.HumanoidArmor, key=type))
            item_inst = getattr(self, type, False)
            if not item_inst:
                err_msg = "commands.tests.TestCommands.test_wear_remove " \
                          "wear remove test for all clothing types failed to " \
                          f"find {type} in unit test."
                raise AssertionError(err_msg)
            # make certain Character does not have a body part of clothing type
            try:
                self.assertFalse(hasattr(self.char1.body, type))
            except AssertionError:
                err_msg = "commands.tests.TestCommands.test_wear_remove " \
                          f"self.char1.body.{type} exists."
                raise AssertionError(err_msg)
            # set part attributes
            item_inst.db.clothing_type = type
            item_inst.location = self.char1
            open_hands = self.char1.open_hands()
            open_hands[0].occupied = item_inst.dbref
            item_inst.usdesc = f"{type} item"
            worn_list.append(item_inst)
            # make the message that should be seen
            if type == "fullbody":
                covering = ", covering undershirt item"
            elif type == "shoes":
                covering = ", covering socks item"
            else:
                covering = ""
            char1_msg = f"You will be busy for 1 second.|You begin to put on {item_inst.usdesc}({item_inst.dbref}).|You wear {item_inst.usdesc}({item_inst.dbref}){covering}.|You are no longer busy."
            char2_msg = f"Char begins to put on {item_inst.usdesc}.|Char wears {item_inst.usdesc}{covering}."
            # test wearing
            wear_rc = {self.char1: char1_msg,
                       self.char2: char2_msg}
            wear_cmd = {
                        'arg': f"= wear {type} item, complete_cmd_early",
                        'receivers': wear_rc,
                       }
            # run the tests
            self.loop_tests((wear_cmd,))
        # verify Character appearance and clothing attributes
        appear_self = self.char1.return_appearance(self.char1)
        appear_other = self.char1.return_appearance(self.char2)
        for worn_art in worn_list:
            self.assertEqual(worn_art.location, self.char1)
            self.assertTrue(worn_art.db.worn)
            if worn_art.usdesc not in "undershirt item socks item":
                # make certain item appears when the wearer is looked at.
                try:
                    self.assertTrue(worn_art.usdesc in appear_self)
                except AssertionError:
                    err_msg = f'"{worn_art.usdesc}" does not appear when a ' \
                              "Character looks at themself. Their appearance " \
                              f"is:\n{appear_self}."
                    raise AssertionError(err_msg)
                try:
                    self.assertTrue(worn_art.usdesc in appear_other)
                except AssertionError:
                    err_msg = f'"{worn_art.usdesc}" does not appear when a ' \
                              "Character looks at another. Their appearance " \
                              f"is:\n{appear_self}."
                    raise AssertionError(err_msg)
            else:  # the item should be covered.
                # covered item should not appear in return_appearance
                try:
                    self.assertFalse(worn_art.usdesc in appear_self)
                except AssertionError:
                    err_msg = f'"{worn_art.usdesc}" appears when a ' \
                              "Character looks at themself. Their appearance " \
                              f"is:\n{appear_self}."
                    raise AssertionError(err_msg)
                try:
                    self.assertFalse(worn_art.usdesc in appear_other)
                except AssertionError:
                    err_msg = f'"{worn_art.usdesc}" appears when a ' \
                              "Character looks at another. Their appearance " \
                              f"is:\n{appear_self}."
                    raise AssertionError(err_msg)
            # remove the clothing
            worn_art.remove(self.char1, True)
            worn_art.location = self.room1

        # test wearing an armor on each body part, supports multiple races
        # body.part.dr, body.part
        # Add additional races to race_list
        # tuple[0]: and instance of a character of tested race
        # tuple[1]: the list of that races body parts from world.rules.body
        # tuple[2]: class of armor that needs to be made for this race
        race_list = ((self.char1, HUMANOID_BODY, clothing.HumanoidArmor),)
        for char, body_parts, armor_class in race_list:
            worn_list = list()
            for part in body_parts:
                setattr(self, part, create_object(armor_class, key=part))
                armor_inst = getattr(self, part, False)
                if not armor_inst:
                    err_msg = "commands.tests.TestCommands.test_wear_remove " \
                              "wear remove test for all body parts failed to " \
                              f"find {part} in unit test."
                    raise AssertionError(err_msg)
                # verify char prc armor rating is 0 for this part
                char_part = getattr(char.body, part, False)
                if char_part:
                    try:
                        self.assertFalse(hasattr(char_part.dr, 'PRC'))
                    except AssertionError:
                        err_msg = "commands.tests.TestCommands.test_wear_remove " \
                                  f"char.{part}.dr.PRC is " \
                                  f"{char_part.dr.PRC} when is should be Falsey."
                        raise AssertionError(err_msg)
                else:
                    err_msg = "commands.tests.TestCommands.test_wear_remove " \
                              "wear remove test for all body parts failed to " \
                              f"find {part} in char."
                    raise AssertionError(err_msg)
                # set part attributes
                armor_inst.db.clothing_type = part
                armor_inst.location = char
                open_hands = char.open_hands()
                open_hands[0].occupied = armor_inst.dbref
                armor_inst.usdesc = f"{part} armor"
                armor_inst.dr.PRC = 2
                worn_list.append(armor_inst)
                # test wearing
                wear_rc = {char: f"You will be busy for 1 second.|You begin to put on {armor_inst.usdesc}({armor_inst.dbref}).|You wear {armor_inst.usdesc}({armor_inst.dbref}).|You are no longer busy.",
                           self.char2: f"Char begins to put on {armor_inst.usdesc}.|Char wears {armor_inst.usdesc}."}
                wear_cmd = {'arg': f"= wear {part} armor, complete_cmd_early",
                            'receivers': wear_rc}
                # run the tests
                self.loop_tests((wear_cmd,))
            # make certain clothing and Character attributes are correct
            appear_self = char.return_appearance(char)
            appear_other = char.return_appearance(self.char2)
            for worn_art in worn_list:
                self.assertEqual(worn_art.location, char)
                self.assertTrue(worn_art.db.worn)
                # Make certain the dr for the item was cached on wearer
                part_type = worn_art.db.clothing_type
                char_part = getattr(char.body, part_type, False)
                if char_part:
                    try:
                        self.assertEqual(char_part.dr.PRC, 2)
                    except AssertionError:
                        err_msg = f"char.body.{part_type}.dr.PRC is " \
                                  f"{char_part.dr.PRC} when it should be 2."
                        raise AssertionError(err_msg)
                # make certain item appears when the wearer is looked at.
                try:
                    self.assertTrue(worn_art.usdesc in appear_self)
                except AssertionError:
                    err_msg = f'"{worn_art.usdesc}" does not appear when a ' \
                              "Character looks at themself. Their appearance " \
                              f"is:\n{appear_self}."
                    raise AssertionError(err_msg)
                try:
                    self.assertTrue(worn_art.usdesc in appear_other)
                except AssertionError:
                    err_msg = f'"{worn_art.usdesc}" does not appear when a ' \
                              "Character looks at another. Their appearance " \
                              f"is:\n{appear_self}."
                    raise AssertionError(err_msg)

            # test removing an article of clothing from each body part
            for part in body_parts:
                armor_desc = f"{part} armor"
                # test remove
                remove_rc = {char: None,
                             self.char2: f"Char begins to remove {armor_desc}.|Char removes {armor_desc}."}
                remove_post = (f"You will be busy for 1 second\.|You begin to remove {armor_desc}(#\d+)\.|You remove {armor_desc}(#\d+)\.|You are no longer busy\.",)
                remove_cmd = {
                            'arg': f"= remove {part} armor, complete_cmd_early, " \
                                   f"drop {part} armor",
                            'receivers': remove_rc,
                            'post_reg_tests': remove_post
                           }
                # run the tests
                self.loop_tests((remove_cmd,))
            # test Character and clothing after removal
            # Character appearance
            appear_self = char.return_appearance(char)
            appear_other = char.return_appearance(self.char2)
            self.assertEqual(appear_self, "You are not wearing anything.")
            self.assertEqual(appear_other, "Char is not wearing anything.")
            # character should have open hands after dropping the items
            self.assertTrue(char.open_hands())
            # test Character and clothing misc attributes
            for worn_art in worn_list:
                self.assertEqual(worn_art.location, self.room1)
                self.assertFalse(worn_art.db.worn)
                # Make certain the dr for the item was cached on wearer
                part_type = worn_art.db.clothing_type
                char_part = getattr(char.body, part_type, False)
                if char_part:
                    try:
                        self.assertFalse(hasattr(char_part.dr, 'PRC'))
                    except AssertionError:
                        err_msg = f"char.body.{part_type}.dr.PRC is " \
                                  f"{char_part.dr.PRC} when it should not exist."
                        raise AssertionError(err_msg)

    def test_dmg(self):
        """
        Test damage in commands.
        Command.dmg_after_dr method
        """
        # test method damage after damage reduction
        # get armor on
        self.test_helmet.location = self.room1
        # give the helmet an armor rating
        self.test_helmet.dr.PRC = 2
        self.test_helmet.dr.ACD = 3
        self.assertEqual(self.test_helmet.attributes.get('dr_PRC'), 2)
        self.assertEqual(self.test_helmet.dr.PRC, 2)
        command = developer_cmds.CmdMultiCmd
        # put the armor on
        arg = "= get helmet, complete_cmd_early, wear helmet, complete_cmd_early"
        self.call(command(), arg)
        self.assertTrue(self.test_helmet.db.worn)
        # get dr from command.dmg_after_dr
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 3, None, head"
        wnt_msg = "dmg_after_dr returned: 1"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain the lowest number returned is 0
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 0, None, head"
        wnt_msg = "dmg_after_dr returned: 0"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # now change the targets dr to make certain that affects
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 3, None, head"
        wnt_msg = "dmg_after_dr returned: 0"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # Verify giving None as dmg_dealt works
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = None, None, head"
        wnt_msg = r"dmg_after_dr returned: \d+"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # Verify max_defense works
        # Verify Command.dmg_type.TYPE value, adds to attack damage
        # testing self.char1.dr and the worn helmet.dr
        # In this case ACD defense is 6
        #    is the highest defense value vs Command.dmg_types.ACD value of 1 (adds to damage)
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 7, True, head"
        wnt_msg = r"dmg_after_dr returned: 2"
        cmd_result = self.call(command(), arg, wnt_msg)
        # test adding a weapon to the equation
        self.sword.dmg_types.ACD = 1
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wnt_msg = "Char picks up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdMultiCmd
        arg = "= wield sword"
        wnt_msg = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char, requires_wielding:True, cmd_type:one_handed = 7, True, head"
        wnt_msg = r"dmg_after_dr returned: 3"
        cmd_result = self.call(command(), arg, wnt_msg)
        # change the sword's ACD modifier, damage should change by the adjustment
        self.sword.dmg_types.ACD = 2
        wnt_msg = r"dmg_after_dr returned: 4"
        self.call(command(), arg, wnt_msg)
    # test self.dmg_max
        # with a wielded weapon
        # test weapon.dmg_max
        self.sword.dmg_max = 5
        command = developer_cmds.CmdCmdAttrTest
        arg = "requires_wielding:True, cmd_type:one_handed=dmg_max"
        wnt_msg = r"dmg_max: 5"
        self.call(command(), arg, wnt_msg)
        # with no wielded weapon
        command = developer_cmds.CmdMultiCmd
        self.call(command(), '= drop sword', 'You drop a sword(#8).')
        command = developer_cmds.CmdCmdAttrTest
        arg = "cmd_type:unarmed=dmg_max"
        wnt_msg = r"dmg_max: 4"
        self.call(command(), arg, wnt_msg)
    # test self.dmg_mod_stat
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char, cmd_type:unarmed, dmg_max:1 = None, True, chest"
        wnt_msg = r"dmg_after_dr returned: 3"
        cmd_result = self.call(command(), arg, wnt_msg)
        # now change the Characters strength
        old_str = self.char1.STR.get()
        self.char1.STR.set(50)
        self.char1.cache_stat_modifiers()
        arg = "/r dmg_after_dr, char, cmd_type:unarmed, dmg_max:1 = None, True, chest"
        wnt_msg = r"dmg_after_dr returned: 1"
        cmd_result = self.call(command(), arg, wnt_msg)
        self.char1.STR.set(old_str)
    #self.dmg_mod_stat
        # switch the stat modifing damage and run the test again.
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char, cmd_type:unarmed, dmg_max:1, dmg_mod_stat:AGI = None, True, chest"
        wnt_msg = r"dmg_after_dr returned: 3"
        cmd_result = self.call(command(), arg, wnt_msg)
        # now change the Characters strength
        old_str = self.char1.AGI.get()
        self.char1.AGI.set(50)
        self.char1.cache_stat_modifiers()
        arg = "/r dmg_after_dr, char, cmd_type:unarmed, dmg_max:1, dmg_mod_stat:AGI = None, True, chest"
        wnt_msg = r"dmg_after_dr returned: 1"
        self.call(command(), arg, wnt_msg)
        self.char1.STR.set(old_str)
        # test all other stats
        stats_long_names = tuple(STAT_MAP_DICT.values())
        for stat in STATS + stats_long_names:
            if stat != 'STR':
                stat_inst = getattr(self.char1, stat)
                if stat_inst:
                    old_stat_value = stat_inst.get()
                    stat_inst.set(50)
                    self.char1.cache_stat_modifiers()
                    arg = f"/r dmg_after_dr, char, cmd_type:unarmed, dmg_max:1, dmg_mod_stat:{stat} = None, True, chest"
                    wnt_msg = r"dmg_after_dr returned: 1"
                    try:
                        self.call(command(), arg, wnt_msg)
                    except AssertionError:
                        err_msg = "commands.tests.CommandTest.test_dmg " \
                                  f"stat: {stat}, dmg_after_dr returned " \
                                  "incorrect value."
                        raise AssertionError(err_msg)
                    stat_inst.set(old_stat_value)
                else:
                    raise AssertionError(f"self.char1 has no stat {stat}.")
                self.assertIsInstance(stat_inst, Element)

    def test_wield_unwield(self):
        """
        Test the wield and unwield commands.
        """
        # test wielding
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wnt_msg = "You pick up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        arg = "= wield sword"
        wnt_msg = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain wield worked
        items_equipped = self.char1.wielding()
        self.assertTrue(self.sword in items_equipped)
        # verify dropping the sword stops it from being wielded
        arg = "= drop sword"
        wnt_msg = "You drop a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        # test the unwield command
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wnt_msg = "You pick up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        arg = "= unwield sword"
        wnt_msg = "You are not wielding a sword."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain the sword is in hand
        self.assertTrue(self.char1.is_holding(self.sword))
        arg = "= wield sword"
        wnt_msg = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        items_equipped = self.char1.wielding()
        self.assertTrue(self.sword in items_equipped)
        arg = "= unwield sword"
        wnt_msg = "You stop wielding a sword."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        arg = "= drop sword"
        wnt_msg = "You drop a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain it is not wielded after dropping
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        # make certain wield & unwield room messages are correct
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wnt_msg = "Char picks up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        arg = "= wield sword"
        wnt_msg = "Char wields a sword"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        items_equipped = self.char1.wielding()
        self.assertTrue(self.sword in items_equipped)
        arg = "= unwield sword"
        wnt_msg = "Char stops wielding a sword."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        #verify an item deleted while held and or wielded will automatically be removed from hand.
        arg = "= wield sword"
        wnt_msg = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        sword_dbref = self.sword.dbref
        self.sword.delete()
        self.assertFalse(self.char1.wielding())
        hands_state = self.char1.hands()
        self.assertNotEqual(hands_state[0].occupied, sword_dbref)
        self.assertNotEqual(hands_state[1].occupied, sword_dbref)

    def test_rolls(self):
        """
        Test non damage based rolls in commands.
        """
    # test self.roll_max
        # test default values
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d action_roll, self, cmd_type:unarmed, evade_mod_stat:OBS, skill_name:punch = False, True"
        wanted_message = r"roll_max: 51"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        # adjust self.roll_max
        # Test with default values
        # roll max default and default skill ranks in the command used.
        arg = "/d action_roll, self, cmd_type:unarmed, evade_mod_stat:OBS, skill_name:punch, roll_max:53 = False, True"
        wanted_message = r"roll_max: 54"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
    # test char.evd_max interaction with commands
        # Run an evasion roll with no changes base values and no evasion command active
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:unarmed, evade_mod_stat:AGI, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 51"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # increase Character.evd_max
        old_evd_max_AGI = self.char1.evd_max.AGI
        self.char1.evd_max.AGI = 55
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:unarmed, evade_mod_stat:AGI, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 55"  # this number increase to the Character.evd_max.AGI value + evade skill
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.char1.evd_max.AGI = old_evd_max_AGI
        # Run an evasion roll with an evasion command running. Increase skills for not that evasion command
        old_dodge_ranks = self.char1.skills.evasion.dodge
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 51"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.char1.skills.evasion.dodge = old_dodge_ranks
        # run an evasion roll with an useable evasion command active.
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI, evade_msg:test_evade, skill_name:dodge = AGI, False, True"
        wnt_msg = r"roll_max: 52"  # 51 is the default + 1 rank
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # change the characters ranks in the evasion command skill_name
        old_dodge_ranks = self.char1.skills.evasion.dodge
        self.char1.skills.evasion.dodge = 10
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI, skill_name:dodge, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 59"  # 51 + 80% of skill ranks dodge is an 'easy' completion difficulty command
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.char1.skills.evasion.dodge = old_dodge_ranks
    # Test item.act_roll_max_mod
        # wield a sword
        command = developer_cmds.CmdMultiCmd
        arg = '= get sword, complete_cmd_early, wield sword, complete_cmd_early'
        wnt_msg = "You wield a sword"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # tests self.roll_max
        self.sword.act_roll_max_mod = 1
        command = developer_cmds.CmdCmdAttrTest
        arg = "requires_wielding:True, cmd_type:one_handed=roll_max"
        wnt_msg = r"roll_max: 51"
        self.call(command(), arg, wnt_msg)
        self.sword.act_roll_max_mod = 10
        wnt_msg = r"roll_max: 60"
        self.call(command(), arg, wnt_msg)
    # test item evasion bonus item.evd_stats, item.evd_roll_max_mod
        # set evasion bonuses on the wielded item
        self.assertFalse(self.sword.attributes.has('evd_stats'))
        self.sword.evd_stats = ('AGI',)
        self.assertEqual(self.sword.attributes.get('evd_stats'), ('AGI',))
        self.sword.evd_roll_max_mod = 1
        self.assertEqual(self.sword.attributes.get('evd_roll_max_mod'), 1)
        # Run a fake evasion command, will not receive skill rank bonuses
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 52"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # increase the evd_roll_max_mod and run the test again
        self.sword.evd_roll_max_mod = 2
        self.assertEqual(self.sword.attributes.get('evd_roll_max_mod'), 2)
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 53"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # change the attack commands evade_mod_stat, so the evasion commands no longer blocks the attack.
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI, evade_msg:'test evade' = WIS, False, True"
        wnt_msg = r"roll_max: 51"  # the 2 from sword.evade_mod_stat is no longer used
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # change the evasion commands evade_mod_stat
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:WIS, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 51"  # the 2 from sword.evade_mod_stat is no longer used
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
    # both item.evd_roll_max_mod and char.skills.set.name bonus
        # run a good evasion command so it receives item and skill rank bonuses
        command = developer_cmds.CmdCmdFuncTest
        arg = "/d evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI, skill_name:dodge, evade_msg:'test evade' = AGI, False, True"
        wnt_msg = r"roll_max: 54"  # 51 + item bonus 2 + 1 80% of skill rank bonus rounded up
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # reset the evade item stats
        del self.sword.evd_stats
        self.assertFalse(self.sword.attributes.has('evd_stats'))
        del self.sword.evd_roll_max_mod
        self.assertFalse(self.sword.attributes.get('evd_roll_max_mod'))

    def test_sit_stand_lay(self):
        """
        Test the sit stand and lay commands.
        """
        # test sit stand lay also tests Character.set_position
        command = developer_cmds.CmdMultiCmd
        arg = "= sit, complete_cmd_early"
        wnt_msg = r"You will be busy for \d+ second.|You move to sit down.|You sit down.|You are no longer busy."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test other sitting down
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=sit, complete_cmd_early char2"
        wnt_msg = "Char2 moves to sit down.|Char2 sits down."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wnt_msg = r"Char2\(#7\) is sitting here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test character already sitting
        command = developer_cmds.CmdMultiCmd
        arg = "= sit"
        wnt_msg = "^You are already sitting\.$"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # stand up
        command = developer_cmds.CmdMultiCmd
        arg = "= stand, complete_cmd_early"
        wnt_msg = r"You will be busy for \d+ seconds.|You move to stand up.|You stand up.|You are no longer busy."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test other standing
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=stand, complete_cmd_early char2"
        wnt_msg = "Char2 moves to stand up.|Char2 stands up."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wnt_msg = r"Char2\(#7\) is standing here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test character already standing
        command = developer_cmds.CmdMultiCmd
        arg = "= stand"
        wnt_msg = "^You are already standing\.$"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # lay down
        command = developer_cmds.CmdMultiCmd
        arg = "= lay, complete_cmd_early"
        wnt_msg = r"You will be busy for \d+ second.|You move to lay down.|You lay down.|You are no longer busy."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test other laying
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=lay, complete_cmd_early char2"
        wnt_msg = "Char2 moves to lay down.|Char2 lays down."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wnt_msg = r"Char2\(#7\) is laying here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test character already laying
        command = developer_cmds.CmdMultiCmd
        arg = "= lay"
        wnt_msg = "^You are already laying\.$"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # a prone Character can not move.
        command = developer_cmds.CmdMultiCmd
        arg = "= out"
        wnt_msg = "You must stand up first."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # stand both characters up
        command = developer_cmds.CmdMultiCmd
        arg = "= stand, complete_cmd_early"
        wnt_msg = "You will be busy for 3 seconds.|You move to stand up.|You stand up.|You are no longer busy."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        self.char2.position = 'standing'
        self.assertEqual(self.char2.position, 'standing')

    def test_rpsys(self):
        """
        test commands:
            mask sdesc pose say whisper emote
        """
        # test permision lock down for pose, sdesc and mask
        # test commands on a character without the permission
        for cmd in ('mask', 'sdesc', 'pose'):
            command = developer_cmds.CmdMultiCmd
            arg = f"= {cmd}"
            wnt_msg = f"Command '{cmd}' is not available."
            cmd_result = self.call(command(), arg, caller=self.char2)
            self.assertRegex(cmd_result, wnt_msg)
        # on on a character with permission
        # test rpsytem commands
        # mask
        command = developer_cmds.CmdMultiCmd
        arg = "= mask"
        wnt_msg = "Usage: (un)mask sdesc"
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # pose
        command = developer_cmds.CmdMultiCmd
        arg = "= pose"
        wnt_msg = "Usage: pose <pose-text> OR pose obj = <pose-text>"
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # sdesc
        command = developer_cmds.CmdMultiCmd
        arg = "= sdesc"
        wnt_msg = "Usage: sdesc <sdesc-text>"
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # emote
        command = developer_cmds.CmdMultiCmd
        arg = "= emote test emote"
        wnt_msg = "Char2 test emote."
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # veryfy emote echos to room properly
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=emote test emote"
        wnt_msg = "Char2 test emote."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # say
        command = developer_cmds.CmdMultiCmd
        arg = "= say test message"
        wnt_msg = r"You say, \"test message\""
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # verify say echos to room properly
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other Char2=say test message"
        wnt_msg = r'Char2\(#7\) says, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test saying to another Character
        command = standard_cmds.CmdSay
        arg = 'to char2 "test message'
        wnt_msg = r'You say to char2(#7), "test message".'
        cmd_result = self.call(command(), arg, wnt_msg)
        # test saying at another Character
        command = standard_cmds.CmdSay
        arg = 'at char2 "test message'
        wnt_msg = r'You say at char2(#7), "test message".'
        cmd_result = self.call(command(), arg, wnt_msg)
        # Test your name is replace with You when you are spoken to
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to char "test message'
        wnt_msg = r'Char2(#7) says to you, "test message".'
        self.call(command(), arg, wnt_msg)
        # make certain say to replaces targets message with name
        # with multiple targets
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to char and obj "test message'
        wnt_msg = r'Char2(#7) says to obj(#4) and you, "test message".'
        self.call(command(), arg, wnt_msg)
        # test seeing a say that does not target you.
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to obj2 and obj "test message'
        wnt_msg = r'Char2(#7) says to obj2(#5) and obj(#4), "test message".'
        self.call(command(), arg, wnt_msg)
        arg = '=control_other char2=say at obj2 and obj "test message'
        wnt_msg = r'Char2(#7) says at obj2(#5) and obj(#4), "test message".'
        self.call(command(), arg, wnt_msg)
        # Test whisper
        # say
        # test saying to another Character
        command = developer_cmds.CmdMultiCmd
        arg = '=whisper to char2 "test message'
        wnt_msg = 'You whisper to char2(#7), "test message".'
        self.call(command(), arg, wnt_msg)
        # test saying at another Character
        command = developer_cmds.CmdMultiCmd
        arg = '=whisper at char2 "test message'
        wnt_msg = 'You whisper at char2(#7), "test message".'
        self.call(command(), arg, wnt_msg)
        # verify say echos to room properly
        command = developer_cmds.CmdMultiCmd
        arg = '= control_other Char2=whisper to obj "test message'
        wnt_msg = 'Char2(#7) whispers something to obj(#4).'
        self.call(command(), arg, wnt_msg)
        # Test your name is replace with You when you are whispered to
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to char "test message'
        wnt_msg = r'Char2(#7) whispers to you, "test message".'
        self.call(command(), arg, wnt_msg)
        # make certain whisper to replaces targets message with name
        # with multiple targets
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to char and obj "test message'
        wnt_msg = r'Char2(#7) whispers to obj(#4) and you, "test message".'
        self.call(command(), arg, wnt_msg)
        # test seeing a multi target whisper that does not target you.
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to obj2 and obj "test message'
        wnt_msg = r'Char2(#7) whispers something to obj2(#5) and obj(#4).'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        arg = '=control_other char2=whisper at obj2 and obj "test message'
        wnt_msg = r'Char2(#7) whispers something at obj2(#5) and obj(#4).'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test recog
        command = developer_cmds.CmdMultiCmd
        arg = "= recog Char2 as CharTwo"
        wnt_msg = r"Char will now remember Char2 as CharTwo."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wnt_msg = r"CharTwo\(#7\) is\s*\w* here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdMultiCmd
        arg = "= forget CharTwo"
        wnt_msg = r"Char will now know them only as 'Char2'."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test mask
        command = developer_cmds.CmdMultiCmd
        arg = "= mask test change"
        wnt_msg = r"You wear a mask as 'test change [masked]'."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wnt_msg = r"test change"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdMultiCmd
        arg = "= unmask"
        wnt_msg = r"You remove your mask and are again 'Char'."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test pose
        command = developer_cmds.CmdMultiCmd
        arg = "= pose obj= test pose"
        wnt_msg = r"Pose will read 'Obj test pose.'."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wnt_msg = r"Obj\(#4\) test pose\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdMultiCmd
        arg = "= pose reset obj="
        wnt_msg = r"Pose will read 'Obj is here.'."
        self.call(command(), arg, wnt_msg, caller=self.char1)

    def test_stats_cmd(self):
        # test the statistics command
        command = developer_cmds.CmdMultiCmd
        wnt_msg = "Statistics for: Char\nOthers who do not know this Character see |o as: Char\n\r\n\nHealth:\n    hp            100 \n    endurance     100 \n\r\n\nAttributes:\n    Constitution     100     Strength        100 \n    Agility          100     Observation     100 \n    Intelligence     100     Speed           100 \n    Charisma         100     Wisdom          100"
        for arg in ('stat', 'stats', 'statistics'):
            cmd_result = self.call(command(), "= "+arg)
            self.assertRegex(cmd_result, wnt_msg)

    def test_cond_cmd(self):
        # test the statistics command
        command = developer_cmds.CmdMultiCmd
        self.call(command(), "= get sword, complete_cmd_early, wield sword")
        for arg in ('cond', 'condition'):
            cmd_result = self.call(command(), "= "+arg)
            self.assertRegex(cmd_result, "Condition of: Char")
            self.assertRegex(cmd_result, "Dead     No")
            self.assertRegex(cmd_result, "Position: Standing")
            self.assertRegex(cmd_result, "Status:")
            self.assertRegex(cmd_result, "Body")
            self.assertRegex(cmd_result, "wielding: a sword\(#8\)")

    def test_unarmed(self):
        """
        test the unarmed command set.
        """
        # tests for the kick command
        kick_rc = {self.char1: "You will be busy for 5 seconds.|Facing char2(#7) you lift your knee up preparing an attack.|kick",
                   self.char2: "Facing you char lifts theirs knee up preparing an attack.|You may want to dodge.|evade ",
                   self.obj1: "Facing char2 char lifts theirs knee up preparing an attack.|Char kicks at char2 with their foot and connects. Hitting char2's "}
        kick_post = ("kick \d+ VS evade \d+: You kick at char2\(#7\) with your foot and connect\. Hitting char2\(#7\)'s",
                     "Dealing \d+ damage\.|You are no longer busy\.",
                     # defenders messages
                     "You may want to dodge\.",
                     "evade \d+ VS kick \d+: Char kicks at you with their foot and connects. Hitting your",
                     "You take \d+ damage\.",
                     # location messages
                     "Hitting char2's \w+\s*\w*\.")
        kick_cmd = {
                    'arg': f"= kick/unit_test_succ Char2, complete_cmd_early",
                    'receivers': kick_rc,
                    'post_reg_tests': kick_post
                   }
        # test a missed kick
        kick_miss_rc = {self.char1: "You will be busy for 5 seconds.|Facing char2(#7) you lift your knee up preparing an attack.|kick",
                   self.char2: "Facing you char lifts theirs knee up preparing an attack.|You may want to dodge.|evade",
                   self.obj1: "Facing char2 char lifts theirs knee up preparing an attack.|Char kicks at char2 with their foot and misses."}
        kick_miss_post = ("kick \d+ VS evade \d+: You kick at char2\(#7\) with your foot but miss\.",
                     # defenders messages
                     "You may want to dodge\.",
                     "evade \d+ VS kick \d+: Char kicks at you with their foot but you successfully evade the kick\.")
        kick_missed_cmd = {
                    'arg': f"= kick/unit_test_fail Char2 , complete_cmd_early",
                    'receivers': kick_miss_rc,
                    'post_reg_tests': kick_miss_post
                   }

        # tests for the punch command
        punch_rc = {self.char1: "You will be busy for 3 seconds.|Facing char2(#7) you pull your hand back preparing an attack.",
                   self.char2: "Facing you char pulls theirs hand back preparing an attack.",
                   self.obj1: "Facing char2 char pulls theirs hand back preparing an attack.|Char punches at char2 with their fist and connects. Hitting char2's "}
        punch_post = ("punch \d+ VS evade \d+: You punch at char2\(#7\) with your fist and connect\. Hitting char2\(#7\)'s ",
                     "Dealing \d+ damage\.|You are no longer busy\.",
                     # defenders messages
                     "evade \d+ VS punch \d+: Char punches at you with their fist and connects. Hitting your ",
                     "You take \d+ damage\.",
                     # location messages
                     "Hitting char2's \w+\s*\w*\.")
        punch_cmd = {
                    'arg': f"= punch/unit_test_succ Char2, complete_cmd_early",
                    'receivers': punch_rc,
                    'post_reg_tests': punch_post
                   }
        # test a punch that misses
        punch_miss_rc = {self.char1: "You will be busy for 3 seconds.|Facing char2(#7) you pull your hand back preparing an attack.",
                         self.char2: "Facing you char pulls theirs hand back preparing an attack.",
                         self.obj1: "Facing char2 char pulls theirs hand back preparing an attack.|Char punches at char2 with their fist and misses."}
        punch_miss_post = ("punch \d+ VS evade \d+: You punch at char2\(#7\) with your fist but miss.",
                     "Dealing \d+ damage\.|You are no longer busy\.",
                     # defenders messages
                     "evade \d+ VS punch \d+: Char punches at you with their fist but you successfully evade the punch\.")
        punch_missed_cmd = {
                    'arg': f"= punch/unit_test_fail Char2, complete_cmd_early",
                    'receivers': punch_miss_rc,
                    'post_reg_tests': punch_miss_post
                   }

        # run the tests
        self.loop_tests((kick_cmd, kick_missed_cmd, punch_cmd, punch_missed_cmd))

        # make certain commands have been taking a cost.
        self.assertTrue(self.char1.END < 100)

    def test_one_handed(self):
        """
        test the unarmed command set.
        """
        # tests for the stab command
        stab_rc = {self.char1: "You will be busy for 3 seconds.|Facing char2(#7) you raise a sword preparing an attack.",
                   self.char2: "Facing you char raises a sword preparing an attack.",
                   self.obj1: "Facing char2 char raises a sword preparing an attack.|Char stabs at char2 with their sword and connects. Hitting char2's "}
        stab_post = ("stab \d+ VS evade \d+: You stab at char2\(#7\) with your sword and connect\. Hitting char2\(#7\)'s",
                     "Dealing \d+ damage\.|You are no longer busy\.",
                     # defenders messages
                     "evade \d+ VS stab \d+: Char stabs at you with their sword and connects. Hitting your",
                     "You take \d+ damage\.",
                     # location messages
                     "Hitting char2's \w+\s*\w*\.")
        stab_cmd = {
                    'arg': f"= stab/unit_test_succ Char2 , complete_cmd_early",
                    'receivers': stab_rc,
                    'post_reg_tests': stab_post
                   }
        # test a missed stab
        stab_miss_rc = {self.char1: "You will be busy for 3 seconds.|Facing char2(#7) you raise a sword preparing an attack.",
                   self.char2: "Facing you char raises a sword preparing an attack.",
                   self.obj1: "Facing char2 char raises a sword preparing an attack.|Char stabs at char2 with their sword and misses."}
        stab_miss_post = ("stab \d+ VS evade \d+: You stab at char2\(#7\) with your sword but miss\.",
                          # defenders messages
                          "evade \d+ VS stab \d+: Char stabs at you with their sword but you successfully evade the stab\.")
        stab_missed_cmd = {
                    'arg': f"= stab/unit_test_fail Char2, complete_cmd_early",
                    'receivers': stab_miss_rc,
                    'post_reg_tests': stab_miss_post
                   }

        # give a rank in each move
        for skill_name in self.char1.skills.one_handed.el_list:
            setattr(self.char1.skills.one_handed, skill_name, 1)

        # wield a sword for the command
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early, wield sword"
        wnt_msg = "You wield a sword in your"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)

        # run the tests
        self.loop_tests((stab_cmd, stab_missed_cmd))

        # make certain commands have been taking a cost.
        self.assertTrue(self.char1.END < 100)

    def test_evasion(self):
        """
        test the evasion command set.
        """
        # tests for the dodge command
        dodge_rc = {self.char1: "Char2 begins to sway warily.",
                   self.char2: "You will be busy for 10 seconds.|You begin to sway warily.",
                   self.obj1: "Char2 begins to sway warily."}
        dodge_post = tuple()
        dodge_cmd = {
                    'arg': f"= dodge",
                    'receivers': dodge_rc,
                    'post_reg_tests': dodge_post,
                    'caller': self.char2
                   }
        punch_rc = {self.char1: "You will be busy for 3 seconds.|Facing char2(#7) you pull your hand back preparing an attack.|Char2 tries to dodge the incoming attack.",
                   self.char2: "Facing you char pulls theirs hand back preparing an attack.|You are no longer busy.|You try to dodge the incoming attack.",
                   self.obj1: "Facing char2 char pulls theirs hand back preparing an attack.|Char2 tries to dodge the incoming attack.|Char punches at char2 with their fist "}
        #punch_post = ("You try to dodge the incoming attack.",)
        punch_post = tuple()
        punch_cmd = {
                    'arg': f"= punch Char2, complete_cmd_early",
                    'receivers': punch_rc,
                    'post_reg_tests': punch_post
                   }

        # run the tests
        self.loop_tests((dodge_cmd, punch_cmd))

        # make certain commands have been taking a cost.
        self.assertTrue(self.char1.END < 100)

    def test_get_body_part(self):
        """
            Test Command methods.
            Many methods are tested in other command unit tests.
        """

        # test method get_body_part
        # run a test with no arguments. Object with a body part
        # self.get_body_part and body.get_part tested here
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, char2"
        wnt_msg = "get_body_part returned: broke: 0 bleeding: 0 missing: 0 occupied: 0 wielding: 0"
        self.call(command(), arg, wnt_msg)
        # now test an object with no body parts
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, obj"
        wnt_msg = "get_body_part returned: False"
        self.call(command(), arg, wnt_msg)
        # test requesting a specific part
        command = developer_cmds.CmdCmdFuncTest
        for part_name in HUMANOID_BODY:
            arg = f"/r get_body_part, char2 = None, {part_name}, False"
            wnt_msg = "get_body_part returned: broke: 0 bleeding: 0 missing: 0 occupied: 0 wielding: 0"
            self.call(command(), arg, wnt_msg)

    def test_cost(self):
        """
        Test command method cost.
        self.cost() Command.cost()

        Test for:
            error catching
            correct costs taken
                all stats tested including willpower and endurance
                all cost_levels tested
                modifier stat is adjust to 100, 0 and -100 for each test
        """
        from utils.element import Element
        # passing no arguments, no deferred command
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r cost, self"
        wnt_msg = "cost returned: 0"
        self.call(command(), arg, wnt_msg)
        # test with an incorrect cost_level
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r/d cost, char, cost_level:low, cost_stat:END = low, END"
        wnt_msg = "You will be busy for 3 seconds.|Error message: rules.action.cost, character: 6 action: cmd_func_test cost_level argument must equal 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number."
        cmd_result = self.call(command(), arg, wnt_msg)
        # test incorrect cost_level without a deferred command
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r cost, char, cost_level:low, cost_stat:END = low, END"
        wnt_msg = "Error message: rules.action.cost, character: 6 cost_level argument must equal 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number."
        cmd_result = self.call(command(), arg, wnt_msg)
        # test with incorrect cost_stat
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r/d cost, char, cost_level:low, cost_stat:ZZZ = very_easy, ZZZ"
        wnt_msg = "You will be busy for 3 seconds.|Error message: rules.action.cost, character: 6, action: cmd_func_test, Failed to find an instance of stat ZZZ on character. Find acceptable stats in world.rules.stats.STATS."
        cmd_result = self.call(command(), arg, wnt_msg)
        # test without a deffered command, incorrect cost_stat
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r cost, char, cost_level:low, cost_stat:ZZZ = very_easy, ZZZ"
        wnt_msg = "Error message: rules.action.cost, character: 6, Failed to find an instance of stat ZZZ on character. Find acceptable stats in world.rules.stats.STATS."
        cmd_result = self.call(command(), arg, wnt_msg)

        # test draining all stat types, all cost levels
        # with modifier stat being 100, 0 than -100
        command = developer_cmds.CmdCmdFuncTest
        std_cost_stats = ('WILL', 'willpower', 'END', 'endurance')
        stats_long_names = tuple(STAT_MAP_DICT.values())
        for stat in std_cost_stats + STATS + stats_long_names:
            # get variables needed for tests
            cost_stat_instance = getattr(self.char1, stat, False)
            if cost_stat_instance:
                # get the stat that modifies this stat's cost.
                cost_mod_stat = getattr(cost_stat_instance, 'modifier_stat', stat)
                cost_mod_stat_inst = getattr(self.char1, cost_mod_stat, False)
                if not cost_mod_stat_inst:
                    err_msg = "commands.tests.TestCommands.test_cost: failed " \
                              f"to cost modifier stat for {stat} on " \
                              f"self.char.{cost_mod_stat}"
                    raise AssertionError(err_msg)
            else:  # an instance of the stat is required
                err_msg = "commands.tests.TestCommands.test_cost: failed to " \
                          f"find self.char1.{stat}"
                raise AssertionError(err_msg)
            # test all cost levels
            for cost_level in COST_LEVELS:
                # test multiple cost modifier levels
                for mod_stat_adj in (100, 0, -95):
                    cost_stat_instance.set(100)
                    cost_mod_stat_inst.set(mod_stat_adj)
                    cost_stat_pre_run = cost_stat_instance.get()
                    # get the cost that should be removed.
                    stat_action_cost_mod = getattr(self.char1, f"{cost_mod_stat}_action_cost_mod", 0)
                    base_cost = COST_LEVELS[cost_level]
                    cost = base_cost - (base_cost * stat_action_cost_mod)
                    # Run command removing stat, where cost_mod_stat is 100
                    arg = f"/r/d cost, char, cost_level:{cost_level}, cost_stat:{stat} = {cost_level}, {stat}"
                    wnt_msg = f"You will be busy for 3 seconds.|cost returned: {cost}|You are no longer busy."
                    cmd_result = self.call(command(), arg, wnt_msg)
                    # verify correct ammount was taken
                    try:
                        self.assertEqual(cost_stat_instance, cost_stat_pre_run - cost)
                    except AssertionError: # make the assert message meaningful
                        err_msg = "commands.test.TestCommands.test_cost, " \
                                  f"cost_stat_instance: {cost_stat_instance.name}" \
                                  f" is {cost_stat_instance.get()} when it " \
                                  f"should be {cost_stat_pre_run - cost}."
                        raise AssertionError(err_msg)

                    # verify evasion commands taking cost
                    cost_stat_instance.set(100)
                    cost_mod_stat_inst.set(mod_stat_adj)
                    cost_stat_pre_run = cost_stat_instance.get()
                    # get the cost that should be removed.
                    stat_action_cost_mod = getattr(self.char1, f"{cost_mod_stat}_action_cost_mod", 0)
                    base_cost = COST_LEVELS[cost_level]
                    cost = base_cost - (base_cost * stat_action_cost_mod)
                    # Run command removing stat, where cost_mod_stat is 100
                    arg = f"/r/d evade_roll, self, cost_level:{cost_level}, cost_stat:{stat}, cmd_type:evasion, " \
                          "evade_msg:evasion_message, evade_mod_stat:AGI  = AGI"
                    wnt_msg = f"You will be busy for 3 seconds.|You are no longer busy.|You try evasion_message|evade_roll returned: "
                    cmd_result = self.call(command(), arg, wnt_msg)
                    # verify correct ammount was taken
                    try:
                        self.assertEqual(cost_stat_instance, cost_stat_pre_run - cost)
                    except AssertionError: # make the assert message meaningful
                        err_msg = "commands.test.TestCommands.test_cost, " \
                                  f"cost_stat_instance: {cost_stat_instance.name}" \
                                  f" is {cost_stat_instance.get()} when it " \
                                  f"should be {cost_stat_pre_run - cost}."
                        raise AssertionError(err_msg)
                    # set the stat back to default max
                    cost_stat_instance.set(100)
                    cost_mod_stat_inst.set(100)

                    # make certain cost stat and modifier stat are still Elements
                    self.assertIsInstance(cost_stat_instance, Element)
                    self.assertIsInstance(cost_mod_stat_inst, Element)

    def test_combat_action(self):
        """
        combat_action is tested many times in
        test_dmg and test_rolls

        These test is for the arguments that are not used in those tests.
        """
        # test hitting with replacement messages.
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r/d/unit_test_succ combat_action, Char2, weapon_desc:weapon_name, cmd_type:unarmed = False, caller_message, target_message, room_message"
        receivers = {
            self.char1: None,
            self.char2: None,
            self.obj1: None
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers)
        self.assertRegex(cmd_result, ": caller_message and connect\. Hitting char2\(#7\)'s ")
        self.assertRegex(cmd_result, ": target_message and connects\. Hitting your ")
        self.assertRegex(cmd_result, "room_message and connects\. Hitting char2's ")
        # test missing with replacement arguments
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r/d/unit_test_fail combat_action, Char2, weapon_desc:weapon_name, cmd_type:unarmed = False, caller_message, target_message, room_message"
        receivers = {
            self.char1: None,
            self.char2: None,
            self.obj1: None
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers)
        self.assertRegex(cmd_result, ": caller_message but miss\.")
        self.assertRegex(cmd_result, ": target_message but you successfully evade the cmd_func_test\.")
        self.assertRegex(cmd_result, "room_message and misses\.")

    def test_look(self):
        """
        test the look command

        Clothing appearances is tested in test_wear_remove
        """
        from commands.standard_cmds import CmdLook
        self.obj3 = create.create_object(
            self.object_typeclass, key="Obj3", location=self.room2, home=self.room2
        )
        self.room2.db.desc = "Room2 description"
        self.exit2 = create.create_object(
            self.exit_typeclass, key="a door", location=self.room1, destination=None
        )
        self.char3 = create.create_object(
            self.character_typeclass, key="Char3", location=self.room1, home=self.room1
        )

        # using aliases
        for aliase in CmdLook.aliases:
            # run a standard look at a room
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase}"
            receivers = {
                self.char1: 'Room_desc\nOn the ground are an Obj(#4), an Obj2(#5), a sword(#8), a test hat(#9), a test helmet(#11) and a test shirt(#10).\nChar2(#7) is here. A normal person(#14) is here.\nYou may leave by out(#3) or a door(#13).',
                self.char2: None
            }
            cmd_result = self.call_multi_receivers(command(), arg, receivers)
            # look at a room with no description.
            old_room_desc = self.room1.db.desc
            self.room1.db.desc = None
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase}"
            receivers = {
                self.char1: 'You are in a space devoid of description.\nOn the ground are an Obj(#4), an Obj2(#5), a sword(#8), a test hat(#9), a test helmet(#11) and a test shirt(#10).\nChar2(#7) is here. A normal person(#14) is here.\nYou may leave by out(#3) or a door(#13).',
                self.char2: None
            }
            cmd_result = self.call_multi_receivers(command(), arg, receivers)
            self.room1.db.desc = old_room_desc
            # Character looks at another Character
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} Char2"
            receivers = {
                self.char1: "Char2(#7) is not wearing anything.",
                self.char2: "Char looks at you.",
                self.obj1: "Char looks at char2"
            }
            self.call_multi_receivers(command(), arg, receivers)
            # Character looks at self
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} me"
            receivers = {
                self.char1: "You are not wearing anything.",
                self.char2: "Char looks at themself."
            }
            self.call_multi_receivers(command(), arg, receivers)
            # character looks at an exit
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} out"
            receivers = {
                self.char1: 'Through out(#3) you see:\r\nRoom2 description\nOn the ground is an Obj3(#12)',
                self.char2: "Char looks through out."
            }
            self.call_multi_receivers(command(), arg, receivers)
            # now look at an exit with no destination
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} door"
            receivers = {
                self.char1: "A door(#13) does not appear to lead anywhere.",
                self.char2: "Char looks through a door."
            }
            self.call_multi_receivers(command(), arg, receivers)
            # look at an object without a description
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} Obj"
            receivers = {
                self.char1: "Obj(#4) is devoid of description.",
                self.char2: "Char looks at obj.",
                self.obj1: "Char looks at you."
            }
            self.call_multi_receivers(command(), arg, receivers)
            # give the object a description.
            self.obj1.db.desc = 'This is a plain object.'
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} Obj"
            receivers = {
                self.char1: "This is a plain object.",
                self.char2: "Char looks at obj.",
                self.obj1: "Char looks at you."
            }
            self.call_multi_receivers(command(), arg, receivers)
            # look at a container
            self.obj1.container = True
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} Obj"
            receivers = {
                self.char1: "This is a plain object.\nIt contains nothing.",
                self.char2: "Char looks at obj.",
                self.obj1: "Char looks at you."
            }
            cmd_result = self.call_multi_receivers(command(), arg, receivers)
            self.assertRegex(cmd_result, "^This is a plain object\.\nIt contains nothing\.Char looks at obj\.Char looks at you\.$")
            # look at a container with an object in it
            self.obj3.location = self.obj1
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} Obj"
            receivers = {
                self.char1: "This is a plain object.\nIt contains an Obj3(#12).",
                self.char2: "Char looks at obj.",
                self.obj1: "Char looks at you."
            }
            cmd_result = self.call_multi_receivers(command(), arg, receivers)
            self.assertRegex(cmd_result, '^This is a plain object\.\\nIt contains an Obj3\(\#12\)\.Char looks')
            # look at a container with multiple objects in it
            self.test_shirt.location = self.obj1
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} Obj"
            receivers = {
                self.char1: "This is a plain object.\nIt contains an Obj3(#12) and a test shirt(#10).",
                self.char2: "Char looks at obj.",
                self.obj1: "Char looks at you."
            }
            cmd_result = self.call_multi_receivers(command(), arg, receivers)
            self.assertRegex(cmd_result, '^This is a plain object\.\\nIt contains an Obj3\(\#12\) and a test shirt\(\#10\)\.Char looks at obj\.Char looks at you\.')
            # look at object in a container
            self.test_shirt.location = self.obj1
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} Obj3 in Obj"
            receivers = {
                self.char1: "Obj3(#12) is devoid of description.",
                self.char2: "Char looks at something in obj.",
                self.obj3: "Char looks at you."
            }
            cmd_result = self.call_multi_receivers(command(), arg, receivers)
            # put objects in self.obj1 back and reset settings changed
            self.test_shirt.location = self.room1
            self.obj1.db.desc = None
            self.obj1.container = False
            self.obj3.location = self.room2


            # test when the Character has no location
            self.char1.location = None
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase}"
            wnt_msg = "You have no location to look at!"
            cmd_result = self.call(command(), arg, wnt_msg)
            self.assertRegex(cmd_result, "caller has no location")
            self.char1.location =  self.room1
            # test a bad target name
            command = developer_cmds.CmdMultiCmd
            arg = f"= {aliase} intentional fail"
            wnt_msg = "You do not see intentional fail here."
            cmd_result = self.call(command(), arg, wnt_msg)

    def test_um_emote(self):
        self.char3 = create.create_object(
            self.character_typeclass, key="Character Three", location=self.room1, home=self.room1
        )
        self.char3.sdesc.add("a normal person")
        self.char4 = create.create_object(
            self.character_typeclass, key="Character Four", location=self.room1, home=self.room1
        )
        self.char3.sdesc.add("a normal person")
        self.char5 = create.create_object(
            self.character_typeclass, key="Character Five", location=self.room1, home=self.room1
        )
        self.char5.usdesc ='a normal giant'
        # general message
        command = developer_cmds.CmdCmdFuncTest
        arg = "send_emote, Char2 = test message"
        receivers = {
            self.char1: "test message",
            self.char2: "test message",
            self.obj1: "test message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test /me switchm /me is self.char1 command caller
        command = developer_cmds.CmdCmdFuncTest
        arg = "send_emote, char2 = /Me message"
        receivers = {
            self.char1: "You message",
            self.char2: f"{ANSI_BLUE}Char{ANSI_NORMAL} message",
            self.obj1: f"Char message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test /target switch
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal = /Target message"
        receivers = {
            self.char1: f"A normal person(#12) message",
            self.char3: "You message",
            self.obj1: "A normal person message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # when target is not the first thing in the emote
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal = Pre message /target message"
        receivers = {
            self.char1: "Pre message a normal person(#12) message",
            self.char3: "Pre message you message",
            self.obj1: "Pre message a normal person message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test /target switch, with a number
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, 2 person = /Target message"
        receivers = {
            self.char1: "A normal person(#13) message",
            self.char2: "A normal person message",
            self.char3: "A normal person message",
            self.char4: "You message",
            self.char5: "A normal person message",
            self.obj1: "A normal person message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test /target's switch
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, 2 person = /Target's message"
        receivers = {
            self.char1: "A normal person(#13)'s message",
            self.char2: "A normal person's message",
            self.char3: "A normal person's message",
            self.char4: "Your message",
            self.char5: "A normal person's message",
            self.obj1: "A normal person's message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # search for multi word desc
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal person = /Target message"
        receivers = {
            self.char1: "A normal person(#12) message",
            self.char2: "A normal person message",
            self.char3: "You message",
            self.char4: "A normal person message",
            self.char5: "A normal person message",
            self.obj1: "A normal person message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        arg = f"send_emote, normal giant = /Target message"
        receivers = {
            self.char1: "A normal giant(#14) message",
            self.char2: "A normal giant message",
            self.char3: "A normal giant message",
            self.char4: "A normal giant message",
            self.char5: "You message",
            self.obj1: "A normal giant message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # target an object
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, obj2 = /Target message"
        receivers = {
            self.char1: "Obj2(#5) message",
            self.char2: "Obj2 message",
            self.char3: "Obj2 message",
            self.char4: "Obj2 message",
            self.char5: "Obj2 message",
            self.obj2: "You message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test after punctuation:
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal person = Sentence one. /Target sentence two."
        receivers = {
            self.char1: "Sentence one. A normal person(#12) sentence two.",
            self.char2: "Sentence one. A normal person sentence two.",
            self.char3: "Sentence one. You sentence two.",
            self.char4: "Sentence one. A normal person sentence two.",
            self.char5: "Sentence one. A normal person sentence two.",
            self.obj1: "Sentence one. A normal person sentence two."
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # color codes at the start of a sentence.
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal person = |r/Target message|n"
        receivers = {
            self.char1: f"{ANSI_RED}A normal person(#12) message{ANSI_NORMAL}",
            self.char2: f"{ANSI_RED}A normal person message{ANSI_NORMAL}",
            self.char3: f"{ANSI_RED}You message{ANSI_NORMAL}",
            self.char4: f"{ANSI_RED}A normal person message{ANSI_NORMAL}",
            self.char5: f"{ANSI_RED}A normal person message{ANSI_NORMAL}",
            self.obj1: f"{ANSI_RED}A normal person message{ANSI_NORMAL}"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # Test color codes after end of sentences and in the middle of a sentence
        # with an ansi switch after the punctiation at the end of the sentence.
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal person = Sentence one. |r/Target sentence two.|n |r/Target sentence three.|n sentence three |r/target|n."
        receivers = {
            self.char1: f"Sentence one. {ANSI_RED}A normal person(#12) sentence two.{ANSI_NORMAL} " \
                        f"{ANSI_RED}A normal person(#12) sentence three.{ANSI_NORMAL} " \
                        f"sentence three {ANSI_RED}a normal person(#12){ANSI_NORMAL}.",
            self.char2: f"Sentence one. {ANSI_RED}A normal person sentence two.{ANSI_NORMAL} " \
                        f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}",
            self.char3: f"Sentence one. {ANSI_RED}You sentence two.{ANSI_NORMAL} " \
                        f"{ANSI_RED}You sentence three.{ANSI_NORMAL}",
            self.char4: f"Sentence one. {ANSI_RED}A normal person sentence two.{ANSI_NORMAL} " \
                        f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}",
            self.char5: f"Sentence one. {ANSI_RED}A normal person sentence two.{ANSI_NORMAL} " \
                        f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}",
            self.obj1: f"Sentence one. {ANSI_RED}A normal person sentence two.{ANSI_NORMAL} " \
                       f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test as previous but text tag appears before functuation.
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal person = Sentence one. |r/Target sentence two|n. |r/Target sentence three.|n sentence three |r/target|n."
        receivers = {
            self.char1: f"Sentence one. {ANSI_RED}A normal person(#12) sentence two{ANSI_NORMAL}. " \
                        f"{ANSI_RED}A normal person(#12) sentence three.{ANSI_NORMAL} " \
                        f"sentence three {ANSI_RED}a normal person(#12){ANSI_NORMAL}.",
            self.char2: f"Sentence one. {ANSI_RED}A normal person sentence two{ANSI_NORMAL}. " \
                        f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}",
            self.char3: f"Sentence one. {ANSI_RED}You sentence two{ANSI_NORMAL}. " \
                        f"{ANSI_RED}You sentence three.{ANSI_NORMAL}",
            self.char4: f"Sentence one. {ANSI_RED}A normal person sentence two{ANSI_NORMAL}. " \
                        f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}",
            self.char5: f"Sentence one. {ANSI_RED}A normal person sentence two{ANSI_NORMAL}. " \
                        f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}",
            self.obj1: f"Sentence one. {ANSI_RED}A normal person sentence two{ANSI_NORMAL}. " \
                       f"{ANSI_RED}A normal person sentence three.{ANSI_NORMAL}"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test where Characters has different recog for the target
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, obj2 = /Target message"
        self.char1.recog.add(self.obj2, "obj2 char1")
        self.char2.recog.add(self.obj2, "obj2 char2")
        self.char3.recog.add(self.obj2, "obj2 char3")
        self.char4.recog.add(self.obj2, "obj2 char4")
        self.char5.recog.add(self.obj2, "obj2 char5")
        receivers = {
            self.char1: "Obj2 char1(#5) message",
            self.char2: "Obj2 char2 message",
            self.char3: "Obj2 char3 message",
            self.char4: "Obj2 char4 message",
            self.char5: "Obj2 char5 message",
            self.obj2: "You message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test with upper cased recog
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, normal = /Target message /target"
        self.char1.recog.add(self.char3, "Char3 for char1")
        self.char2.recog.add(self.char3, "Char3 for char2")
        self.char3.recog.add(self.char3, "Char3 for char3")
        self.char4.recog.add(self.char3, "Char3 for char4")
        self.char5.recog.add(self.char3, "Char3 for char5")
        receivers = {
            self.char1: "Char3 for char1(#12) message Char3 for char1(#12)",
            self.char2: "Char3 for char2 message Char3 for char2",
            self.char3: "You message you",
            self.char4: "Char3 for char4 message Char3 for char4",
            self.char5: "Char3 for char5 message Char3 for char5",
            self.obj2: "A normal person message a normal person"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        self.char1.recog.remove(self.char3)
        self.char2.recog.remove(self.char3)
        self.char3.recog.remove(self.char3)
        self.char4.recog.remove(self.char3)
        self.char5.recog.remove(self.char3)
        # the command has no target, but the /target switch appears in the msg
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, None = /target message"
        receivers = {
            self.char1: f"{ANSI_RED}nothing{ANSI_NORMAL} message",
            self.char2: f"{ANSI_RED}nothing{ANSI_NORMAL} message",
            self.char3: f"{ANSI_RED}nothing{ANSI_NORMAL} message",
            self.char4: f"{ANSI_RED}nothing{ANSI_NORMAL} message",
            self.char5: f"{ANSI_RED}nothing{ANSI_NORMAL} message",
            self.obj1: f"{ANSI_RED}nothing{ANSI_NORMAL} message"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test multiple targets
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, to person and 2 person = /Target message. /Target"
        receivers = {
            self.char1: "A normal person(#12) and a normal person(#13) message. A normal person(#12) and a normal person(#13)",
            self.char2: "A normal person and a normal person message. A normal person and a normal person",
            self.char3: "A normal person and you message. A normal person and you",
            self.char4: "A normal person and you message. A normal person and you",
            self.char5: "A normal person and a normal person message. A normal person and a normal person",
            self.obj1: "A normal person and a normal person message. A normal person and a normal person"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # multiple targets where the sender is in the target list.
        command = developer_cmds.CmdCmdFuncTest
        arg = f"send_emote, to self and 2 person = /Target message. /Target"
        receivers = {
            self.char1: "A normal person(#13) and you message. A normal person(#13) and you",
            self.char2: "Char and a normal person message. Char and a normal person",
            self.char3: "Char and a normal person message. Char and a normal person",
            self.char4: "Char and you message. Char and you",
            self.char5: "Char and a normal person message. Char and a normal person",
            self.obj1: "Char and a normal person message. Char and a normal person"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test multi targets with recog's set
        command = developer_cmds.CmdCmdFuncTest
        self.char1.recog.add(self.char3, "Char3 char1")
        self.char2.recog.add(self.char3, "Char3 char2")
        self.char3.recog.add(self.char3, "Char3 char3")
        self.char4.recog.add(self.char3, "Char3 char4")
        self.char5.recog.add(self.char3, "Char3 char5")
        arg = f"send_emote, to person and 2 person = /Target message /target"
        receivers = {
            self.char1: "Char3 char1(#12) and a normal person(#13) message Char3 char1(#12) and a normal person(#13)",
            self.char2: "Char3 char2 and a normal person message Char3 char2 and a normal person",
            self.char3: "A normal person and you message a normal person and you",
            self.char4: "Char3 char4 and you message Char3 char4 and you",
            self.char5: "Char3 char5 and a normal person message Char3 char5 and a normal person",
            self.obj1: "A normal person and a normal person message a normal person and a normal person"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test where recog has an upper case
        command = developer_cmds.CmdCmdFuncTest
        self.char1.recog.add(self.char3, "char3 char1")
        self.char2.recog.add(self.char3, "char3 char2")
        self.char3.recog.add(self.char3, "char3 char3")
        self.char4.recog.add(self.char3, "char3 char4")
        self.char5.recog.add(self.char3, "char3 char5")
        self.char1.recog.add(self.char4, "Char4 char1")
        self.char2.recog.add(self.char4, "Char4 char2")
        self.char3.recog.add(self.char4, "Char4 char3")
        self.char4.recog.add(self.char4, "Char4 char4")
        self.char5.recog.add(self.char4, "Char4 char5")
        arg = f"send_emote, to person and 2 person = /Target message. /Target"
        receivers = {
            self.char1: "Char3 char1(#12) and Char4 char1(#13) message. Char3 char1(#12) and Char4 char1(#13)",
            self.char2: "Char3 char2 and Char4 char2 message. Char3 char2 and Char4 char2",
            self.char3: "Char4 char3 and you message. Char4 char3 and you",
            self.char4: "Char3 char4 and you message. Char3 char4 and you",
            self.char5: "Char3 char5 and Char4 char5 message. Char3 char5 and Char4 char5",
            self.obj1: "A normal person and a normal person message. A normal person and a normal person"
        }
        cmd_result = self.call_multi_receivers(command(), arg, receivers, noansi=False)
        # test the upper switch.
        result = replace_cap("/target test /target test. /target", "/target", "name", upper=True, lower=False)
        self.assertEqual(result, "Name test Name test. Name")
        # test the lower switch.
        result = replace_cap("/target test /target test. /target", "/target", "name", upper=False, lower=True)
        self.assertEqual(result, "name test name test. name")

    def test_gain_exp(self):
        # punch command
        command = developer_cmds.CmdCmdFuncTest
        end_time = time.time() + 3.1
        arg = f"/r gain_exp, char2, cmd_type:unarmed, end_time:{end_time}, skill_name:punch"
        wnt_msg = "gain_exp returned: 3.0"
        self.call(command(), arg, wnt_msg)
        self.assertTrue(self.char1.skills.unarmed.punch_exp > 3)
        self.assertTrue(self.char1.skills.unarmed.punch_exp < 3.5)
        self.char1.skills.unarmed.punch_exp = 0
        # dodge command
        command = developer_cmds.CmdCmdFuncTest
        end_time = time.time() + 3.1
        arg = f"/r gain_exp, char2, cmd_type:evasion, end_time:{end_time}, skill_name:dodge"
        wnt_msg = "gain_exp returned: 3.0"
        self.call(command(), arg, wnt_msg)
        self.assertTrue(self.char1.skills.evasion.dodge_exp > 3)
        self.assertTrue(self.char1.skills.evasion.dodge_exp < 3.5)
        self.char1.skills.evasion.dodge_exp = 0
        # Run the punch command. Not not set a run time.
        command = developer_cmds.CmdMultiCmd
        arg = "= punch char2, complete_cmd_early"
        self.call(command(), arg)
        self.assertTrue(self.char1.skills.unarmed.punch_exp > 0)
        self.char1.skills.unarmed.punch_exp = 0
        # Run the dodge command. Complete early without actually dodging
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge, complete_cmd_early"
        self.call(command(), arg)
        self.assertTrue(self.char1.skills.evasion.dodge_exp == 0)
        self.char1.skills.evasion.dodge_exp = 0
        # test a succesful dodge.
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        self.call(command(), arg, caller=self.char2)
        arg = "= punch char2, complete_cmd_early"
        self.call(command(), arg)
        self.assertTrue(self.char2.skills.evasion.dodge_exp > 0)
        # test message on rank available.
        command = developer_cmds.CmdCmdFuncTest
        self.char1.skills.unarmed.punch_exp = 599
        end_time = time.time() + 3.1
        arg = f"/r gain_exp, char2, cmd_type:unarmed, end_time:{end_time}, skill_name:punch"
        wnt_msg = "You have enough experience with punch to learn rank 2."
        self.call(command(), arg, wnt_msg)
            # should not receive a message after the first one this rank.
        end_time = time.time() + 3.1
        arg = f"/r gain_exp, char2, cmd_type:unarmed, end_time:{end_time}, skill_name:punch"
        wnt_msg = "gain_exp returned: 3.0"
        self.call(command(), arg, wnt_msg)


class TestLearn(UniqueMudCmdTest):
    """verify the successfull learning messages, including the room
    verify learning survives a restart
    """

    def test_no_rank_ready(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= learn"
        wnt_msg = "None of your skills are ready for a rank increase."
        self.call(command(), arg, wnt_msg)

    def test_rank_ready(self):
        self.char1.skills.unarmed.punch_exp = 600
        command = developer_cmds.CmdMultiCmd
        arg = "= learn"
        wnt_msg = "Punch is ready for a new rank.\n" \
                  "It will take 0:30:00 to learn this rank.\n" \
                  "Increase punch with learn punch."
        self.call(command(), arg, wnt_msg)

    def test_skill_point_rank_ready(self):
        self.char1.skills.one_handed.skill_points = 300
        command = developer_cmds.CmdMultiCmd
        arg = "= learn"
        wnt_msg = "Stab is ready for a new rank.\n" \
                  "It will take 0:15:00 to learn this rank.\n" \
                  "Increase stab with learn stab."
        self.call(command(), arg, wnt_msg)

    def test_incorrect_skill_name(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= learn int_fail"
        wnt_msg = "int_fail, is not an increasable skill.|None of your skills are ready for a rank increase."
        self.call(command(), arg, wnt_msg)

    def test_successful_study(self):
        self.char1.skills.unarmed.punch_exp = 600
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch, complete_cmd_early"
        cmd_result = self.call(command(), arg)
        wnt_msg = "^You will be busy for 30 seconds.|You begin to study punch to rank 2."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = "When you complete studing punch, it will take 0:30:00 to learn the new rank."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = "You can not learn another skill during this time. You will be fully functional otherwise."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = "You can not stop learning after you have started. "
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = "If you do not want learning to be locked out for this time use stop before you have completed studing.|"
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You complete studing punch, this rank increase will complete on \d+-\d+-\d+ \d+:\d+:\d+\.|"
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You are no longer busy\.$"
        self.assertRegex(cmd_result, wnt_msg)

    def test_learning_message(self):
        self.char1.skills.unarmed.punch_exp = 600
        self.char1.skills.one_handed.skill_points = 300
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch, complete_cmd_early"
        self.call(command(), arg)
        arg = "= learn"
        cmd_result = self.call(command(), arg)
        wnt_msg = "^Stab is ready for a new rank.\n" \
                  "It will take 0:15:00 to learn this rank.\n" \
                  "Increase stab with learn stab.\n" \
                  r"You are currently learning punch to rank 2\.\n" \
                  r"Learning will complete on \d+-\d+-\d+ \d+:\d+:\d+\.$"
        self.assertRegex(cmd_result, wnt_msg)

    def test_requires_ready(self):
        cmd_set = self.char1.cmdset.get()[0]
        cmd_inst = cmd_set.get('learn')
        cmd_inst.set_instance_attributes()
        self.assertFalse(cmd_inst.requires_ready)
        self.char1.skills.unarmed.punch_exp = 600
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch"
        self.call(command(), arg)
        self.assertTrue(cmd_inst.requires_ready)
        arg = "= complete_cmd_early"
        self.call(command(), arg)
        self.assertFalse(cmd_inst.requires_ready)

    def test_rank_increase(self):
        self.char1.skills.unarmed.punch_exp = 600
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch, complete_cmd_early"
        self.call(command(), arg)
        self.assertEqual(self.char1.skills.unarmed.punch, 1)
        self.task_handler.clock.advance(1801)
        self.assertEqual(self.char1.skills.unarmed.punch, 2)

    def test_learning_dict(self):
        self.char1.skills.unarmed.punch_exp = 600
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch, complete_cmd_early"
        self.call(command(), arg)
        learning_dict = self.char1.learning
        self.assertTrue(isinstance(learning_dict.get('comp_date'), float))
        self.assertTrue(isinstance(learning_dict.get('task_id'), int))
        self.assertTrue(isinstance(learning_dict.get('rank'), int))
        self.assertTrue(isinstance(learning_dict.get('skill_name'), str))
        self.task_handler.clock.advance(1801)
        self.assertFalse(self.char1.learning)

    def test_learn_one_skill_at_a_time(self):
        self.char1.skills.unarmed.punch_exp = 600
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch, complete_cmd_early"
        self.call(command(), arg)
        arg = "= learn punch"
        cmd_result = self.call(command(), arg)
        wnt_msg = r"^You are currently learning punch to rank 2\.\n" \
                  r"Learning will complete on \d+-\d+-\d+ \d+:\d+:\d+\.$"
        self.assertRegex(cmd_result, wnt_msg)

    def test_task(self):
        self.char1.skills.unarmed.punch_exp = 600
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch, complete_cmd_early"
        self.call(command(), arg)
        task_id = self.char1.learning.get('task_id')
        self.assertTrue(self.task_handler.exists(task_id))

    def test_single_skill(self):
        self.char1.skills.unarmed.punch_exp = 600
        self.char1.skills.one_handed.skill_points = 300
        command = developer_cmds.CmdMultiCmd
        arg = "= learn punch?"
        wnt_msg = "Punch is ready for a new rank.\n" \
                  "It will take 0:30:00 to learn this rank.\n" \
                  "Increase punch with learn punch."
        self.call(command(), arg, wnt_msg)


class TestStop(UniqueMudCmdTest):
    """Test the stop command"""

    def test_stop(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= punch char2"
        self.call(command(), arg)
        self.assertTrue(self.char1.nattributes.has('deffered_command'))
        arg = "= stop"
        wnt_msg = "You are no longer busy."
        self.call(command(), arg, wnt_msg)
        self.assertFalse(self.char1.nattributes.has('deffered_command'))

    def test_no_deferred_action(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= stop"
        wnt_msg = 'You are not commited to an action.'
        self.call(command(), arg, wnt_msg)

    def test_unstoppable(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= punch char2"
        self.call(command(), arg)
        deferred_cmd = self.char1.nattributes.get('deffered_command')
        deferred_cmd.unstoppable = True
        arg = "= stop"
        wnt_msg = 'Punch can not be stopped.'
        self.call(command(), arg, wnt_msg)


class TestSkills(UniqueMudCmdTest):

    def test_skills(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= skills"
        cmd_result = self.call(command(), arg)
        wnt_msg = 'Evasion\nskill points: 0\n    skill name     ranks     exp     next rank \n' \
        '    dodge          1         0       600       \n\r\n\n' \
        'Unarmed\nskill points: 0\n    skill name     ranks     exp     next rank \n' \
        '    punch          1         0       600       \n    kick           1         0       600'
        self.assertRegex(cmd_result, wnt_msg)

    def test_single_set(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= skills unarmed"
        cmd_result = self.call(command(), arg)
        wnt_msg = 'Unarmed\nskill points: 0\n    skill name     ranks     exp     next rank \n' \
                  '    punch          1         0       600       \n    kick           1         0       600'
        self.assertRegex(cmd_result, wnt_msg)

    def test_set_with_no_rank_or_sp(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= skills one handed"
        wnt_msg = 'You do not know skills or have skill points in the one handed skill set.'
        self.call(command(), arg, wnt_msg)

    def test_non_existent_set(self):
        command = developer_cmds.CmdMultiCmd
        arg = "= skills fail"
        wnt_msg = 'fail, is not a skill set name.|Skill sets are: '
        cmd_result = self.call(command(), arg, wnt_msg)
        wnt_msg = ", and "
        self.assertRegex(cmd_result, wnt_msg)

    def test_set_with_sp_only(self):
        self.char1.skills.one_handed.skill_points = 150
        command = developer_cmds.CmdMultiCmd
        arg = "= skills one handed"
        wnt_msg = 'One handed|skill points: 150|'
        self.call(command(), arg, wnt_msg)
