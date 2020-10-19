"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia import Command as BaseCommand
from world import status_functions
import time
from evennia import utils


class Command(BaseCommand):
    """
    Note that Evennia's default commands inherits from
    MuxCommand instead.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    UniqueMud:

    Command attributes
        status_type = 'busy'  # Character status type used to track the command
        defer_time = 3
    Methods:
        All methods are fully documented in their docstrings.
        defer(int or float), defer the action of a command by calling Command.deferred_action after the number of seconds passed to defer
        stop_request(self, target, stop_message, stop_cmd), request a Character to stop a deffered command early
        stop_forced(self, target, stop_message, stop_cmd, status_type), force a character to stop a deffered command early
        complete_early(self, target, stop_message), make a Character to complete a deffered command early
    """

    # -------------------------------------------------------------
    #
    # The default commands inherit from
    #
    #   evennia.commands.default.muxcommand.MuxCommand.
    #
    # If you want to make sweeping changes to default commands you can
    # uncomment this copy of the MuxCommand parent and add
    #
    #   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
    #
    # to your settings file. Be warned that the default commands expect
    # the functionality implemented in the parse() method, so be
    # careful with what you change.
    #
    # -------------------------------------------------------------

    # from evennia.utils import utils
    #
    #
    # class MuxCommand(Command):
    #     """
    #     This sets up the basis for a MUX command. The idea
    #     is that most other Mux-related commands should just
    #     inherit from this and don't have to implement much
    #     parsing of their own unless they do something particularly
    #     advanced.
    #
    #     Note that the class's __doc__ string (this text) is
    #     used by Evennia to create the automatic help entry for
    #     the command, so make sure to document consistently here.
    #     """
    #     def has_perm(self, srcobj):
    #         """
    #         This is called by the cmdhandler to determine
    #         if srcobj is allowed to execute this command.
    #         We just show it here for completeness - we
    #         are satisfied using the default check in Command.
    #         """
    #         return super().has_perm(srcobj)
    #
    #     def at_pre_cmd(self):
    #         """
    #         This hook is called before self.parse() on all commands
    #         """
    #         pass
    #
    #     def at_post_cmd(self):
    #         """
    #         This hook is called after the command has finished executing
    #         (after self.func()).
    #         """
    #         pass
    #
    def parse(self):
        """
        This method is called by the cmdhandler once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from self.func() (see below)

        The following variables are available for our use when entering this
        method (from the command definition, and assigned on the fly by the
        cmdhandler):
           self.key - the name of this command ('look')
           self.aliases - the aliases of this cmd ('l')
           self.permissions - permission string for this command
           self.help_category - overall category of command

           self.caller - the object calling this command
           self.cmdstring - the actual command name used to call this
                            (this allows you to know which alias was used,
                             for example)
           self.args - the raw input; everything following self.cmdstring.
           self.cmdset - the cmdset from which this command was picked. Not
                         often used (useful for commands like 'help' or to
                         list all available commands etc)
           self.obj - the object on which this command was defined. It is often
                         the same as self.caller.

        A MUX command has the following possible syntax:

          name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]

        The 'name[ with several words]' part is already dealt with by the
        cmdhandler at this point, and stored in self.cmdname (we don't use
        it here). The rest of the command is stored in self.args, which can
        start with the switch indicator /.

        This parser breaks self.args into its constituents and stores them in the
        following variables:
          self.switches = [list of /switches (without the /)]
          self.raw = This is the raw argument input, including switches
          self.args = This is re-defined to be everything *except* the switches
          self.lhs = Everything to the left of = (lhs:'left-hand side'). If
                     no = is found, this is identical to self.args.
          self.rhs: Everything to the right of = (rhs:'right-hand side').
                    If no '=' is found, this is None.
          self.lhslist - [self.lhs split into a list by comma]
          self.rhslist - [list of self.rhs split into a list by comma]
          self.arglist = [list of space-separated args (stripped, including '=' if it exists)]

          All args and list members are stripped of excess whitespace around the
          strings, but case is preserved.
        """
        raw = self.args
        args = raw.strip()
        # split out switches
        switches = []
        if args and len(args) > 1 and args[0] == "/":
            # we have a switch, or a set of switches. These end with a space.
            switches = args[1:].split(None, 1)
            if len(switches) > 1:
                switches, args = switches
                switches = switches.split('/')
            else:
                args = ""
                switches = switches[0].split('/')
        arglist = [arg.strip() for arg in args.split()]
        # check for arg1, arg2, ... = argA, argB, ... constructs
        lhs, rhs = args, None
        lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
        if args and '=' in args:
            lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
            lhslist = [arg.strip() for arg in lhs.split(',')]
            rhslist = [arg.strip() for arg in rhs.split(',')]
        # save to object properties:
        self.raw = raw
        self.switches = switches
        self.args = args.strip()
        self.arglist = arglist
        self.lhs = lhs
        self.lhslist = lhslist
        self.rhs = rhs
        self.rhslist = rhslist
        # if the class has the account_caller property set on itself, we make
        # sure that self.caller is always the account if possible. We also create
        # a special property "character" for the puppeted object, if any. This
        # is convenient for commands defined on the Account only.
        if hasattr(self, "account_caller") and self.account_caller:
            if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
                # caller is an Object/Character
                self.character = self.caller
                self.caller = self.caller.account
            elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
                # caller was already an Account
                self.character = self.caller.get_puppet(self.session)
            else:
                self.character = None

    def defer(self, defer_time=3, status_type='busy'):
        """
        Defer or delay the action of a command.
        By calling Command.deferred_action when the defferal time has completed.
        Returns True if the command was successfully deffered.
            Likely you will not need the returned boolean.

        Arguments:
            position 1, time in seconds to defer the action of a command
            position 2, type of defer that is occuring
                currently suported: 'busy'

        Usage:
            self.defer(defer_time=int, status_type=str)
            Call withing the func method of a Command instance.
            When the defer time has completed the deferred_action method will run

        Defaults:
            defer_time == 3
            status_type == 'busy'

        Example:
            # from withing the func method of a Command
            self.defer(6)  # defer a command for 6 seconds
        Full Example:
            class Cmd(Command):
                key = "cmd"
                help_category = "catergory"
                status_type = 'busy'
                defer_time = 3

                def func(self):
                    defer_successful = self.defer()
                    if defer_successful:
                        message = f"{self.caller.name} is testing deferring a command."
                        self.caller.location.msg_contents(message)

                def deferred_action(self):
                    self.caller.msg("Defered command ran successfully.")
        """
        if self.caller.ready():
            try:
                if self.defer_time:
                    defer_time = self.defer_time
            except AttributeError:
                pass
            try:
                if self.status_type:
                    status_type = self.status_type
            except AttributeError:
                pass
            return status_functions.status_delay_set(self.caller, self,
                                                     defer_time, status_type)

    def stop_request(self, target=None, stop_message=None, stop_cmd=None):
        """
        Request for a player to stop an action.
        This has a parent function in Character.status_stop_request.
        stop_request will verify that the target has a deffered command.
        If stop_cmd was provided and there is no deffered command.
            stop_request will suggest the stop_cmd to the target.
        Returns True if the command was successfully stopped.

        Arguments:
            target=Character, target of the stop request
                Default: caller.self
            stop_message=str, message shown to target.
                Default: f'Stop your {target.ndb.deffered_command.key} command?'
            stop_cmd=str, command to run if the stop request is done.
                Default: None
                Example: 'look'

        Reason:
            Adds a command stop request at command level.

        Useage:
            If not calling on self:
                call within Command.func or Command.deffered_action methods
                self.stop_request(target, stop_message, stop_cmd)
            If calling on self
                NOTE: recommend using Character.status_stop_request over this strategy
                Character.ndb.deffered_command.stop_request()  # to call off a deffered command
                The above method is still useable if the command does not use the Character.ready() method

        Limitations:
            Is NOT compatible with settings.MULTISESSION_MODE = 3
        """
        if not target:
            target = self.caller
        return target.status_stop_request(stop_message, stop_cmd)

    def stop_forced(self, target=None, stop_message=None, stop_cmd=None, status_type='busy'):
        """
        Forcibly stop a Characters deffered command or current status
        Has a sister method in Character.status_stop
        Supports:
            Sending a custom message
            Following the forcibly stopped command with a different one.

        Arguments:
            target=Character, the target of the forced stop
                Default: self.caller
            stop_message=str, a message to show the target.
                Default: f'{self.caller.name} stopped your {target.ndb.deffered_command.key} command with {self_pronoun} {self.key}.'
            stop_cmd=str: a command to run when the deffered command is stopped.
                Default: None
                Example: 'look'
            status_type=str, status type to stop
                default: 'busy'

        Example:
            commands.developer_cmdsets.CmdStopCmd
        """
        #set the target of the forced stop
        if not target:
            target = self.caller
        # if the target has a command deffered
        if target.nattributes.has('deffered_command'):
            if not stop_message:  # if none was provided make a message
                self_pronoun = self.caller.get_pronoun('|p')
                stop_message = f'{self.caller.name} stopped your {target.ndb.deffered_command.key} command with {self_pronoun} {self.key}.'
            status_functions.status_force_stop(target, stop_message, stop_cmd, status_type)
        else:
            self.caller.msg(f'{target.name} is not commited to an action.')

    def complete_early(self, target=None, stop_message=None):
        """
        Complete a deffered complete before the completion time has passed
        Returns True if the early completion was successful.
        Displays a f'{target.name} is not commited to an action.' message
            if the command could not be completed early.

        Supports:
            Sending a custom message
            Target other than self.caller

        Arguments:
            target=Character, a Character to complete a command early
            stop_message=msg, a message to send to the target

        Example:
            From within a commands func method
            if target:
                self.complete_early(target)
            else:
                self.complete_early(self.caller)

            Example in commands.developer_cmdsets.CmdCompleteCmdEarly
        """
        #set the target of the forced stop
        stopped_succesfully = None
        if not target:
            target = self.caller
        if target.nattributes.has('deffered_command'):
            if not stop_message:  # if none was provided make a message
                self_pronoun = self.caller.get_pronoun('|p')
                stop_message = f'{self.caller.name} allowed you to complete your {target.ndb.deffered_command.key} command early with {self_pronoun} {self.key} command.'
            stopped_succesfully = status_functions.status_delay_stop(target, 'busy', True)
            target.msg(stop_message)
        else:
            if target == self.caller:
                self.caller.msg(f'You are not commited to an action.')
            else:
                self.caller.msg(f'{target.name} is not commited to an action.')
        return stopped_succesfully
