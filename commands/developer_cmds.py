from commands.command import Command
from evennia import CmdSet
from world.rules import stats


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
        self.add(CmdViewObj)
        self.add(CmdContrlOther)
        self.add(CmdCmdFuncTest)


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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

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
                self.caller.msg('You are not commited to an action.')
        else:
            stop_success = self.stop_request(target, None, 'test_cmd')
            if not stop_success:
                self.caller.msg(f'{target.usdesc} is not commited to an action.')


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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

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
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

    def func(self):
        commands = self.rhslist
        for command in commands:
            self.caller.execute_cmd(command)


class CmdViewObj(Command):
    """
    Used to view misc information that exists on Objects as basic python attributes.

    Reason:
        Misc testing.
        Unit testing

        Usage:
            view_obj/switches target=view_group_name,attribute_name
            Providing no view_group_name or attribute_name will dump the objects __dict__

    Switches:
        v, to view in veribose mode

    Target:
        Leave the target blank for self: view_obj =attribute_name

    view_group_names:
        'stat_cache' or 'stat cache': to view all stat caches on Character.
    """
    key = "view_obj"
    help_category = "developer"
    locks = "cmd:perm(Developer)"
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

    def view_cache_stat_modifiers(self, target=None):
        if not target:
            target = self.caller
        char_message = 'Character ID: '+str(target.id)+' | '
        stats_dictionary = stats.STAT_MAP_DICT
        for stat_type, long_name in stats_dictionary.items():
            mod_name = stat_type + '_evade_mod'
            self.caller.msg(f'{char_message+mod_name}: {getattr(target, mod_name)}')
            mod_name = stat_type + '_action_mod'
            self.caller.msg(f'{char_message+mod_name}: {getattr(target, mod_name)}')
            mod_name = stat_type + '_action_cost_mod'
            self.caller.msg(f'{char_message+mod_name}: {getattr(target, mod_name)}')
            mod_name = stat_type + '_dmg_mod'
            self.caller.msg(f'{char_message+mod_name}: {getattr(target, mod_name)}')
            mod_name = stat_type + '_restoration_mod'
            self.caller.msg(f'{char_message+mod_name}: {getattr(target, mod_name)}')
        self.caller.msg(f"{char_message}hp_max_mod: {getattr(target, 'hp_max_mod')}")
        self.caller.msg(f"{char_message}endurance_max_mod: {getattr(target, 'endurance_max_mod')}")
        self.caller.msg(f"{char_message}sanity_max_mod: {getattr(target, 'sanity_max_mod')}")
        self.caller.msg(f"{char_message}load_max_mod: {getattr(target, 'load_max_mod')}")
        self.caller.msg(f"{char_message}busy_mod: {getattr(target, 'busy_mod')}")
        self.caller.msg(f"{char_message}stunned_mod: {getattr(target, 'stunned_mod')}")
        self.caller.msg(f"{char_message}purchase_mod: {getattr(target, 'purchase_mod')}")

    def func(self):
        target = self.lhs.strip()
        target = self.caller.search(target, quiet=True)
        if target:
            target = target[0]
        else:
            target = self.caller
        view_list = self.rhslist
        if 'v' in self.switches:
            self.caller.msg(f'target: {target} | view_list: {view_list}')
        for view_type in view_list:
            view_type = view_type.lower()
            if view_type == 'stat_cache' or view_type == 'stat cache':
                self.view_cache_stat_modifiers(target)
            else:
                if hasattr(target, view_type):
                    self.caller.msg(f'{target}.{view_type} == {getattr(target, view_type)}')
                else:
                    self.caller.msg(f'{target.__dict__}')


class CmdContrlOther(Command):
    """
    Used to force another object to commit a command.

    Reason:
        Used to test commands that interact with commands on other objects.
        Will also be used in unit testing.

    usage:
        control_other <target>=command
    """
    key = "control_other"
    help_category = "developer"
    locks = "cmd:perm(Developer)"
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

    def func(self):
        caller = self.caller
        target_name = self.lhs.strip()
        target = caller.search(target_name, quiet=True)
        cmd_list = self.rhslist
        if target:
            target=target[0]
        else:
            caller.msg(f'{target_name} is not here.')
            return
        if 'v' in self.switches:
            caller.msg(f'target: {target} | cmd_list: {cmd_list}')
        for cmd in cmd_list:
            cmd = cmd.lower()
            target.execute_cmd(cmd)


class CmdCmdFuncTest(Command):
    """
    Used to test an individual function in the command module.

    Reason:
        Used to test functions outside commands.
        Will also be used in unit testing.

    usage:
        cmd_func_test <function name>,<target>=<arg1>,<arg2>...
        only <function name> is required
        Can pass 0 or more arguments after =
            CmdCmdFuncTest will attempt to convert arguments to number.
            Any argument that can be turned into an int will be.

        The target of this command is saved as self.target, for the function to use also.
    """
    key = "cmd_func_test"
    help_category = "developer"
    locks = "cmd:perm(Developer)"
    requires_ready = False
    requires_conscious = False  # if true this command requires the caller to be conscious

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.

        If overridden call super().at_init()
        """
        super().at_init()  # uncomment when overridden
        # this is needed for testing function Command.dmg_after_dr
        self.dmg_types = {"ACD": 1, "PRC": 0}  # dictionary of damage types this command can manipulate.

    def func(self):
        caller = self.caller
        func_name, target_name = self.lhslist
        target = None
        if target_name:
            target = caller.search(target_name, quiet=True)
            if target:
                target=target[0]
                self.target = target
            else:
                caller.msg(f'{target_name} is not here.')
                return
        if hasattr(self, func_name): # find this function in the command module
            func_inst = getattr(self, func_name)
            arguments = []
            for argument in self.rhslist:
                # convert strings to ints if they are ints.
                try:
                    int_arg = int(argument)
                    arguments.append(int_arg)
                except ValueError:
                    # if None was passed as an argument turn it into None
                    if argument.strip() == 'None':
                        argument = None
                    arguments.append(argument)
            # Call the function capturing any returns.
            func_return = func_inst(*arguments)
            # show the return to screen if the r switch was used
            if 'r' in self.switches:
                caller.msg(f'{func_name} returned: {func_return}')
        else:
            caller.msg(f'No function {func_name} found.')
