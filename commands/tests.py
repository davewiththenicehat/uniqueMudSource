from evennia import create_object

from typeclasses.objects import Object
from typeclasses.equipment import clothing
from commands import standard_cmds, developer_cmds
from typeclasses.equipment.wieldable import OneHandedWeapon
from utils.unit_test_resources import UniqueMudCmdTest
from world.rules.stats import STATS


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
        wnt_msg = "You pick up Obj\."
        cmd_result = self.call(command(), arg, caller=self.char1)
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
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar puts on test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
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
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test shirt.\nChar puts on test shirt.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # get a second object
        arg = "= get Obj2, complete_cmd_early"
        wnt_msg = "You pick up Obj2\."
        cmd_result = self.call(command(), arg, caller=self.char1)
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
        wnt_msg = "You will be busy for 5 seconds.|Char is testing deferring a command.|Defered command ran successfully.|You are no longer busy.|Char allowed you to complete your defer_cmd command early with their complete_cmd_early command."
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
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_cmd"
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
        wnt_msg = "Defered command ran successfully.|You are no longer busy.|Char allowed you to complete your defer_cmd command early with their complete_cmd_early command."
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
        wnt_msg = 'You can not punch out.'
        cmd_result = self.call(command(), arg, wnt_msg)
        # test targeting a targetable exit
        self.exit.targetable = True
        command = developer_cmds.CmdMultiCmd
        arg = "= punch out, complete_cmd_early"
        wnt_msg = "You will be busy for \\d+ seconds.\nFacing out Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade 5: You punch at out"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        self.exit.targetable = False
        # test attacking a basic Object, defense should be 5
        # test a targeted command that has a stop_request against an object
        # to make certain the stop request to an object causes no issues
        command = developer_cmds.CmdMultiCmd
        arg = "= kick Obj, complete_cmd_early"
        wnt_msg = "You will be busy for \\d+ seconds.\nFacing Obj Char lifts theirs knee up preparing an attack.\nkick \\d+ VS evade 5: You kick at Obj"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
        # test a target leaving melee range
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char2, control_other Char2=out, complete_cmd_early"
        wnt_msg = "You can no longer reach Char2\\."
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
        wnt_msg = r'You say to object two, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain saying to the first object works after saying to the second
        # this makes certain the Command.target is not a global variable
        arg = 'to object "test message'
        wnt_msg = r'You say to object one, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # add unit test for drop after get has been updated to use UM targetting system.
        # test for multiple targets using &
        command = standard_cmds.CmdSay
        arg = 'to object & 2 object "test message'
        wnt_msg = r'You say to object one and object two, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test for multiple targets using " and "
        command = standard_cmds.CmdSay
        arg = 'to object and 2 object "test message'
        wnt_msg = r'You say to object one and object two, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)

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
        wnt_msg = "You pick up Obj\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj1))
        # test getting an object already in possession
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj"
        wnt_msg = "^You are already carrying Obj\.$"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
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
        wnt_msg = "You put Obj2 into Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You begin to put Obj2 into Obj\."
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
        wnt_msg = r"You reach into Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You get Obj2 from Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # test putting an object into a non container object.
        # this does NOT use self.sl_split
        arg = "= put Obj2 in Obj"
        wnt_msg = '^Obj is not a container\.$'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # test CmdPut the error catching in deffered action
        self.obj1.container = True
        arg = "= put Obj2 in Obj"
        wnt_msg = "You begin to put Obj2 into Obj\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        self.obj1.container = False
        arg = "= complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1)
        wnt_msg = r"Obj2 can not be put into Obj\.\nError message: CmdPut: caller: #6, target: #5 container: #4\. target\.move_to returned false in Command\.deferred_action\.\r\nThis has NOT been logged\. System detects you are a developer\.\nYou are no longer busy\."
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # drop the first object
        arg = "= drop Obj"
        wnt_msg = "You drop Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj1))
        # try putting obj2 into a container that does not exist
        arg = "= put Obj2 in fake container"
        wnt_msg = "^You did not find fake container among your possesions or near by\.$"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # test help message for put when no container is supplied.
        arg = "= put Obj2"
        wnt_msg = r"^You must specify a container to place Obj2 into.\r\nFor a full help use: Help put$"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # put obj2 in obj1 while obj1 is on the ground
        self.obj1.container = True
        arg = "= put Obj2 in Obj, complete_cmd_early"
        wnt_msg = "You put Obj2 into Obj\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj2))
        self.obj1.container = False
        # get obj2 from obj1 while obj1 is on the ground
        # tests self.sl_split
        arg = "= get Obj2 from Obj, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1)
        wnt_msg = r"You reach into Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = r"You get Obj2 from Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        self.assertTrue(self.char1.is_holding(self.obj2))
        # drop the second object
        arg = "= drop Obj2"
        wnt_msg = "You drop Obj2"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj2))
    # make certain room message is correct
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early"
        wnt_msg = "Char picks up Obj\."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # get second object
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj2, complete_cmd_early"
        wnt_msg = "Char picks up Obj2\."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # put object 2 in object 1
        self.obj1.container = True
        arg = "= put Obj2 in Obj, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        wnt_msg = "Char begins to put Obj2 into Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = "Char puts Obj2 into Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        self.obj1.container = False
        # get object 2 from object 1
        arg = "= get Obj2 from Obj, complete_cmd_early"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        wnt_msg = "Char gets Obj2 from Obj\."
        self.assertRegex(cmd_result, wnt_msg)
        wnt_msg = "Char reaches into Obj\."
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
        wnt_msg = "Char drops Obj\."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
        # drop object 2
        arg = "= drop Obj2, complete_cmd_early"
        wnt_msg = "Char drops Obj2\."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wnt_msg)
    # test get command failures
        # get an object from a location that does not exist
        # test self.target_required when self.sl_split found
        arg = "= get Obj from fake location"
        wnt_msg = "You could not find fake location to search for Obj."
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test getting fake object from a location that exists.
        # test target_required when sl_split found
        arg = "= get fake item from Obj"
        wnt_msg = "You could not find fake item in Obj."
        self.call(command(), arg, wnt_msg, caller=self.char1)
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
        wnt_msg = 'You will be busy for \\d+ seconds.\nFacing Char2 Char raises a sword preparing an attack.\nstab \\d+ VS evade \\d+: You stab at Char2.*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)
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
        # test clothing commands
        self.test_helmet.location = self.char1
        # give the helmet an armor rating
        self.test_helmet.dr.PRC = 2
        self.test_helmet.dr.ACD = 3
        self.assertEqual(self.test_helmet.attributes.get('dr_PRC'), 2)
        self.assertEqual(self.test_helmet.dr.PRC, 2)
        # Test wear with no arguments.
        command = developer_cmds.CmdMultiCmd
        arg = "= wear"
        wnt_msg = "What would you like to wear?|If you need help try help wear."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # Test wearing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= get hat, complete_cmd_early"
        wnt_msg = "You pick up test hat"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar puts on test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain the hat is no longer in hand
        self.assertFalse(self.char1.is_holding(self.test_hat))
        # test tring to wear an item that is not clothing, also tests target_inherits_from
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early"
        wnt_msg = "You pick up Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # make certain hands are occupied with the object picked up
        self.assertTrue(self.char1.is_holding(self.obj1))
        arg = "= wear Obj"
        wnt_msg = "You can only wear clothing and armor."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        arg = "= drop Obj"
        wnt_msg = "You drop Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertFalse(self.char1.is_holding(self.obj1))
        # test removing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= remove hat, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar removes test hat.\nYou are no longer busy.\nChar allowed you to complete your remove command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # Put the hat back on to test covering
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar puts on test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # Test wearing a peace of armor
        command = developer_cmds.CmdMultiCmd
        arg = "= wear helmet, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test helmet.\nChar puts on test helmet, covering test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
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
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test clothing covering.
        # Make a test shirt
        test_undershirt = create_object(clothing.Clothing, key="test undershirt")
        test_undershirt.db.clothing_type = "undershirt"
        test_undershirt.location = self.char1
        # Test wearing the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear undershirt, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test undershirt.\nChar puts on test undershirt.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # get the test shirt
        command = developer_cmds.CmdMultiCmd
        arg = "= get shirt, complete_cmd_early"
        wnt_msg = "You pick up test shirt."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # Test wearing the shirt covering the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear shirt, complete_cmd_early"
        wnt_msg = "You will be busy for 1 second.\nYou begin to put on test shirt.\nChar puts on test shirt, covering test undershirt.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        self.assertEqual(test_undershirt.db.covered_by, self.test_shirt)
        #verify that the helmet's armor rating has been cached in the wearer
        self.assertEqual(self.char1.body.head.dr.PRC, 2)
        self.assertEqual(self.char1.body.head.dr.ACD, 3)
        self.assertEqual(self.char1.body.head.dr.BLG, 0)
        # test dropping a worn item
        arg = "= drop shirt"
        wnt_msg = 'You must remove test shirt to drop it.\r\nTry command remove test shirt to remove it.'
        self.call(command(), arg, wnt_msg, caller=self.char1)

    def test_dmg(self):
        """
        Test damage in commands.
        Command.dmg_after_dr method
        """
        # test method damage after damage reduction
        # get armor on
        self.test_helmet.location = self.char1
        # give the helmet an armor rating
        self.test_helmet.dr.PRC = 2
        self.test_helmet.dr.ACD = 3
        self.assertEqual(self.test_helmet.attributes.get('dr_PRC'), 2)
        self.assertEqual(self.test_helmet.dr.PRC, 2)
        command = developer_cmds.CmdMultiCmd
        # put the armor on
        arg = "= wear helmet, complete_cmd_early"
        wnt_msg = "Char puts on test helmet"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
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
        self.call(command(), '= drop sword', 'You drop a sword.')
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
        for stat in STATS:
            if stat != 'STR':
                stat_inst = getattr(self.char1, stat)
                if stat_inst:
                    old_stat_value =stat_inst.get()
                    stat_inst.set(50)
                    self.char1.cache_stat_modifiers()
                    arg = f"/r dmg_after_dr, char, cmd_type:unarmed, dmg_max:1, dmg_mod_stat:{stat} = None, True, chest"
                    wnt_msg = r"dmg_after_dr returned: 1"
                    self.call(command(), arg, wnt_msg)
                    stat_inst.set(old_stat_value)
                else:
                    raise AssertionError(f"self.char1 has no stat {stat}.")

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
        wnt_msg = r"You will be busy for \d+ second.|You move to sit down.|You sit down.|You are no longer busy.|Char allowed you to complete your sit command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
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
        wnt_msg = "You are already sitting."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # stand up
        command = developer_cmds.CmdMultiCmd
        arg = "= stand, complete_cmd_early"
        wnt_msg = r"You will be busy for \d+ seconds.|You move to stand up.|You stand up.|You are no longer busy.|Char allowed you to complete your stand command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
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
        wnt_msg = "You are already standing."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # lay down
        command = developer_cmds.CmdMultiCmd
        arg = "= lay, complete_cmd_early"
        wnt_msg = r"You will be busy for \d+ second.|You move to lay down.|You lay down.|You are no longer busy.|Char allowed you to complete your lay command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
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
        wnt_msg = "You are already laying."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # a prone Character can not move.
        command = developer_cmds.CmdMultiCmd
        arg = "= out"
        wnt_msg = "You must stand up first."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        # stand both characters up
        command = developer_cmds.CmdMultiCmd
        arg = "= stand, complete_cmd_early"
        wnt_msg = "You will be busy for 3 seconds.|You move to stand up.|You stand up.|You are no longer busy.|Char allowed you to complete your stand command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, wnt_msg, caller=self.char1)
        self.char2.position = 'standing'
        self.assertEqual(self.char2.position, 'standing')

    def test_cmds(self):
    # test punch, kick and dodge
        # test punch
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char2, complete_cmd_early"
        wnt_msg = 'You will be busy for \\d+ seconds.\nFacing Char2 Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade \\d+: You punch at Char2.*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)

        # test kick
        command = developer_cmds.CmdMultiCmd
        arg = "= kick Char2, complete_cmd_early"
        wnt_msg = 'You will be busy for \\d+ seconds.\nFacing Char2 Char lifts theirs knee up preparing an attack.\nkick \\d+ VS evade \\d+: You kick at Char2'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)

        # test dodge
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge, control_other Char2=punch Char, complete_cmd_early Char2"
        wnt_msg = r"You will be busy for \d+ seconds.\nYou begin to sway warily.\nFacing Char Char2 pulls theirs hand back preparing an attack.\nYou are no longer busy.\nYou try to dodge the incoming attack.\nevade \d+ VS punch \d+: Char2 punches at you with their fist "
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)

        # test method get_body_part
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, char2"
        wnt_msg = r"get_body_part returned: False"
        cmd_result = self.call(command(), arg)
        self.assertFalse(cmd_result == wnt_msg)
        # now test an object with no body parts
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, obj"
        wnt_msg = r"^get_body_part returned: False"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)

        # test permision lock down for pose, sdesc and mask
        # test commands on a character without the permission
        for cmd in ('mask', 'sdesc', 'pose'):
            command = developer_cmds.CmdMultiCmd
            arg = f"= {cmd}"
            wnt_msg = f"Command '{cmd}' is not available."
            cmd_result = self.call(command(), arg, caller=self.char2)
            self.assertRegex(cmd_result, wnt_msg)
        # on on a character with permission
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

        # test rpsytem commands
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
        wnt_msg = r'You say to Char2, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # test saying at another Character
        command = standard_cmds.CmdSay
        arg = 'at char2 "test message'
        wnt_msg = r'You say at Char2, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wnt_msg)
        # Test your name is replace with You when you are spoken to
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to char "test message'
        wnt_msg = r'Char2 says to you, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # make certain say to replaces targets message with name
        # with multiple targets
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to char and obj "test message'
        wnt_msg = r'Char2 says to Obj and you, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test seeing a say that does not target you.
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to obj2 and obj "test message'
        wnt_msg = r'Char2 says to Obj2 and Obj, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        arg = '=control_other char2=say at obj2 and obj "test message'
        wnt_msg = r'Char2 says at Obj2 and Obj, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)

        # Test whisper
        # say
        # test saying to another Character
        command = developer_cmds.CmdMultiCmd
        arg = '=whisper to char2 "test message'
        wnt_msg = 'You whisper to Char2, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test saying at another Character
        command = developer_cmds.CmdMultiCmd
        arg = '=whisper at char2 "test message'
        wnt_msg = 'You whisper at Char2, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # verify say echos to room properly
        command = developer_cmds.CmdMultiCmd
        arg = '= control_other Char2=whisper to obj "test message'
        wnt_msg = 'Char2 whispers something to Obj.'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # Test your name is replace with You when you are whispered to
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to char "test message'
        wnt_msg = r'Char2 whispers to you, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # make certain whisper to replaces targets message with name
        # with multiple targets
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to char and obj "test message'
        wnt_msg = r'Char2 whispers to Obj and you, "test message"'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        # test seeing a multi target whisper that does not target you.
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to obj2 and obj "test message'
        wnt_msg = r'Char2 whispers something to Obj2 and Obj.'
        self.call(command(), arg, wnt_msg, caller=self.char1)
        arg = '=control_other char2=whisper at obj2 and obj "test message'
        wnt_msg = r'Char2 whispers something at Obj2 and Obj.'
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

        # test the statistics command
        command = developer_cmds.CmdMultiCmd
        arg = "= stat"
        wnt_msg = "Statistics for: Char"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wnt_msg)

        # make certain commands have been taking a cost.
        self.assertTrue(self.char1.END < 100)
