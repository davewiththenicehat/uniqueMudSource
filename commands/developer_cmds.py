from commands.command import Command
from evennia import CmdSet


class DeveloperCmdSet(CmdSet):
    def at_cmdset_creation(self):
        """
        The only thing this method should need to do is to add commands to the set.

        Ideally these commands should be locked with Developer permission.

        These commands are intended for unit testing.
        They are also a very good reference of how to make a very basic command
        There is no reason developers could not use them also.
        """
        self.add(CmdDeferCmd)
        self.add(CmdInterruptCmd)
        self.add(CmdTestCmd)
        self.add(CmdStopCmd)
        self.add(CmdStunSelf)
        self.add(CmdStopStun)
        self.add(CmdMultiCmd)
        self.add(CmdCompleteCmdEarly)


class CmdDeferCmd(Command):
    """
    Test deffering the action portion of a command.

    Reason:
        Created while making the Command.defer method.
        It is used to test a deffered command.
        Retained as it is a good reference for future commands.
        Will also be used in unit testing.

    usage:
        defer_cmd
    """
    key = "defer_cmd"
    help_category = "developer"
    status_type = 'busy'
    defer_time = 5
    locks = "cmd:perm(Developer)"

    def func(self):
        defer_successful = self.defer()
        if defer_successful:
            message = f"{self.caller.name} is testing deferring a command."
            self.caller.location.msg_contents(message)

    def deferred_action(self):
        self.caller.msg("Defered command ran successfully.")


class CmdInterruptCmd(Command):
    """
    Test requesting a user to stop their command.

    Reason:
        Created while making the Command.defer method.
        It is used to test a deffered command.
        Retained as it is a good reference for future commands.
        Will also be used in unit testing.

    usage:
    interrupt_cmd <target>
    Ommit arguments to interrupt self, or use self as target.
    """
    key = "interrupt_cmd"
    help_category = "developer"
    locks = "cmd:perm(Developer)"

    def func(self):
        target = None
        stop_success = None
        if self.args:
            target = self.args.lstrip()
            if target:
                target = self.caller.search(target)
        if not target:
            stop_success = self.stop_request(None, None, 'test_cmd')
            if not stop_success:
                self.caller.msg(f'You are not commited to an action.')
        else:
            stop_success = self.stop_request(target, None, 'test_cmd')
            if not stop_success:
                self.caller.msg(f'{target.name} is not commited to an action.')


class CmdStopCmd(Command):
    """
    Test focing a command to stop

    Reason:
        Created while making the Command.defer method.
        It is used to test a deffered command.
        Retained as it is a good reference for future commands.
        Will also be used in unit testing.

    usage:
    stop_cmd <target>
    Ommit arguments to stop a command ran by yourself, or use self as target.
    """
    key = "stop_cmd"
    help_category = "developer"
    locks = "cmd:perm(Developer)"

    def func(self):
        target = None
        if self.args:
            target = self.args.lstrip()
            if target:
                target = self.caller.search(target)
        if target:
            self.stop_forced(target, None, 'test_cmd')
        else:
            self.stop_forced(None, None, 'test_cmd')


class CmdCompleteCmdEarly(Command):
    """
    Complete a deffered command before the time has elasped.

    Reason:
        Unit testing.

    usage:
    complete_cmd_early <target>
    Ommit arguments to stop a command ran by yourself, or use self as target.
    """
    key = "complete_cmd_early"
    help_category = "developer"
    locks = "cmd:perm(Developer)"

    def func(self):
        target = None
        if self.args:
            target = self.args.lstrip()
            if target:
                target = self.caller.search(target)
        if target:
            self.complete_early(target)
        else:
            self.complete_early(self.caller)


class CmdTestCmd(Command):
    """
    Intended to how a message to the caller to show that the command ran successful.
    Will also be used in unit testing.

    Usage:
        Character.execute_cmd('test_cmd')  # within your code
    """
    key = "test_cmd"
    help_category = "developer"
    locks = "cmd:perm(Developer)"

    def func(self):
        self.caller.msg("Test command ran successfully.")


class CmdStunSelf(Command):
    """
    Stuns self to test setting stun status.
    No character can be stunned longer than 10 seconds.

    Reason:
        Created while making the Command.defer method.
        It is used to test a deffered command.
        Retained as it is a good reference for future commands.
        Will also be used in unit testing.

    usage:
        stun_self
    """
    key = "stun_self"
    help_category = "developer"
    locks = "cmd:perm(Developer)"

    def func(self):
        self.caller.stun(3)


class CmdStopStun(Command):
    """
    Removes the stun status from self

    Reason:
        Created while making the Command.defer method.
        It is used to test a deffered command.
        Retained as it is a good reference for future commands.
        Will also be used in unit testing.

    usage:
        stop_stun
    """
    key = "stop_stun"
    help_category = "developer"
    locks = "cmd:perm(Developer)"

    def func(self):
        stop_success = self.caller.status_stop('stunned', "Stunned stopped message successful.", 'test_cmd')
        if not stop_success:
            self.caller.msg('You are not currently stunned.')


class CmdMultiCmd(Command):
    """
    Used to run multiple commands in sequence.

    Reason:
        For unit testing.

    usage:
        multi_cmd = command 1, command 2

    Example: as it would be used in a unit test
        class TestCommands(CommandTest):

            character_typeclass = Character

            def test_cmd_defferal(self):
                # stun locks out busy commands
                command = developer_cmds.CmdMultiCmd
                arg = "= stun_self, defer_cmd"
                wanted_message = "You will be stunned for 3 seconds.|You will be stunned for 3 seconds."
                self.call(command(), arg, wanted_message)
    """
    key = "multi_cmd"
    help_category = "developer"
    locks = "cmd:perm(Developer)"

    def func(self):
        commands = self.rhslist
        for command in commands:
            self.caller.execute_cmd(command)
