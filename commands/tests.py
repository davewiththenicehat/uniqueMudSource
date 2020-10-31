from evennia.commands.default.tests import CommandTest
from commands import developer_cmds
from commands.combat import evasion, unarmed
from typeclasses.characters import Character


class TestCommands(CommandTest):

    """
        CommandTest.call arguments
        call(cmdobj, args, msg=None, cmdset=None,
            noansi=True, caller=None, receiver=None, cmdstring=None,
            obj=None, inputs=None, raw_string=None,
        ):
    """

    # account_typeclass = DefaultAccount
    # object_typeclass = DefaultObject
    character_typeclass = Character
    # exit_typeclass = DefaultExit
    # room_typeclass = DefaultRoom
    # script_typeclass = DefaultScript


    def test_cmds(self):

    # test deffering commands
        # defer a command and complete it
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, complete_cmd_early"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Defered command ran successfully.|You are no longer busy.|Char allowed you to complete your defer_cmd command early with their complete_cmd_early command."
        self.call(command(), arg, wanted_message)

        # request a deffered command to stop
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd, y"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # you can not fullow up a busy command with another busy command
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, defer_cmd"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|You will be busy for 5 seconds."
        self.call(command(), arg, wanted_message)

        # force a deffered command to stop, a deffered command was left open on 'char' from the test above
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_cmd"
        wanted_message = "You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # request the stop of a deffered command on self when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd"
        wanted_message = "You may want to test_cmd.|You are not commited to an action."
        self.call(command(), arg, wanted_message)

        # complete a command early when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= complete_cmd_early"
        wanted_message = "You are not commited to an action."
        self.call(command(), arg, wanted_message)

        # request the stop of a deffered command on a target that has no deffered command
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd char2"
        wanted_message = "Char2 is not commited to an action."
        self.call(command(), arg, wanted_message)

        # request target to stop a deffered comamnd
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd char, y"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # stun a character and stop it early
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, stop_stun"
        wanted_message = "You will be stunned for 3 seconds.|You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # stun locks out busy commands
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, defer_cmd"
        wanted_message = "You will be stunned for 3 seconds.|You will be stunned for 3 seconds."
        self.call(command(), arg, wanted_message)

        # stop a stun on self when there is no stun
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_stun"
        wanted_message = "You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wanted_message)  # stop the stun above
        wanted_message = "You are not currently stunned."
        self.call(command(), arg, wanted_message)

    # test punch, kick and dodge
        # test punch
        command = developer_cmds.CmdMultiCmd
        arg = "= punch char2, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Char2 Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade \\d+: You punch at Char2 .*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test kick
        command = developer_cmds.CmdMultiCmd
        arg = "= kick char2, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Char2 Char lifts theirs knee up preparing an attack.\nkick \\d+ VS evade \\d+: You kick at Char2 .*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test dodge
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge, control_other char2=punch char, complete_cmd_early char2"
        wanted_message =  "You will be busy for \\d+ seconds.\nYou begin to sway warily.\nFacing Char Char2 pulls theirs hand back preparing an attack.\nYou are no longer busy.\nYou try to dodge the incoming attack.\nevade \\d+ VS punch \\d+: You attempt to evade Char2's punch .*"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
