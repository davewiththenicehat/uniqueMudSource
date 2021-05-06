"""
Commands

Commands describe the input the account can do to the game.

"""

import re
from datetime import datetime

from evennia import default_cmds
from world import status_functions
from evennia import utils
from evennia.utils.logger import log_info

from world.rules import damage, actions, body, skills
from utils.um_utils import highlighter
from utils.emote import um_emote


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
        To more seamlessly support UniqueMud's deffered command system,
            evennia's Command.func has been overridden.
            If your command does not defer an action, override Command.func
        To provide UM targeting system to Command.func, parse has been
            overridden and cleared.
        parse is called manually in Command.at_pre_cmd via super().parse()
        All attributes added for UM are local or non-class attributes.
        Command.at_init has been created for a high degree of instance customization.

    Attributes:
        Important: All attributes added for UM are local or non-class attributes.
            This allows for an extreme degree of automation and customization on the instance level.
            Allowing Object attributes to interact with Command attributes.
            To initalize an attribute created by UM it needs to be declared in Command.at_init.

        status_type = 'busy'  # Character status type used to track the command
        defer_time = 3  # time is seconds for the command to wait before running
            action of command
        evade_mod_stat = 'AGI'  # stat used to evade this command
            AGI  # agility, defend against physical actions like attacks
        evade_msg, message to display when the character attempts to evade
            Used in world.rules.actions.evade_roll
        action_mod_stat = 'OBS'  # stat used to modify this command
            OBS  # observation, for physical actions. Attacks
        cost_stat='END'  # stat this command will use for the action's cost
        cost_level='very easy' #  level this action should cost.
            Acceptable levels: 'very easy', 'easy', 'moderate', 'hard', 'daunting' or a number or an integer
            dictionary for these values is in world.rules.actions.COST_LEVELS
            If a number is used for cost_level that number is used as the base
                cost for the command.
        desc = None  # a present tense description for the action of this command.
            IE: "kicks"
            If None when self.func is called, it will give assigned self.key
        weapon_desc = None  # weapon description that will show up in
            This is intended for attack commands that do note use a wielded weapon.
            Leave as None if requires_wielding is in use.
        caller_weapon = None  # instance of the caller's wielded weapon from requires_wielding
            Automatically collected in Command.at_pre_cmd
        roll_max = 50  # max number this command can roll to succeed
            If a command requires a wielded item. item.act_roll_max_mod is added to Command.roll_max
                item.act_roll_max_mod can be a negative number.
        dmg_max = 4  # the maximum damage this command can roll
        cmd_type = ''  # string of that command type. IE: 'evasion' for an evasion cmd
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
        search_candidates (list): List of objects to search for the command's target.
            Defaults to caller's location.
            Over ride with Command method get_search_candidates.
                get_search_candidates is automatically called to set search_candidates in at_pre_cmd
            Do not set in Command's at_init method.
        sl_split = (' from ', ' in ')  # Search Location split list
            A list of words to used to split the name of the object from it's location
            Locations specified must exist in caller.search()
            Examples:
                get <object> from <container>
                    Get will automatically look for <object> in <container>
                    No additional code in get required
                say to person, 2 person and monster in a cage "Hello"
                    Will say "Hello" to a monster in a container named 'a cage'.
                    The message still sends to other targets also.
                    No additional code in say required
            To avoid this:
                make self.sl_split = None
                Use rh_split to separate targets from commands. As is done in CmdSay.
        requires_ready = True  # if true this command requires the ready status before it can be used.
            deferal commands still require ready to defer, even is requires_ready is false.
            Failure message is handled automatically.
        requires_conscious = True  # if true this command requires the caller to be conscious before it can be used
            Failure message is handled automatically.
        requires_wielding = None  # If True this command will require a wielded item that matches Command.cmd_type
            item types can be found in typeclasses.equipment.wieldable
            item types will match command set names in world.rules.skills.SKILLS
            The item.item_type attribute must match the command's Command.cmd_type
            Example: 'one_handed'
        required_ranks = 0  # required ranks in the commands skill_name for this command to work.
        dmg_mod_stat = 'STR'  # the stat that will modifier damage this command manipulates
        dmg_types = None  # dictionary of damage types this command can manipulate.
            Attack commands should ALWAYS have one or more dmg_type.
                If an attack command has no dmg_types,
                there is no chance for the defenders dr to take affect.
            key is the type of damage as they appear in rules.damage.TYPES
            value is a flat bonus this command will provide in reference to damage.
                Most commands the value should be 0.
                Having the damage type offers the ability for this command to do that type of damage.
            Usage Example:
                An action that calls Command.dmg_after_dr(), will look for the defenders lowest
                dr value from the commands dmg_types on the body part hit.
                If the key has a value greater than 0, that value will be added to the damage dealt.
                    Even if the key is a negative number.
        caller_message_pass = None  # text to message the caller.
            Will not call automatically, here to pass between Command functions
        target_message_pass = None  # text to message the target.
            Will not call automatically, here to pass between Command functions
        room_message_pass = None  # text to message the room.
            Will not call automatically, here to pass between Command functions
        log = False  # set to true to info logging should be enabled.
            Error and warning messages are always enabled.
        learn_diff = 1  # How difficult the command is to learn.
            1: 'very easy', 2: 'easy', 3: 'moderate', 4: 'hard', 5: 'daunting'
            difficulty rules in world.rules.skills
        comp_diff = 2  # How difficult the command is to complete
            1: 'very easy', 2: 'easy', 3: 'moderate', 4: 'hard', 5: 'daunting'
            difficulty rules in world.rules.skills
        skill_name = self.key  # the skill name this command uses for rank modification
        start_time = datetime.datetime.now()  # time the command starts
        end_time = False  # used to manually override the end time.
            intended for unit testing.

    Methods:
        All methods are fully documented in their docstrings.
        at_init, Called when the Command object is initialized.
        func, To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.
        custom_requirements(), Verifies commands custom requirements are met. Stops the command if they are not.
        defer(int or float), defer the action of a command by calling Command.deferred_action after the number of seconds passed to defer
        deferred_action(), override to commit the action of a command to a later time.
        def_act_comp(self), called if deferred_action returns True, runs completion tasks.
            exp gain and action costs occur here.
        start_message(), Displays a message after a command has been successfully deffered.
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
        cost(cost_level='very easy', cost_stat='END'), Calculate and remove the cost of this Command
        target_bad(target=object), returns True if object passed is not targetable by this command
        get_search_candidates(self): Return a list of objects the command should use as search candidates.
        target_search(target_name=str), Search for an instance of a target.
        split_target_name(target_name=str), accepts command target string.
            Returns the target_name and location_name
        evade_roll, used for unit testing
        action_roll, used for unit testing
        skill_ranks(), Returns the number of ranks the caller has in this command's corrisponding Character skill
        gain_exp(self), Character gains experience for the command.
    """

    def __init__(self, **kwargs):
        """
        Overiding to call the at_init method.

        """
        if kwargs:
            super().__init__(self, **kwargs)
        self.dmg_types = None  # dictionary of damage types this command can manipulate.
        self.weapon_desc = None  # weapon description that will show up in Command.combat_action's automated messages
        self.caller_weapon = None  # instance of the caller's wielded weapon from requires_wielding
        self.dmg_max = 4  # the maximum damage this command can roll
        self.status_type = 'busy'  # Character status type used to track the command
        self.defer_time = 3  # time is seconds for the command to wait before running action of command
        self.evade_mod_stat = 'AGI'  # stat used to evade this command
        self.action_mod_stat = 'OBS'  # stat used to modify this command
        self.roll_max = 50  # max number this command can roll to succeed
        self.dmg_mod_stat = 'STR'  # the stat that will modifier damage this command manipulates
        self.target_required = False  # if True the command will stop without a target
        self.can_not_target_self = False  # if True this command will end with a message if the Character targets themself
        self.cmd_type = ''  # string of that command type. IE: 'evasion' for an evasion cmd
        self.target_inherits_from = False  # a tuple
            # position 0 string of a class type, position 1 is a string to show on mismatch
        self.target_in_hand = False  # if True the target of the command must be in the Characters hand to complete successfully
        self.search_caller_only = False  # if True the command will only search the caller for targets
        self.search_candidates = []  # List of objects to search for the command's target.
        self.caller_message_pass = None  # text to message the caller.
            # Will not call automatically, here to pass between Command functions
        self.target_message_pass = None  # text to message the target.
            # Will not call automatically, here to pass between Command functions
        self.room_message_pass = None  # text to message the room.
            # Will not call automatically, here to pass between Command functions
        self.pres_tense_desc = None  # a present tense description for the action of this command. IE: "kicks"
        self.requires_ready = True  # if true this command requires the ready status before it can do anything.
            # deferal commands still require ready to defer
        self.requires_conscious = True  # if true this command requires the caller to be conscious
        self.requires_wielding = None  # require a wielded item type for command to work.
        self.required_ranks = 0  # required ranks in the commands skill_name for this command to work.
        self.cost_stat = 'END'  # stat this command will use for the action's cost
        self.cost_level = None  # level this action should cost. Acceptable levels: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number
        self.log = False  # set to true to info logging should be enabled. Error and warning messages are always enabled.
        self.learn_diff = 1  # How difficult the command is to learn.
        self.comp_diff = 2  # How difficult the command is to complete
        self.skill_name = self.key  # the skill name this command uses of rank modification
        self.sl_split = (' from ', ' in ')  # list of words to split names from locations in commands
        self.start_time = datetime.now()  # time the command starts
        self.end_time = False  # used to manually override the end time.
        self.at_init()

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        pass

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
        stops the execution of a Command if Character does not meet the Command.required_ranks in the
            Command.skill_name skill.
        finds and store a reference of the Object the command is targetting as self.target
            Also adds support for easy targeting of simular objects.
            "punch 2 droid", rather than "punch 2-droid full name"
        stops the command if targeting self an self.can_not_target_self is True
        stops the commnad if the targets self.targetable is False
        sets the commands self.pres_tense_desc to self.key if desc was not set manually
        if Command.required_wielding is True
            collects an instance of wielded weapon of same type as command in Command.caller_weapon
                IE: For an item to be accepted item.item_type == command.cmd_type
            Command.weapon_desc is set to item.key
            Command.dmg_max is set to item.dmg_max
            item.dmg_types is merged with command.dmg_types
                Where values are added together, not replaced.
            item.act_roll_max_mod is added to Command.act_roll_max_mod

        Notes:
            if a command starts with "to " or "at ".
                The name of the target to search for will be collected after those starting strings.
            Evennia note: at_pre_cmd(): If this returns anything truthy, execution is aborted.
            Behavior note: returning anything stops the exection of the command.
        """
        caller = self.caller
        self.search_candidates = self.get_search_candidates()
        # stop the command if basic requirements are not met
        if not self.requirements(basic=True):
            return True
        # stop the command if ranks requirement are not met
        required_ranks = self.required_ranks
        if required_ranks:
            if required_ranks > self.skill_ranks():
                msg = f"You must have {required_ranks} or more ranks in {self.skill_name} to {self.key}."
                caller.msg(msg)
                return True
        # give an action description if none was provided
        if not self.pres_tense_desc:
            self.pres_tense_desc = self.key
        # self.parse was overriden to provide UM targeting system to commands that use only self.func
        # it has to be manually called now
        super().parse()
        # find the name and if provided number of the target
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
            target = self.target_search(target_name)  # if present, find target instance
            if self.target_required:  # if a target is required and
                if target:  # if a target was found
                    # if that target does not meet command requirements, stop the command
                    if self.target_bad(target):
                        return True  # stop the command
        if target:  # a target(s) were found
            self.target = target  # target is good, collect an instance of it in Command
        else:  # no target was found
            if self.target_required:
                if len(target_name) == 0:  # caller provided no target name
                    caller.msg(f"What would you like to {self.key}?")
                    cmd_suggestion = f"help {self.key}"
                    caller.msg(f"If you need help try |lc{cmd_suggestion}|lt{cmd_suggestion}|le.")
                    return True
                else:  # caller provided a target name
                    if self.search_caller_only:
                        not_found_msg = f'{target_name} is not among your possesions.'
                        target = caller.search(target_name, nofound_string=not_found_msg)
                        if target:
                            cmd_suggestion = f"get {target_name}"
                            caller.msg(f"Try picking it up first with |lc{cmd_suggestion}|lt{cmd_suggestion}|le.")
                        return True
                    else:
                        target_name, location_name = self.split_target_name(target_name)
                        if location_name:  # caller provided a search location
                            # find a reference of the search_candidates
                            search_candidates = self.target_search(location_name)
                            if search_candidates:  # useable location provided
                                msg = f"You could not find {target_name} " \
                                      f"in {search_candidates.get_display_name(caller)}."
                                caller.msg(msg)
                                return True
                            else:  # caller did not provide a useable location
                                msg = f"You could not find {location_name} " \
                                      f"to search for {target_name}."
                                caller.msg(msg)
                                return True
                        else:
                            caller.msg(f'You can not find {target_name}.')
                            return True
        # stop the command if custom command requirements are not met
        if not self.custom_requirements():
            return True
        return super().at_pre_cmd()

    def requirements(self, basic=False, custom=False, target=False):
        """Verify requirements for command are met.

        Args:
            basic (bool): If True check basic requirements. Default is False.
                Does not require parse method call or target collection.
            custom (bool): calls custom_requirements. Default is False
                Should only be used after at_pre_cmd method call.
            target (bool): If True verify target(s) are good. Default is False.
                Can only be used after at_pre_cmd method call.

        Returns:
            met (bool): True if requirements are met.
        """
        caller = self.caller
        if basic:  # check basic command requirements
            if self.requires_ready:
                caller_ready = caller.ready()
                if not caller_ready:
                    return False
            elif self.requires_conscious:
                if not caller.ready(conscious_only=True):
                    return False
            # check if required wielded weapon is being wielded.
            if self.requires_wielding:
                wielded_items = caller.wielding()
                if not wielded_items:
                    required_item_type = self.cmd_type.replace('_', ' ')
                    caller.msg(f'You must be wielding a {required_item_type} item to {self.key}.')
                    return False
                # look for required wielded item type among wielded items
                for item in wielded_items:
                    if item.item_type == self.cmd_type:
                        self.caller_weapon = item
                        self.weapon_desc = item.key
                        self.dmg_max = item.dmg_max
                        if item.act_roll_max_mod:  # the item has a meaningful roll_max modifier add it
                            self.roll_max += item.act_roll_max_mod
                        break
                if not self.caller_weapon:
                    required_item_type = self.cmd_type.replace('_', ' ')
                    caller.msg(f'You must be wielding a {required_item_type} item to {self.key}.')
                    return False
        if custom:
            if not self.custom_requirements():
                return False
        if target:
            if not self.target_required:  # stop the requirement check if target is not required.
                return True
        return True

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        return True  # custom requirements met, allow command to run

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
                        message = f"/Me is testing deferring a command."
                        self.caller.location.emote_contents(message)

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
        Returns:
            successful (bool): True if the command completed sucessfully.
                If this method returns True self.def_act_comp will be called after automatically.
        """

    def def_act_comp(self):
        """Called after deferred_action completes successfully.
        If the deferred_action returned True.

        By default it calls:
            self.gain_exp()
            self.cost()
        """
        self.gain_exp()
        self.cost()

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
                Default: f'/Me stopped your {target.ndb.deffered_command.key} command with {self_pronoun} {self.key}.'
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
                    stop_message = f'/Me stopped your {target.ndb.deffered_command.key} command with {self_pronoun} {self.key}.'
            status_functions.status_force_stop(target, stop_message, stop_cmd, status_type, caller)
        else:
            caller.emote(f'/target is not commited to an action.', target)

    def complete_early(self, target=None, comp_msg=None):
        """
        Complete a deffered complete before the completion time has passed
        Returns True if the early completion was successful.
        Displays a f'/target is not commited to an action.' message
            if the command could not be completed early.

        Supports:
            Sending a custom message
            Target other than self.caller

        Arguments:
            target=Character, a Character to complete a command early
            comp_msg=msg, a message to send to the target

        Example:
            From within a commands func method
            if target:
                self.complete_early(target)
            else:
                self.complete_early(self.caller)

            Example in commands.developer_cmdsets.CmdCompleteCmdEarly
        """
        caller = self.caller
        stopped_succesfully = None
        if not target:
            target = self.caller
        if target.nattributes.has('deffered_command'):
            if not comp_msg:  # if none was provided make a message
                self_pronoun = self.caller.get_pronoun('|p')
                comp_msg = f'/Me allowed you to complete your {target.ndb.deffered_command.key} command early with {self_pronoun} {self.key} command.'
            stopped_succesfully = status_functions.status_delay_stop(target, 'busy', True)
            if comp_msg and target is not caller:
                target.emote(comp_msg, caller, target)
        else:
            if target == self.caller:
                self.caller.msg(f'You are not commited to an action.')
            else:
                caller.emote("/Target is not commited to an action.", target)
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
        cmd_target = self.target
        target_name = cmd_target.get_display_name(caller)
        target = caller.search(target_name, quiet=True)
        if target:
            if cmd_target in target:
                return False
        caller.msg(f'You can no longer reach {target_name}.')
        return True

    def get_body_part(self, target=None, part_name=False, log=None):
        """
        Return an instance of a body part on a target.

        Arguments:
            target, an Object target for get_part to choose a body part from
            part_name=False, Pass a string name of a body part and get_body_part will return an
                instance of that part.
                Example: 'left_leg'
            log=False, if True log the variables used

        Returns:
            str, in the form of a body part description.
                Example: "head" or "waist"
            False, if this object has no body parts to hit.
            None, the function failed on the python level.

        Unit Tests:
            in commands.test.TestCommands.test_cmd_methods

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
        return body.get_part(target, part_name, log)

    def dmg_after_dr(self, dmg_dealt=None, max_defense=False, body_part=None, target=None, log=False):
        """
        Get damage dealt after damage reduction.
        Minimum return value is 0.

        Arguments
            dmg_dealt=None, the damage the command dealt
                If None is provided get_dmg_after_dr will use self.dmg_dealt
                if self.dmg_dealt does not exist a random roll will be processed.
                    using standard rules: dmg_dealt = damage.roll(self)
                    where self.dmg_max is the max damage possible and self.dmg_mod_stat modifies the damage
            max_defense=False, if true the attack's least damaging dmg_type is used.
            body_part=None, the body part the command is manipulating.
                Leave blank if you want to ignore dr for armor.
                Can be an instance of the body part, or the parts string name.
            target=None, instance of the target that would receive the damage.
            log=False, should this function log messages

        Returns:
            damage dealt after dr for the body part hit after the targets damage reduction.
            Default the highest possible damage is returned.
            pass max_defense=True, to return the lowest possible damage.
            The minimum value this function returns is 0.

        Unit Tests:
            in commands.test.TestCommands.test_dmg

        equation:
            Each action has a list of damage types they can manipulate.
            By default the damage type that does the most damage is chosen.
            If argument max_defense is True, the type that does the least damage is chosen.

            Action's damage is reduced by
                targets dr value
                If the action hit a body part.
                That body part's dr value is also used to reduce damage.
                    Normally this would be the armor's dr value for that body part.
        """
        return damage.get_dmg_after_dr(self, dmg_dealt, max_defense, body_part, target, log)

    def combat_action(self, action_mod=None, caller_msg=None, target_msg=None, room_msg=None, log=None):
        """
        A command method intended to be a used to easily facilitate basic combat actions.
        This is intended for basic combat actions.
        Complex combat actions, or ones with intricate descriptions need to be custom made.
        combat_action can be very useful as an outline for more complex actions

        Arguments
            action_mod=None, an int to add to the caller's action roll.
            caller_msg=None, Replaced message sent to caller.
                Replaces:
                    You {self.key} at /target
                    if self.weapon_desc: with your {weapon_desc}
            target_msg=None, Replaced message sent to action's target.
                Replaces:
                    /Me /target at you
                    if self.weapon_desc: with {caller.get_pronoun('|p')} {weapon_desc}
            room_msg=None, Replaced message sent to the caller's location.
                Replaces:
                    /Me {cmd_desc} at /target
                    if self.weapon_desc: with {caller.get_pronoun('|p')} {weapon_desc}
            log, if this method and methods and functions used within should log messages

        Usage:
            Below is an example taken from commands.combat.unarmed.CmdPunch
                def deferred_action(self):
                    action_mod = self.unarmed_str_mod  # add unarmed STR mod
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
                create a basic message to show caller, target and other in the room.

            The messages in this method automatically truncate weapon_desc by removing
            "a " or "an " from the start of the weapon_desc string.

            combat_action intentionally does not accept a damage modifier
            Damage should be modified with Command.dmg_max
                Keeping on the idea of uncertain outcomes that the player is
                more likely to succeed at.

        Unit Test:
            If called by a character attached to a developer account. Arguments
            '/unit_test_succ' and '/unit_test_fail' are switches that cause
            a combat_action to always fail or succeed.
                '/unit_test_succ': combat_action will always succeed.
                '/unit_test_fail': combat_action will always fail.

            in commands.test.TestCommands.test_ most any command set.

        Returns:
            True, if the action completed successfully.
            None, if there are python exceptions
            False, if there is a rules based reason for failure.
                Example: self.target_out_of_melee()

        todo:
            add damage type messages.

        """
        # stop the method if target is out of range
        if self.target_out_of_melee():
            return False

        # reference data types
        caller = self.caller
        target = self.target
        cmd_desc = self.pres_tense_desc
        weapon_desc = self.weapon_desc
        passed_caller_msg = caller_msg
        passed_target_msg = target_msg
        passed_room_msg = room_msg
        result = None

        # remove the words "a" and "an" from the start of weapon_desc
        if weapon_desc.startswith('a '):
            weapon_desc = weapon_desc.replace('a ', '', 1)
        elif weapon_desc.startswith('an '):
            weapon_desc = weapon_desc.replace('a ', '', 1)

        # for unit tests add support for always hit or always miss
        if hasattr(caller, 'account'):  # caller has an account
            perm_str = ''
            if hasattr(caller.account, 'permissions'):
                perm_str = str(caller.account.permissions)
            if 'developer' in perm_str:  # if the caller is a developer
                if 'unit_test_succ' in self.switches:  # attack always succeeds
                    result = 95
                    action_result = 100
                    evade_result = 5
                elif 'unit_test_fail' in self.switches:  # attack always fails
                    result = -95
                    action_result = 5
                    evade_result = 100

        # roll the attack
        if result is None:  # Not a dev account using unit_test arg
            result, action_result, evade_result = actions.targeted_action(caller, target, log)
        if action_mod:  # if passed, add action mod to results
            result += action_mod
            action_result += action_mod

        # create the attack messages
        caller_msg, target_msg = self.act_vs_msg(action_result, evade_result)
        # use passed messages if they were not provided, make messages
        if passed_caller_msg:  # if a custom caller message was passed
            caller_msg += passed_caller_msg
        else:  # no custom caller message was passed
            caller_msg += f"You {self.key} at /target"
            if weapon_desc:  # if the Command instance has a weapon_desc saved
                caller_msg += f" with your {weapon_desc}"
        if passed_target_msg:  # if a custom target message was pssed
            target_msg += passed_target_msg
        else:  # no custom target message was passed
            target_msg += f"/Me {cmd_desc} at you"
            if weapon_desc:  # if the Command instance has a weapon_desc saved
                target_msg += f" with {caller.get_pronoun('|p')} {weapon_desc}"
        if passed_room_msg:  # if a custom room message was passed
            room_msg = passed_room_msg
        else:  # no custom room message was passed
            room_msg = f"/Me {cmd_desc} at /target"
            if weapon_desc:  # if the Command instance has a weapon_desc saved
                room_msg += f" with {caller.get_pronoun('|p')} {weapon_desc}"
        if result > 0:  # the action hit
            # get the body part that was hit
            part_hit = self.get_body_part()
            dmg_dealt = self.dmg_after_dr(body_part=part_hit)
            if dmg_dealt > 0:  # make certain the combat action adjusts hp only when needed
                target.hp -= dmg_dealt
            caller_msg += " and connect."
            target_msg += " and connects."
            room_msg += " and connects."
            if part_hit:  # if that target had parts to hit, add it to the action's messages
                part_hit_name = part_hit.name.replace('_', ' ')  # change "side_name" to "side name"
                caller_msg += f" Hitting /target's {part_hit_name}."
                target_msg += f" Hitting your {part_hit_name}."
                room_msg += f" Hitting /target's {part_hit_name}."
            caller_msg += f" Dealing {dmg_dealt} damage."
            target_msg += f" You take {dmg_dealt} damage."
            self.successful(True)  # record the success
        else:  # the action missed
            caller_msg += " but miss."
            target_msg += f" but you successfully evade the {self.key}."
            room_msg += " and misses."
            self.successful(False)  # record the failure

        # display messages to caller, target and everyone else in the room
        self.send_emote(caller_msg, receivers=caller)
        # only show message to target if it is a Character
        # should be switched to if controlled by a session
        if utils.inherits_from(target, 'typeclasses.characters.Character'):
            self.send_emote(target_msg, receivers=target)
        # message the location
        caller.location.emote_contents(room_msg, caller, target, exclude=(target, caller))
        if log:
            log_info(f'Command.combat_action, Character ID: {caller.id} | result {result}')
            log_info("caller message: "+caller_msg)
            log_info("target message: "+target_msg)
            log_info("room message: "+room_msg)
        return True

    def cost(self, cost_level=None, cost_stat=None, subt_cost=True, log=False):
        """remove that cost from the Character and return a numerical value of the cost.

        Unit test for this function is in commands.tests.TestCommands.test_methods

        Equation, cost - (cost * stat_action_cost_mod)

        Args:
            char (Character), is the character commiting the action
            cost_stat (str), The Character stat this function will use for this action.
                If falsley action cost will attempt to collect it from a deferred command.
                If passed a Falsey argument and no deferred command is available or cost_stat
                    is falsey on the deferred. Function returns 0.
            cost_level (str), level this action should cost.
                Accepts: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number or an integer
                If a number, the cost is that number.
                If falsley action cost will attempt to collect it from a deferred command.
                If passed a Falsey argument and no deferred command is available or cost_level
                    is falsey on the deferred. Function returns 0.
            subt_cost=True, if True, the cost will be subtracted from the cost_stat.
            log=False, if True log the variables used

        Returns:
            cost (int): the numrical value that the stat will be drained.
        """
        caller = self.caller
        cost_level = cost_level if cost_level else self.cost_level
        cost_stat = cost_stat if cost_stat else self.cost_stat
        return actions.action_cost(caller, cost_level, cost_stat, subt_cost)

    def target_bad(self, target):
        """
        returns True if object passed is not targetable by this command

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
            caller.emote(f'You can not {self.key} /target.', target)
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
                get_cmd = f"get {target.get_display_name(caller)}"
                get_suggestion = highlighter(get_cmd, click_cmd=get_cmd)
                stop_msg += f"Try getting it with {get_suggestion}."
                caller.msg(stop_msg)
                return True

    def get_search_candidates(self):
        """Return a list of objects the command should use as search candidates.

        When looking for the command's target.

        Returns:
            search_candidates (list): a list of Objects to search.
                Default is caller, caller's location and contents of each.

        """
        caller = self.caller
        location = caller.location
        candidates = caller.contents
        if location:
            candidates = candidates + [location] + location.contents
        else:
            # normally we don't need this since we are
            # included in location.contents
            candidates.append(self)
        return candidates

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
        else:  # search somewhere other than caller
            standard_search = True  # a stanard search is needed
            target_name, location_name = self.split_target_name(target_name)
            if target_name and location_name:
                standard_search = False  # a stanard search is not needed
                # find a reference of the search candidates
                search_candidates = self.target_search(location_name)
                # search for the target
                if search_candidates:  # caller provided useable search location
                    target = caller.search(target_name, quiet=True, candidates=search_candidates.contents)
            if standard_search:  # a standard search is required.
                target = caller.search(target_name, quiet=True)
        if target:  # a target(s) was found
            target = target[target_number]  # get the correct target number
            return target

    def split_target_name(self, target_name):
        """
        Accepts a full target name with a 'from location_name' in it.
        Splits the location name out a returns both.

        Returns:
            target_name=str, target name caller provided.
                With any '<sl_split>' and <location_name> strings removed
            location_name=str, with no '<sl_split>' in it
                Returns False if no '<sl_split>' was found in the passed str
        """
        for split_text in self.sl_split:  # Search Location Split list
            if split_text in target_name:  # Caller spcified a search location
                # separate target and location names
                target_name, location_name = target_name.split(split_text, 1)
                location_name.replace(split_text, "", 1)
                # find a reference of the search_candidates
                return target_name, location_name
        return target_name, False

    def evade_roll(self, evade_mod_stat=None, log=False, unit_test=False):
        """
        This was created with the intent of using it during unit testing.
        If called directly it likely will not work as you intend.

        Roll evasion for the command's target.
        This is wrapper for rules.actions.evade_roll

        Returns:
            int, the evasion roll the commands target rolled.

        Arguments:
            evade_mod_stat, the stat required to evade the action evade_roll to evade
            log=False, if True log the variables used
            unit_test=False, if True evade_roll will display variables to screen

        Usage:
            Within a unit test:

            self.char1.skills.evasion.dodge = 20
            command = developer_cmds.CmdMultiCmd
            arg = "= dodge"
            wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
            cmd_result = self.call(command(), arg)
            self.assertRegex(cmd_result, wanted_message)
            command = developer_cmds.CmdCmdFuncTest
            arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
            wanted_message = r"roll_max: 67"
            cmd_result = self.call(command(), arg)
            self.assertRegex(cmd_result, wanted_message)

        Notes:
            This was created with the intent of using it during unit testing.
            If called directly it likely will not work as you intend.
        """
        if not self.target:
            self.caller.msg('A target is required.')
            return
        else:
            target = self.target
        if not evade_mod_stat:
            evade_mod_stat = self.evade_mod_stat
        return actions.evade_roll(target, evade_mod_stat, log, unit_test)

    def action_roll(self, log=False, unit_test=False):
        """
        This was created with the intent of using it during unit testing.
        If called directly it likely will not work as you intend.

        Roll evasion for the command's target.
        This is wrapper for rules.actions.action_roll

        Returns:
            int, the evasion roll the commands target rolled.

        Arguments:
            action_mod_stat, the stat required to action the action action_roll to action
            log=False, if True log the variables used
            unit_test=False, if True action_roll will display variables to screen

        Notes:
            This was created with the intent of using it during unit testing.
            If called directly it likely will not work as you intend.
        """
        return actions.action_roll(self.target, log, unit_test)

    def skill_ranks(self, log=False):
        """
        Returns the number of ranks the caller has in the skill required to run this command.

        Returns:
            int, the number of ranks the caller has in this command's skill.
                It is 0 if
                    Caller has no ranks
                    The command has no skill set

        Usage:
            # test if ranks exist
            if self.skill_ranks():
                # 1 or more ranks in this command's skill
            else:
                # no ranks in this command's skill

            # test for 10 or more ranks in this skill
            if self.skill_ranks() > 9:
                # There are 10 or more ranks in this command's skill
        """
        caller = self.caller
        skill_set = self.cmd_type
        skil_set_inst = getattr(caller.skills, skill_set, False)
        if skil_set_inst:
            skill_name = self.skill_name
            # get ranks in skill or 0 if the skill is unknown
            skill_ranks = getattr(skil_set_inst, skill_name, 0)
            skill_ranks = int(skill_ranks)
            return skill_ranks
        return 0

    def send_emote(self, emote, sender=None, receivers=None, anonymous_add=None):
        """
        Distribute an emote.

        Arguments:
            emote (str): The raw emote string as input by emoter.
            sender (Object): The one sending the emote.
            receivers (iterable): Receivers of the emote. These
                will also form the basis for which sdescs are
                'valid' to use in the emote.
            anonymous_add (str or None, optional): If `sender` is not
                self-referencing in the emote, this will auto-add
                `sender`'s data to the emote. Possible values are
                - None: No auto-add at anonymous emote
                - 'last': Add sender to the end of emote as [sender]
                - 'first': Prepend sender to start of emote.

        Example:
            "/Me punches at /target "
            from a by stander: "A tall man punches at a short name "
            from the target of the attach: "A tall man punches at you "
            from the sender (or command caller) "You punches at a short man "
                Normally the command caller and target get custom messages.

        Notes:
            All standard evennia switches are supported.
            /me will be replaced with "you" for the sender.
            /target will be replaced with the display name of the target.
                From the receivers recog attribute for the target.
                For example if they recog a friend with a proper name.
            Capitalization of /Me or /Target results in the name being upper cased.
                This does NOT work as string.capitalize(), ONLY the first character
                is adjusted. Meaning following character's in the string can be
                upper cased.
                Example: /Target may be replaced with "A big fish flops"
                         where /target would show "a big fish flops"
            If a receiver has a recog for a /target or /me entry, it will have the
                potential of being upper case. This allows for players to recog
                with proper names.
            This method is a very light wrapper for utils.um_utils.um_emote.
            If a feature is supported there, it will be supported here.

        Unit tests:
            commands.tests.TestCommands.test_um_emote, indirectly
            There are many commands that use this resulting in direct tests.
        """
        caller = self.caller
        target = self.targets if self.targets else self.target
        um_emote(emote, caller, receivers, target, anonymous_add)

    def gain_exp(self):
        """Gain experience.

        Called in world.rules.status_fucntions.status_delay_stop, where each
        command's deferred_action method is called. For all non-evasion cmds
        Called in world.rules.actions.evade_roll for evade commands. Just after
        the function stops the deferred instance, but before it echos the
        evasion message.

        Returns:
            exp_gained (int): experience gained or number of sendonds the command ran.

        todo:
            exclude dodge commands that were not used as a dodge.
        """
        if not self.cmd_type:  # this command can not gain experience
            return 0
        skill_name = self.skill_name  # the skill name this command uses of rank modification
        # do not gain skill on test commands that have not set a proper skill name
        if skill_name == 'cmd_func_test':
            return 0
        # get variables
        start_time = self.start_time  # time the command starts
        caller = self.caller  # Object that called the command
        skill_set_name = self.cmd_type  # Should be a string of the cmd type.
        end_time = self.end_time if self.end_time else datetime.now()
        # if end_time is a string, it was received from unit testing.
        # convert it into a datatime object
        if isinstance(end_time, str) and '_' in end_time:
            end_time = end_time.replace('_', ':')
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')
        # get the skill set instance than the exp value for this command
        skill_set = getattr(caller.skills, skill_set_name, False)
        if not skill_set:
            return 0
        if skill_name+"_exp" not in skill_set:
            return 0
        # calculate the experience gained (time the command ran)
        act_time = end_time - start_time
        exp_gained = act_time.total_seconds()
        current_exp = skill_set[skill_name+"_exp"]
        # record the experience gained
        skill_set[skill_name+"_exp"] = current_exp + exp_gained
        # message caller if new rank is possible
        exp_required = skills.rank_requirement(skill_set[skill_name]+1, self.learn_diff)
        if exp_required <= skill_set[skill_name+"_exp"] and skill_set[skill_name+"_msg"]:
            caller.msg(f'You have enough experience with {skill_name} to learn rank {skill_set[skill_name]+1}.')
            skill_set[skill_name+"_msg"] = False
        return exp_gained
