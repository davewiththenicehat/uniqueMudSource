"""
Commands

Commands describe the input the account can do to the game.

"""

import re
from evennia import default_cmds
from world import status_functions
from evennia import utils
from evennia.utils.logger import log_info
from world.rules import damage, actions, body
from utils.um_utils import error_report, highlighter


class Command(default_cmds.MuxCommand):
    """
    Note that Evennia's default commands inherits from
    MuxCommand instead.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): has been overridden in UM, and if not overridden will defer
            the action of a command to Command.deferred_action().
            Full notes below.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

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

    Optional variables to aid in parsing, if set:
      self.switch_options  - (tuple of valid /switches expected by this
                              command (without the /))
      self.rhs_split       - Alternate string delimiter or tuple of strings
                             to separate left/right hand sides. tuple form
                             gives priority split to first string delimiter.

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

    UniqueMud:
        To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.
            If your command does not defer an action, override Command.func
        To provide UM targeting system to Command.func, parse has been overridden and cleared.
        parse is called manually in Command.at_pre_cmd via super().parse()

    Command attributes
        status_type = 'busy'  # Character status type used to track the command
        defer_time = 3  # time is seconds for the command to wait before running action of command
        evade_mod_stat = 'AGI'  # stat used to evade this command
        action_mod_stat = 'OBS'  # stat used to modify this command
        cost_stat='END'  # stat this command will use for the action's cost
        cost_level='low' #  level this action should cost. Acceptable levels: 'low', 'mid', 'high' or an integer
            low, nearly free actions like walking
            mid, is for easy but exerting actions like punch.
            high, is for actions that require a lot of energy.
            If a number is used for cost_level that number is used as the base cost for the command.
        desc = None  # a present tense description for the action of this command. IE: "kicks"
            If None when self.func is called, it will give assigned self.key
        caller_weapon = None  # weapon name that will show up in Command.combat_action's automated messages
            Will be automatically filled in Command.func when a Character weapon system is developed.
        roll_max = 50  # max number this command can roll to succeed
        dmg_max = 4  # the maximum damage this command can cause
        cmd_type = False  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
        begins_to_or_at = False  # becomes string "to" or "at" if the commands arguments starts with "to " or "at "
            collected in Command.parse
        target = None  # collected in Command.at_pre_cmd if the command has a target
            Over ride after Command.at_pre_cmd, or your self.target will be replaced
        targets = ()  # multiple instances of targets, when multiple are supplied
            collected in Command.at_pre_cmd if the command starts with "to " or "at "
            If any targets are found, Command.target is always the first
                instance found in commands.targets
            If only one good target is found self.targets is an empty tuple
            Over ride after Command.at_pre_cmd, or your self.targets will be
                replaced after Commnad.at_pre_cmd
        can_not_target_self = False  # if True this command will end with a message if the Character targets themself
            Failure message is handled automatically.
        target_inherits_from = False  # a tuple, position 0 string of a class type, position 1 is a string to show on mismatch
            example: target_inherits_from = ("typeclasses.equipment.clothing.Clothing", 'clothing and armor')
            Failure message is handled automatically.
        target_in_hand = False  # if True the target of the command must be in the Characters hand to complete successfully
        search_caller_only = False  # if True the command will only search the caller for targets
            Failure message is handled automatically.
        requires_ready = True  # if true this command requires the ready status before it can be used.
            deferal commands still require ready to defer, even is requires_ready is false.
            Failure message is handled automatically.
        requires_conscious = True  # if true this command requires the caller to be conscious before it can be used
            Failure message is handled automatically.
        dmg_types = None  # tuple or list of damage types this command can manupulate
            list of types is in world.rules.damage.TYPES
            dmg_types = ('BLG') is not a tuple it is a string. dmg_types = ('BLG',), will return a tuple
        caller_message = None  # text to message the caller. Will not call automatically, here to pass between Command functions
        target_message = None  # text to message the target. Will not call automatically, here to pass between Command functions
        room_message = None  # text to message the room. Will not call automatically, here to pass between Command functions
        log = False  # set to true to info logging should be enabled.
            Error and warning messages are always enabled.

    Methods:
        All methods are fully documented in their docstrings.
        func, To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.
        defer(int or float), defer the action of a command by calling Command.deferred_action after the number of seconds passed to defer
        Command.deferred_action(), override to commit the action of a command to a later time.
        start_message, Displays a message after a command has been successfully deffered.
        stop_request(self, target, stop_message, stop_cmd), request a Character to stop a deffered command early
        stop_forced(self, target, stop_message, stop_cmd, status_type), force a character to stop a deffered command early
        complete_early(self, target, stop_message), make a Character to complete a deffered command early
        successful(success=True), records if a command was successful
        target_out_of_melee(), returns true if the commands target is out of melee range.
        act_vs_msg(action_result, evade_result), Returns two strings to display at the start of an actions message.
        get_body_part(target, no_understore), returns the name of a body part on target
        dmg_after_dr(dmg_dealt=None, body_part_name=None), Returns damage dealt after damage reduction.
        combat_action(action_mod=None, caller_msg=None, target_msg=None, room_msg=None, log=None),
            A command method intended to be a used to easily facilitate basic combat actions.
    """
    status_type = 'busy'  # Character status type used to track the command
    defer_time = 3  # time is seconds for the command to wait before running action of command
    evade_mod_stat = 'AGI'  # stat used to evade this command
    action_mod_stat = 'OBS'  # stat used to modify this command
    roll_max = 50  # max number this command can roll to succeed
    dmg_max = 4  # the maximum damage this command can cause
    dmg_mod_stat = 'STR'  # the stat that will modifier damage this command manipulates
    target_required = False  # if True and the command has no target, Command.func will stop execution and message the player
    can_not_target_self = False  # if True this command will end with a message if the Character targets themself
    cmd_type = False  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
    target_inherits_from = False  # a tuple, position 0 string of a class type, position 1 is a string to show on mismatch
    target_in_hand = False  # if True the target of the command must be in the Characters hand to complete successfully
    search_caller_only = False  # if True the command will only search the caller for targets
    dmg_types = None  # tuple of list or damage types this command can manupulate
    caller_message = None  # text to message the caller. Will not call automatically, here to pass between Command functions
    target_message = None  # text to message the target. Will not call automatically, here to pass between Command functions
    room_message = None  # text to message the room. Will not call automatically, here to pass between Command functions
    caller_weapon = None  # weapon name that will show up in Command.combat_action's automated messages
    desc = None  # a present tense description for the action of this command. IE: "kicks"
    requires_ready = True  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer
    requires_conscious = True  # if true this command requires the caller to be conscious
    cost_stat = 'END'  # stat this command will use for the action's cost
    cost_level = None  # level this action should cost. Acceptable levels: 'low', 'mid', 'high'
    log = False  # set to true to info logging should be enabled. Error and warning messages are always enabled.
    # do not decare these attributes globally. Global attributes will be kept between each command run for a player
    # begins_to_or_at = False  # becomes string "to" or "at" if the commands arguments starts with "to " or "at "
    # target  # the object target of this Command
    # targets = ()  # collected in Command.at_pre_cmd if the command starts with "to " or "at "

    def parse(self):
        """
        parse has been overridden. It is manually called in self.at_pre_cmd
        To allow
            easy support of stopping the command when conditions are not met
            make commands that do not defer work off the UM target system
        """

    def func(self):
        """
        To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.

        UniqueMud:
            UniqueMud's func will:
                defer the action of the command.
                call Command.start_message if the command deffered successfully.
            If your command does not defer an action, override Command.func
            It is possible to use this method within your overidden one with:
                super().self.func()
        """
        # defer the command
        defer_successful = self.defer()
        # show a message to player that their command is waiting
        if defer_successful:
            self.start_message()

    def at_pre_cmd(self):
        """
        Important
            This command calls super().parse, because self.parse has been overritten to be blank.
            This is done to provice UM targeting system to self.func
                Allowing for it to be easily overriten

        Attributes:
            self.target, is added if the command supplied a target.
            self.targets, is added if the command is supplied multipe targets.

        stops execution of a Command if a Character does not meet the commands status requirements.
            self.requires_ready and self.requires_conscious
        finds and store a reference of the Object the command is targetting as self.target
            Also adds support for easy targeting of simular objects.
            "punch 2 droid", rather than "punch 2-droid full name"
        stops the command if targeting self an self.can_not_target_self is True
        stops the commnad if the targets self.targetable is False
        sets the commands self.desc to self.key if desc was not set manually

        Notes:
            if a command starts with "to " or "at ".
                The name of the target to search for will be collected after those starting strings.
            Evennia note: at_pre_cmd(): If this returns anything truthy, execution is aborted.
            Behavior note: returning anything stops the exection of the command.
        """
        # stop the command if a status requirement is not met.
        caller = self.caller
        if self.requires_ready:
            caller_ready = caller.ready()
            if not caller_ready:
                return True
        elif self.requires_conscious:
            if caller.condition.unconscious:
                caller.msg("You can not do that while unconscious.", force_on_unconscious=True)
                return True
            elif caller.condition.dead:
                caller.msg("You can not do that while dead.", force=True)
                return True
        # give an action description if none was provided
        if not self.desc:
            self.desc = self.key
        # self.parse was overriden to provide UM targeting system to commands that use only self.func
        # it has to be manually called now
        super().parse()
        # find the name and if provided number of the target
        caller = self.caller
        lhs = self.lhs.strip()
        args_lower = self.args.lower()
        targets = list()
        self.targets = targets  # Set a default self.targets as blank
        self.target = None  # set default target to None
        self.begins_to_or_at = False  # set a default value for begins_to_or_at
        if args_lower.startswith('to ') or args_lower.startswith('at '):
            # collect the name(s) after to or at
            target_string = self.lhs[3:]
            # collect if this string starts with "to" or "at"
            self.begins_to_or_at = args_lower[:2]
            # get a list of names to search for
            target_names = re.split(', |& | and ', target_string)
            targets = list()
            for target_name in target_names:
                # if present, find target instnace
                possible_target = self.target_search(target_name)
                if possible_target:  # if a possible target was found
                    if not self.target_bad(possible_target):
                        targets.append(possible_target)
            if len(targets) == 0:
                target = None
            else:
                target = targets[0]
                # if only one target was found, targets should be an empty iterator
                if len(targets) < 2:
                    targets = tuple()
            # if multiple targets were found collect their instances
            self.targets = targets
        else:
            target_name = lhs
            target = self.target_search(target_name)  # if present, find target instnace
            if self.target_required:  # if a target is required and
                if target:  # if a target was found
                    # if that target does not meet command requirements, stop the command
                    if self.target_bad(target):
                        return True  # stop the command
        if target:  # a target(s) were found
            self.target = target  # target is good, collect an instance of it in Command
        else:  # no target was found
            if self.target_required:
                if len(target_name) == 0:
                    caller.msg(f"What would you like to {self.key}?")
                    cmd_suggestion = f"help {self.key}"
                    caller.msg(f"If you need help try |lc{cmd_suggestion}|lt{cmd_suggestion}|le.")
                    return True
                else:
                    if self.search_caller_only:
                        not_found_msg = f'{target_name} is not here.'
                        target = caller.search(target_name, nofound_string=not_found_msg)
                        if target:
                            cmd_suggestion = f"get {target_name}"
                            caller.msg(f"Try picking it up first with |lc{cmd_suggestion}|lt{cmd_suggestion}|le.")
                            return True
                    else:
                        caller.msg(f'{target_name} is not here.')
                        return True
        return super().at_pre_cmd()

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """

    def successful(self, success=True):
        """Record if the command was successful."""

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
                        message = f"{self.caller.usdesc} is testing deferring a command."
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

    def deferred_action(self):
        """
        This method is called after defer_time seconds when the Command.defer method is used.

        Usage:
            Intended to be overritten. Simply put the action portions of a command in this method.
        Return:
            Return True if the command completes successfully.
        """
        pass

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
        if utils.inherits_from(target, 'typeclasses.characters.Character'):
            return target.status_stop_request(stop_message, stop_cmd)
        else:
            return False

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
                Default: f'{self.caller.usdesc} stopped your {target.ndb.deffered_command.key} command with {self_pronoun} {self.key}.'
            stop_cmd=str: a command to run when the deffered command is stopped.
                Default: None
                Example: 'look'
            status_type=str, status type to stop
                default: 'busy'

        Example:
            commands.developer_cmdsets.CmdStopCmd
        """
        caller = self.caller
        #set the target of the forced stop
        if not target:
            target = caller
        # if the target has a command deffered
        if target.nattributes.has('deffered_command'):
            if not stop_message:  # if none was provided make a message
                if target == caller:  # do not display a stop message if the player stopped their own command
                    stop_message = None
                else:
                    self_pronoun = caller.get_pronoun('|p')
                    stop_message = f'{caller.usdesc} stopped your {target.ndb.deffered_command.key} command with {self_pronoun} {self.key}.'
            status_functions.status_force_stop(target, stop_message, stop_cmd, status_type)
        else:
            caller.msg(f'{target.usdesc} is not commited to an action.')

    def complete_early(self, target=None, stop_message=None):
        """
        Complete a deffered complete before the completion time has passed
        Returns True if the early completion was successful.
        Displays a f'{target.usdesc} is not commited to an action.' message
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
                stop_message = f'{self.caller.usdesc} allowed you to complete your {target.ndb.deffered_command.key} command early with {self_pronoun} {self.key} command.'
            stopped_succesfully = status_functions.status_delay_stop(target, 'busy', True)
            if stop_message:
                target.msg(stop_message)
        else:
            if target == self.caller:
                self.caller.msg(f'You are not commited to an action.')
            else:
                self.caller.msg(f'{target.usdesc} is not commited to an action.')
        return stopped_succesfully

    def act_vs_msg(self, action_result, evade_result):
        """
        Returns two strings to display at the start of an actions message.
        Intended to be used to more easily get the vs message for commands

        Arguments:
            action_result: number returned from actions.targeted_action
            evade_result: number returned from actions.targeted_action

        Returns:
            caller_message, target_message
            Where caller_message is the message to show the command's caller
            where target_message is the message to show the command's target
        """
        caller_message = f"{self.key} {action_result} VS evade {evade_result}: "
        target_message = f"evade {evade_result} VS {self.key} {action_result}: "
        return caller_message, target_message

    def target_out_of_melee(self):
        """
        returns true if the commands target is out of melee range.
        Intended to be used in Command.deferred_action to easily check if the target is still in range.

        Returns:
            True, if the target is out of melee range
        """
        caller = self.caller
        target = caller.search(self.target.usdesc, quiet=True)
        if not target:
            caller.msg(f'You can no longer reach {self.target.usdesc}.')
            return True

    def get_body_part(self, target=None, no_understore=False, log=False):
        """
        Return the name of a body part that exists on target

        Arguments:
            target, an Object target for get_part to choose a body part from
            no_understore=False, if True underscores '_' will be removed from the returned part name.
            log=False, if True log the variables used

        Returns:
            str, in the form of a body part description.
                Example: "head" or "waist"
            False, if this object has no body parts to hit.
            None, the function failed on the python level.

        Notes:
            If not passed, target is a reference of self.target
            if self.target has no object instance, target is self.caller
        """
        if not target:
            if hasattr(self, 'target'):
                if self.target:
                    target = self.target  # use target when available
                else:
                    target = self.caller
            else:
                target = self.caller
        return body.get_part(target, no_understore, log)

    def dmg_after_dr(self, dmg_dealt=None, body_part_name=None):
        """
        Returns damage dealt after damage reduction.
        Minimum return value is 0.

        Arguments
            dmg_dealt=None, the damage the command dealth
                If None is provided dmg_after_dr will use self.dmg_dealt
                if self.dmg_dealt does not exist a random roll will be processed.
                    using standard rules: dmg_dealt = damage.roll(self)
                    where self.dmg_max is the max damage possible and self.dmg_mod_stat modifies the damage
            body_part_name=None, the body part the command is manipulating.
                Leave blank if you want to ignore dr for armor
            log=False, should this function log messages

        Usage:
            dmg_result = self.dmg_after_dr()

        equation:
            Each action has a list of damage types they can manipulate.

            Action's damage is reduced by
                targets lowest dr value, that the action manipulates.

                If the action hit a body part.
                It is ALSO reduced by that body parts lowest dr value, that the action manipulates.
                Normally this would be the armor's dr value for that body part.

        Returns:
            damage dealt after dr for the body part hit and the target
            The minimum value this method returns is 0
        """
        return damage.get_dmg_after_dr(self, dmg_dealt, body_part_name)

    def combat_action(self, action_mod=None, caller_msg=None, target_msg=None, room_msg=None, log=None):
        """
        A command method intended to be a used to easily facilitate basic combat actions.
        This is indeded for basic combat actions.
        Complex combat actions, or ones with intricate descriptions need to be custom made.
        combat_action can be very useful as an outline for more complex actions

        Arguments
            action_mod=None, an int to add to the caller's action roll.
            log, if this method and methods and functions used within should log messages

        Usage:
            Below is an example taken from commands.combat.unarmed.CmdPunch
                def deferred_action(self):
                    action_mod = self.unarmed_str_mod  # add half of the caller's str modifier to the attack
                    return self.combat_action(action_mod)

        Notes:
            This action will:
                Verify the target is within the Command's range.
                    currently with Command.target_out_of_melee()
                    will be updated when combat ranged attack are developed
                use actions.target_action to roll for an attack
                On success
                    get a body part hit with Command.get_body_part()
                    get damage dealt with Command.dmg_after_dr(part_hit)
                    adjust target's hp if damage dealt was greater than 0
                create a basic message to show caller, target and other in the room

            combat_action intentionally does not accept a damage modifier
            Damage should be modified with Command.dmg_max
            Keeping on the idea of uncertain outcomes that the player is more likely to succeed at.


        Returns:
            True, if the action completed successfully.
            None, if there are python exceptions
            False, if there is a rules based reason for failure.
                Example: self.target_out_of_melee()

        todo:
            add damage type messages
            f" Hitting {target.usdesc}'s {part_hit}."
            f" {dmg_type_desc} {target.usdesc}'s {part_hit}."

        """
        # stop the method if target is out of range
        if self.target_out_of_melee():
            return False
        caller = self.caller
        target = self.target
        cmd_desc = self.desc
        caller_weapon = self.caller_weapon
        passed_caller_msg = caller_msg
        passed_target_msg = target_msg
        passed_room_msg = room_msg
        result, action_result, evade_result = actions.targeted_action(caller, target, log)
        if action_mod:  # if passed, add action mod to results
            result += action_mod
            action_result += action_mod
        caller_msg, target_msg = self.act_vs_msg(action_result, evade_result)
        # use passed messages if they were not provided, make messages
        if passed_caller_msg:  # if a custom caller message was passed
            caller_msg += passed_caller_msg
        else:  # no custom caller message was passed
            caller_msg += f"You {self.key} at {target.usdesc}"
            if caller_weapon:  # if the Command instance has a caller_weapon saved
                caller_msg += f" with your {caller_weapon}"
        if passed_target_msg:  # if a custom target message was pssed
            target_msg += passed_target_msg
        else:  # no custom target message was passed
            target_msg += f"{caller.usdesc} {cmd_desc} at you"
            if caller_weapon:  # if the Command instance has a caller_weapon saved
                target_msg += f" with {caller.get_pronoun('|p')} {caller_weapon}"
        if passed_room_msg:  # if a custom room message was passed
            room_msg = passed_room_msg
        else:  # no custom room message was passed
            room_msg = f"{caller.usdesc} {cmd_desc} at {target.usdesc}"
            if caller_weapon:  # if the Command instance has a caller_weapon saved
                room_msg += f" with {caller.get_pronoun('|p')} {caller_weapon}"
        if result > 0:  # the action hit
            # get the body part that was hit
            part_hit = self.get_body_part()
            dmg_dealt = self.dmg_after_dr(body_part_name=part_hit)
            if dmg_dealt > 0:  # make certain the combat action adjusts hp only when needed
                target.hp -= dmg_dealt
            caller_msg += " and connect."
            target_msg += " and connects."
            room_msg += " and connects."
            if part_hit:  # if that target had parts to hit, add it to the action's messages
                part_hit = part_hit.replace('_', ' ')  # change "side_name" to "side name"
                caller_msg += f" Hitting {target.usdesc}'s {part_hit}."
                target_msg += f" Hitting your {part_hit}."
                room_msg += f" Hitting {target.usdesc}'s {part_hit}."
            caller_msg += f" Dealing {dmg_dealt} damage."
            target_msg += f" You take {dmg_dealt} damage."
            self.successful(True)  # record the success
        else:  # the action missed
            caller_msg += " but miss."
            target_msg += f" but you successfully evade the {self.key}."
            room_msg += " and misses."
            self.successful(False)  # record the failure
        # display messages to caller, target and everyone else in the room
        caller.msg(caller_msg)
        # only show message to target if it is a Character
        # should be switched to if controlled by a session
        if utils.inherits_from(target, 'typeclasses.characters.Character'):
            target.msg(target_msg, force_on_unconscious=True)
        caller.location.msg_contents(room_msg, exclude=(target, caller))
        # make the action cost something
        self.cost(self.cost_level, self.cost_stat)
        if log:
            log_info(f'Command.combat_action, Character ID: {caller.id} | result {result}')
            log_info("caller message: "+caller_msg)
            log_info("target message: "+target_msg)
            log_info("room message: "+room_msg)
        return True

    def cost(self, cost_level='low', cost_stat='END', log=False):
        """
        action cost

        Arguments:
            cost_level='low', level this action should cost.
                Accepts: 'low', 'mid', 'high' or an integer
                if a number, the cost is that number.
                This variable will be overriden with the action commands cost_level attribute
            cost_stat='END', The stat this function will use for this action.
                This variable will be overriden with the action commands cost_stat attribute

            log=False, if True log the variables used

        Returns:
            the numrical value that the stat will be drained.
        """
        caller = self.caller
        actions.action_cost(caller, cost_level, cost_stat)

    def target_bad(self, target):
        """
        Received an instance of an object and verifies it is useable by this command.

        Tests:
            self.can_not_target_self, if True this command will end with a message if the Character targets themself
            target.targetable, if the target can be targeted by commands
            self.target_inherits_from, a tuple, position 0 string of a class type, position 1 is a string to show on mismatch

        Arguments
            target, an instance of an object for this command to target

        Returns:
            True, if that target is not useable by this command.
        """
        caller = self.caller
        # check for targeting self support
        if target == caller and self.can_not_target_self:
            caller.msg(f'You can not {self.key} yourself.')
            return True
        # check if the target can be targeted
        if not target.targetable:
            caller.msg(f'You can not {self.key} {target.usdesc}.')
            return True
        # if enabled verify inheritens and show message on mismatch
        if self.target_inherits_from:
            target_inherits_from, inherit_mismatch_msg = self.target_inherits_from
            if not utils.inherits_from(target, target_inherits_from):
                caller.msg(f"You can only {self.key} {inherit_mismatch_msg}.")
                return True
        # check if target needs to be in caller's hand
        if self.target_in_hand:
            # if the Character is not holding the object to be wielded, stop the command
            if not caller.is_holding(target):
                stop_msg = f"You have to hold an object you want to {self.cmdstring}.|/"
                get_cmd = f"get {target.usdesc}"
                get_suggestion = highlighter(get_cmd, click_cmd=get_cmd)
                stop_msg += f"Try getting it with {get_suggestion}"
                caller.msg(stop_msg)
                return True

    def target_search(self, target_name):
        """
        Search for an instance of a target.

        Arguments:
            target_name str, a string representation of a target's name or description.
                Uses caller.search() to search
                Start string with target number if you would like to choose a
                specific index from the returned tuple from caller.search()

        Returns:
            None, if the target was not found.
            object instance of the target if it was found.
        """
        caller = self.caller
        target = None
        target_name_starts_with_num = re.match(r"^(\d+)\s+(.+)", target_name)
        # the arguments of the command starts with a number
        if target_name_starts_with_num:
            # there are two or more capture patterns above
            target_number, target_name = target_name_starts_with_num.groups()
            target_number = int(target_number)
            # make the number provided array friendly
            if target_number > 1:
                target_number -= 1
            if self.log:
                log_info(f"Command.parse, Caller ID: {self.caller.id}, Command key: {self.key} | " \
                         f"target_name_starts_with_num: {target_name_starts_with_num} | target_number: {target_number} | " \
                         f"target_name: {target_name}")
        else:  # command target does not start with a number
            target_number = 0
        # if set search the caller only, if not search the room
        if self.search_caller_only:
            target = caller.search(target_name, quiet=True, candidates=caller.contents)
        else:
            target = caller.search(target_name, quiet=True)
        if target:  # a target(s) was found
            target = target[target_number]  # get the correct target number
            return target
