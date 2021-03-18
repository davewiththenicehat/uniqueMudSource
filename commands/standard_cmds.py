import re
from evennia.utils import evtable, evmore
from evennia.utils.utils import fill, dedent, inherits_from
from evennia import default_cmds
from evennia.contrib import rpsystem
from evennia import CmdSet
from commands.command import Command
from evennia.commands.default.help import CmdHelp as EvCmdHelp
from evennia.commands.default.system import CmdObjects
from evennia.commands.default.general import CmdLook as EvCmdLook
from world.rules import stats
from utils.um_utils import highlighter, error_report, objs_sdesc_str
from typeclasses.exits import STANDARD_EXITS


class StandardCmdsCmdSet(default_cmds.CharacterCmdSet):
    """
    Collection of very basic game command.
    That have no specific grouping.
    That must in some way be altered from evennias provided version.
    examples drop, inventory

    Unit tests for these commands are in commands.tests.TestCommands
    """

    priority = 100

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        self.add(CmdDrop)
        self.add(CmdInventory)
        self.add(CmdSit)
        self.add(CmdStand)
        self.add(CmdLay)
        self.add(CmdGet)
        self.add(CmdSay)
        self.add(CmdHelp)
        self.add(CmdLook)
        self.add(CmdWhisper)
        self.add(CmdStatus)
        self.add(UMCmdObjects)
        self.add(CmdPut)


class UMCmdObjects(CmdObjects):
    # overidding to remove 'stats' as an alias
    aliases = ["listobjects", "listobjs", "db"]


class CmdStatus(Command):
    """
    Display information about your Character's statistics.

    Usage:
      stats, stat or statistics
    """
    key = "stat"
    aliases = ["statistics", "stats"]

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer
        self.requires_conscious = False  # if true this command requires the caller to be conscious

    def func(self):
        caller = self.caller
        # display name and appearance
        caller.msg("|/", force=True)
        caller.msg(f"Statistics for: |w{caller.name.capitalize()}|n", force=True)
        caller.msg(f"Others who do not know this Character see |o as: |w{caller.usdesc}|n", force=True)
        caller.msg("|/", force=True)
        # show health statistics
        caller.msg("Health:", force=True)
        row1 = list()
        row2 = list()
        for health_stat in ('hp', 'endurance'):
            row1.append(health_stat)
            if hasattr(caller, health_stat):
                health_value = getattr(caller, health_stat, 'Missing post check')
            else:
                health_value = 'Missing'
            row2.append('|w'+str(health_value)+'|n')
        health_list = [row1, row2]
        health_table = evtable.EvTable(table=health_list, border=None, pad_left=4)
        caller.msg(health_table, force=True)
        caller.msg("|/", force=True)
        # show attributes statistics
        caller.msg("Attributes:", force=True)
        row1 = list()
        row2 = list()
        row3 = list()
        row4 = list()
        # loop through statistics attributes
        for short_name, long_name in stats.STAT_MAP_DICT.items():
            # show two stats to a row
            if len(row1) < len(row3):
                first_row = row1
                second_row = row2
            else:
                first_row = row3
                second_row = row4
            # make the attribute clickable
            long_name = highlighter(long_name, click_cmd=f"help {long_name}", up=True)
            first_row.append(long_name)
            stat_value = getattr(caller, short_name, 'Missing')
            second_row.append("|w"+str(stat_value)+'|n')
        stats_list = [row1, row2, row3, row4]
        stats_table = evtable.EvTable(table=stats_list, border=None, pad_left=4)
        caller.msg(stats_table, force=True)
        caller.msg("|/", force=True)


class CmdLook(EvCmdLook, Command):
    # Override look to use UM Command strucure.
    # Adds support for not working when the Character is unconscious.
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Status:
      look requires a Character be conscious

    Time:
      look takes no time to complete

    Observes your location or objects in your vicinity.
    """
    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer

    def custom_req_met(self):
        """
        Verifies commands custom requirements are met.
        If this method returns False the command will end.
        This method must message the caller why the command failed.

        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Automatically called at the end of self.at_pre_cmd.

        Returns:
            requirements_met=boolean
            False: will stop the command
            True: the command will continue
        """
        caller = self.caller
        if self.args:  # a target was provided in command
            if not self.target:  # no target found
                caller.msg(f"You do not see {self.args} here.")
                return False
        else:  # no target was provided in command
            if not caller.location:  # caller has no location
                caller.msg("You have no location to look at!")
                err_msg = f"Command look, caller: {caller.id} | " \
                           "caller has no location."
                error_report(err_msg, caller)
                return False
            else:  # set the command's target to the caller's location
                self.target = caller.location
        return True  # custom requirements met, allow command to run

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        target = self.target
        if not target:
            err_msg = f"Command look, caller: {caller.id} | " \
                       "caller has no location. After func call."
            error_report(err_msg, caller)
            return False
        # process the look
        self.msg((caller.at_look(target), {"type": "look"}), options=None)
        # if the character is looking at something other than the room.
        if not inherits_from(target, "typeclasses.rooms.Room"):
            if inherits_from(target, "typeclasses.rooms.Exit"):
                if target.usdesc in STANDARD_EXITS:  # if the target is a standard exit
                    room_msg = f"{caller.usdesc.capitalize()} looks {target.usdesc}."
                else:
                    room_msg = f"{caller.usdesc.capitalize()} looks through {target.usdesc}."
                caller.location.msg_contents(room_msg, exclude=(caller,))
            else:
                if target is caller: # |o
                    room_msg = f"{caller.usdesc.capitalize()} looks at " \
                               f"{caller.get_pronoun('|o')}self."
                    caller.location.msg_contents(room_msg, exclude=(caller,))
                else:
                    room_msg = f"{caller.usdesc.capitalize()} looks at {target.usdesc}."
                    target_msg = f"{caller.usdesc.capitalize()} looks at you."
                    caller.location.msg_contents(room_msg, exclude=(caller, target))
                    target.msg(target_msg)

# separator used to format help cmd
from django.conf import settings
_DEFAULT_WIDTH = settings.CLIENT_DEFAULT_WIDTH
_SEP = "|C" + "-" * _DEFAULT_WIDTH + "|n"


class CmdHelp(EvCmdHelp):
    """
    View help or a list of topics

    Usage:
      help <topic or command>
      help list
      help all

    This will search for help on commands and other
    topics related to the game.
    """

    key = "help"
    aliases = ["?"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    # suggestion cutoff, between 0 and 1 (1 => perfect match)
    suggestion_cutoff = 0.6

    # number of suggestions (set to 0 to remove suggestions from help)
    suggestion_maxnum = 5

    def msg_help(self, text):
        """
        messages text to the caller, adding an extra oob argument to indicate
        that this is a help command result and could be rendered in a separate
        help window
        """
        if type(self).help_more:
            usemore = True

            if self.session and self.session.protocol_key in ("websocket", "ajax/comet"):
                try:
                    options = self.account.db._saved_webclient_options
                    if options and options["helppopup"]:
                        usemore = False
                except KeyError:
                    pass

            if usemore:
                evmore.msg(self.caller, text, session=self.session, force=True)
                return

        self.msg(text=(text, {"type": "help"}))

    @staticmethod
    def format_help_entry(title, help_text, aliases=None, suggested=None):
        """
        This visually formats the help entry.
        This method can be overriden to customize the way a help
        entry is displayed.

        Args:
            title (str): the title of the help entry.
            help_text (str): the text of the help entry.
            aliases (list of str or None): the list of aliases.
            suggested (list of str or None): suggested reading.

        Returns the formatted string, ready to be sent.

        """
        string = _SEP + "\n"
        if title:
            string += "|CHelp for |w%s|n" % title
        if aliases:
            string += " |C(aliases: %s|C)|n" % ("|C,|n ".join("|w%s|n" % ali for ali in aliases))
        if help_text:
            string += "\n%s" % dedent(help_text.rstrip())
        if suggested:
            string += "\n\n|CSuggested:|n "
            string += "%s" % fill("|C, ".join(f"|w|lchelp {sug}|lt{sug}|le" for sug in suggested))
            #f"|C, |G|lchelp {cmd}|lt{cmd}|le"
        string.strip()
        string += "\n" + _SEP
        return string

    @staticmethod
    def format_help_list(hdict_cmds, hdict_db):
        """
        Output a category-ordered list. The input are the
        pre-loaded help files for commands and database-helpfiles
        respectively.  You can override this method to return a
        custom display of the list of commands and topics.
        """
        string = ""
        if hdict_cmds and any(hdict_cmds.values()):
            string += "\n" + _SEP + "\n   |CCommand help entries|n\n" + _SEP
            for category in sorted(hdict_cmds.keys()):
                string += "\n  |w%s|n:\n" % (str(category).title())
                category_list = hdict_cmds[category]
                string += f"    |C|G|lchelp {category_list[0]}|lt{category_list[0]}|le"
                for cmd in category_list[1:]:
                    # make clickable help commands that strech the screen width
                    string += f"|C, |G|lchelp {cmd}|lt{cmd}|le"
        if hdict_db and any(hdict_db.values()):
            string += "\n\n" + _SEP + "\n\r  |COther help entries|n\n" + _SEP
            for category in sorted(hdict_db.keys()):
                string += "\n\r  |w%s|n:\n" % (str(category).title())
                string += (
                    "|G"
                    + fill(", ".join(sorted([str(topic) for topic in hdict_db[category]])))
                    + "|n"
                )
        return string

    def msg(self, text=None, to_obj=None, from_obj=None, session=None, **kwargs):
        """
        Overriding to allow option to show messages to dead and unconscious Characters
        """
        kwargs.update({"force": True})
        super().msg(text, to_obj, from_obj, session, **kwargs)


class CmdSay(Command):
    """
    speak as your character

    Usage:
      say <message>
      say to <target>, <target> "<message>"
          the first " is required when a target(s) is supplied.
          each target must have a , between the names.

    Example:
      say to blue droid, gray droid "Hello."

    Status
      say requires a Character to be conscious.

    Time
      say requires no time to complete

    Talk to those in your current location.
    """

    key = "say"
    aliases = ['"', "'"]
    locks = "cmd:all()"
    rhs_split = ('=', '"')

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer

    def func(self):
        """Run the say command"""
        caller = self.caller
        # if no speech stop command
        if not self.args:
            say_help = highlighter("help say", click_cmd="help say")
            help_msg = f"What would you like to say.|/Use {say_help}, for help."
            caller.msg(help_msg)
            return
        # if the command starts with string "to" or "at"
        if self.begins_to_or_at:
            if self.rhs:  # if message as a proper break in it
                if self.targets:  # if multiple targets were found
                    targets = self.targets
                    speech = self.rhs.strip('"')  # speech without quotes
                    say_to_or_at = self.begins_to_or_at
                    # message room
                    target_names = objs_sdesc_str(targets)  # get a string of object names
                    room_message = f"{caller.usdesc.capitalize()} says {say_to_or_at} " \
                                   f'{target_names}, "{speech}"'
                    exclude = list(targets)
                    exclude.append(caller)
                    caller.location.msg_contents(room_message, exclude=exclude)
                    # message the caller
                    caller_message = f"You say {say_to_or_at} "
                    caller_message += f'{target_names}, "{speech}"'
                    caller.msg(caller_message)
                    # message targets
                    for receiver in targets:
                        # replace the first instance of the receiver's name with "you"
                        target_names = objs_sdesc_str(targets, receiver)  # get a string of object names
                        receiver_message = f"{caller.usdesc.capitalize()} says {say_to_or_at} "
                        receiver_message += f'{target_names}, "{speech}"'
                        receiver.msg(receiver_message)
                    return
                elif self.target:  # if only one target found
                    target = self.target
                    speech = self.rhs.strip('"')  # speech without quotes
                    say_to_or_at = self.begins_to_or_at
                    room_message = f"{caller.usdesc.capitalize()} says " \
                                   f'{say_to_or_at} {target.usdesc}, "{speech}"'
                    caller.location.msg_contents(room_message, exclude=(caller, target))
                    target_message = f"{caller.usdesc.capitalize()} says " \
                                     f'{say_to_or_at} you, "{speech}"'
                    target.msg(target_message)
                    caller_message = f"You say {say_to_or_at} {target.usdesc}, " \
                                     f'"{speech}"'
                    caller.msg(caller_message)
                    return
        # No special targets, normal say
        speech = self.args
        # Calling the at_before_say hook on the character
        speech = caller.at_before_say(speech)
        if not speech:  # If speech is empty, stop here
            return
        # Call the at_after_say hook on the character
        caller.at_say(speech, msg_self=True)


class CmdWhisper(Command):
    """
    Speak privately as your character to another

    Usage:
      whisper <target> "<message>
      whisper to <target1>, <target2> "<message>"
          the first " is required.
          the " could also be =, to retain mux command support.
          each target must have a , between the names.

    Example:
      whisper to blue droid, gray droid "Hello."

    Status
      whisper requires a Character to be in the ready status.
        If you are whispering to someone it means your attention is focused there.

    Time
      whisper requires no time to complete
    """

    key = "whisper"
    locks = "cmd:all()"
    rhs_split = ('=', '"')

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player

    def func(self):
        """Run the whisper command"""
        caller = self.caller
        # if no speech stop command
        if not self.args:
            whisper_help = highlighter("help whisper", click_cmd="help whisper")
            help_msg = f"What would you like to whisper.|/" \
                       f"Use {whisper_help}, for help."
            caller.msg(help_msg)
            return
        if not self.rhs:
            whisper_help = highlighter("help whisper", click_cmd="help whisper")
            help_msg = f'The first " is required.|/' \
                       f'For example: whisper to door "Hello door."|/' \
                       f'Use {whisper_help}, for help.'
            caller.msg(help_msg)
            return
        if not self.begins_to_or_at:
            begins_to_or_at = 'to'
        else:
            begins_to_or_at = self.begins_to_or_at
        if self.targets:  # if multiple targets were found
            targets = self.targets
            speech = self.rhs.strip('"')  # speech without quotes
            whisper_to_or_at = begins_to_or_at
            # message room
            target_names = objs_sdesc_str(targets)  # get a string of object names
            room_message = f"{caller.usdesc.capitalize()} whispers something {whisper_to_or_at} " \
                           f'{target_names}.'
            exclude = list(targets)
            exclude.append(caller)
            caller.location.msg_contents(room_message, exclude=exclude)
            # message the caller
            caller_message = f"You whisper {whisper_to_or_at} "
            caller_message += f'{target_names}, "{speech}"'
            caller.msg(caller_message)
            # message targets
            for receiver in targets:
                # replace the first instance of the receiver's name with "you"
                target_names = objs_sdesc_str(targets, receiver)  # get a string of object names
                receiver_message = f"{caller.usdesc.capitalize()} whispers {whisper_to_or_at} "
                receiver_message += f'{target_names}, "{speech}"'
                receiver.msg(receiver_message)
            return
        elif self.target:  # if only one target found
            target = self.target
            speech = self.rhs.strip('"')  # speech without quotes
            whisper_to_or_at = begins_to_or_at
            room_message = f"{caller.usdesc.capitalize()} whispers something " \
                           f'{whisper_to_or_at} {target.usdesc}.'
            caller.location.msg_contents(room_message, exclude=(caller, target))
            target_message = f"{caller.usdesc.capitalize()} whispers " \
                             f'{whisper_to_or_at} you, "{speech}"'
            target.msg(target_message)
            caller_message = f"You whisper {whisper_to_or_at} {target.usdesc}, " \
                             f'"{speech}"'
            caller.msg(caller_message)
            return
        else:
            # no target should have already been caught
            err_msg = f"Command whisper, caller: {caller.id} | " \
                       "target not found, but func was still called."
            error_report(err_msg, caller)


class CmdDrop(Command):
    """
    drop something

    Usage:
      drop <obj>

    Status:
      drop requires a Character to be conscious to use.

    Time:
      drop does not take any time to complete.

    Lets you drop an object from your inventory into the
    location you are currently in.
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.search_caller_only = True  # if True the command will only search the caller for targets
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer

    def func(self):
        """Implement command"""
        caller = self.caller
        obj = self.target
        # shoot an error message if there is no target
        if not obj:
            error_report(f"Command drop, caller: {caller.id} | target not found, but func was still called.", caller)
            return
        # prevent dropping worn items that are covered by another worn item.
        elif obj.db.covered_by:
            caller.msg(f"You can't drop that because it's covered by {obj.db.covered_by}.")
            return
        # Inform player worn items must be removed to drop.
        elif obj.db.worn:
            remove_help = highlighter(f"remove {obj.usdesc}", click_cmd=f"remove {obj.usdesc}")
            caller.msg(f"You must remove {obj.usdesc} to drop it.|/Try command {remove_help} to remove it.")
            return
        obj.move_to(caller.location, quiet=True)  # move the object from the Character to the room
        # object being moved will remove itself from Character's hands in Object.at_after_move
        caller.msg(f"You drop {obj.usdesc}.")  # message the caller
        caller.location.msg_contents(f"{caller.usdesc} drops {obj.usdesc}.", exclude=caller)  # message the room
        obj.at_drop(caller)


class CmdGet(Command):
    """
    pick up something

    Usage:
      get <obj>

    status:
      get requires a Character to be in the ready status to use.

    Time:
      get, by default, requires 1 second to complete.
    """

    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.can_not_target_self = True  # if True this command will end with a message if the Character targets themself

    def custom_req_met(self):
        """
        Verifies commands custom requirements are met.
        If this method returns False the command will end.
        This method must message the caller why the command failed.

        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Automatically called at the end of self.at_pre_cmd.

        Returns:
            requirements_met=boolean
            False: will stop the command
            True: the command will continue
        """
        caller = self.caller
        target = self.target
        # check if a hand is open
        open_hands = caller.open_hands()
        # hands are full, stop the command
        if not open_hands:
            stop_message = f"Your hands are full."
            caller.msg(stop_message)
            return False
        # stop the command if the caller is already caring the object.
        if target.location == caller:
            stop_message = f"You are already carrying {target.usdesc}."
            caller.msg(stop_message)
            return False
        return True  # custom requirements met, command can run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        if target.location == caller.location:  # get target is in caller's room
            caller_message = f"You reach for {target.usdesc}."
            caller.msg(caller_message)
            room_message = f"{caller.usdesc.capitalize()} reaches for {target.usdesc}."
            caller.location.msg_contents(room_message, exclude=(caller,))
        else:  # get target is not in callers room
            caller_message = f"You reach into {target.location.usdesc}."
            caller.msg(caller_message)
            room_message = f"{caller.usdesc.capitalize()} reaches into {target.location.usdesc}."
            caller.location.msg_contents(room_message, exclude=(caller,))

    def deferred_action(self):
        """implements the command."""

        caller = self.caller
        obj = self.target

        if not obj.access(caller, "get"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("You can't get that.")
            return

        # calling at_before_get hook method
        if not obj.at_before_get(caller):
            return

        # check if a hand is open
        open_hands = caller.open_hands()
        # hands are full, stop the command
        # this repeat error checking is here itenetionally do not remove
        if not open_hands:
            caller.msg("Your hands are full.")
            return
        else:
            open_hand = open_hands[0]  # hand of the first open hand
        targ_old_location = obj.location  # used to choose message text
        success = obj.move_to(caller, quiet=True)
        if not success:
            caller.msg(f"{obj.usdesc.capitalize()} can not be picked up.")
        else:
            # calling at_get hook method
            obj.at_get(caller)
            # occupy the hand used to get the object
            if open_hand:
                # occupy with dbref to make it very easy to search for items in hand
                open_hand.occupied = obj.dbref
            else:
                err_msg = f"CmdGet, failed for find an instance of the {open_hand} body part."
                error_report(err_msg, caller)
            # message player(s)
            if targ_old_location == caller.location:  # get target is in caller's room
                caller_msg = f"You pick up {obj.usdesc}."
                location_msg = f"{caller.usdesc} picks up {obj.usdesc}."
                caller.location.msg_contents(location_msg, exclude=caller)
            else:  # caller is getting target from container
                caller_msg = f"You get {obj.usdesc} from {targ_old_location.usdesc}."
                location_msg = f"{caller.usdesc.capitalize()} gets {obj.usdesc} " \
                               f"from {targ_old_location.usdesc}."
            caller.msg(caller_msg)
            caller.location.msg_contents(location_msg, exclude=caller)


class CmdPut(Command):
    """
    Put an object in a container

    Usage:
      put <obj> in <container>

    Example:
      put book in bag

    status:
      put requires a Character to be in the ready status to use.

    Time:
      put, by default, requires 1 second to complete.
    """
    key = "put"
    aliases = "stow"
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    rhs_split = ('=', ' in ')

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.can_not_target_self = True  # if True this command will end with a message if the Character targets themself
        self.target_in_hand = False  # if True the target of the command must be in the Characters hand to complete successfully
        self.requires_ready = True  # if true this command requires the ready status before it can do anything.

    def custom_req_met(self):
        """
        Verifies commands custom requirements are met.
        If this method returns False the command will end.
        This command must message the caller.

        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Automatically called in at the self.at_pre_cmd.

        Returns:
            requirements_met=boolean
            False: will stop the command
            True: the command will continue
        """
        caller = self.caller
        target = self.target
        if self.rhs:
            # Command.parse used rhs_split = ('=', ' in ') to collect the containers name in Command.rhs
            container_name = self.rhs.replace(" in ", '', 1)  # get the name of the container
            # find a reference of the container
            container = caller.search(container_name, quiet=True)
            if container:  # a possible container object was found
                container = container[0]  # get the correct target number
                # stop the command if the target can not move to the container
                if not target.at_before_move(container):
                    stop_message = f"{container.usdesc.capitalize()} is not a container."
                    caller.msg(stop_message)
                    return False  # Stop the command from running
                # target can be moved to container, notify caller and location
                self.container = container
                return True  # all custom requirements met, command can run
            else:  # no object of name container_name was found
                stop_message = f"You did not find {container_name} among your " \
                               "possesions or near by."
                caller.msg(stop_message)
                return False  # Stop the command from running
        else:
            cmd_help = highlighter('help put', click_cmd=f"help put", up=True)
            stop_message = f"You must specify a container to place {target.usdesc} into.|/" \
                           f"For a full help use: {cmd_help}"
            caller.msg(stop_message)
            return False  # stop the command from running

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        container = self.container  # collected in self.custom_req_met
        # message caller and Characters in the room
        caller_message = f"You begin to put {target.usdesc} into " \
                         f"{container.usdesc}."
        caller.msg(caller_message)
        room_message = f"{caller.usdesc.capitalize()} begins to put " \
                       f"{target.usdesc} into {container.usdesc}."
        caller.location.msg_contents(room_message, exclude=(caller,))

    def deferred_action(self):
        caller = self.caller
        target = self.target
        container = self.container  # was collected in self.start_message
        if not target.at_before_get(container):
            return
        success = target.move_to(container, quiet=True)
        if success:
            target.at_get(container)
            # object being moved will remove itself from Character's hands in Object.at_after_move
            # message player(s)
            caller.msg(f"You put {target.usdesc} into {container.usdesc}.")
            room_msg = f"{caller.usdesc} puts {target.usdesc} into {container.usdesc}."
            caller.location.msg_contents(room_msg, exclude=caller)
            # calling at_get hook method
            target.at_get(container)
        else:
            caller.msg(f"{target.usdesc.capitalize()} can not be put into " \
                       f"{container.usdesc}.")
            err_msg = f"CmdPut: caller: {caller.dbref}, target: {target.dbref} " \
                      f"container: {container.dbref}. target.move_to returned " \
                      f"false in Command.deferred_action."
            error_report(err_msg, caller)

class CmdInventory(Command):
    """
    view inventory

    Usage:
      inventory
      inv

    Status:
      inventory requires a Character to be in the ready status to use.

    Time:
      inventory, by default, takes 1 second to complete.

    Status and time requirements represent your Character searching through their belongings.

    Shows your inventory.
    """

    # Alternate version of the inventory command which separates
    # worn and carried items.

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command

    def custom_req_met(self):
        """
        Verifies commands custom requirements are met.
        If this method returns False the command will end.
        This method must message the caller why the command failed.

        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Automatically called at the end of self.at_pre_cmd.

        Returns:
            requirements_met=boolean
            False: will stop the command
            True: the command will continue
        """
        caller = self.caller
        if not caller.contents:
            caller.msg("You are not carrying or wearing anything.")
            return False  # requirements not met stop the command
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        caller_pronoun = caller.get_pronoun('|a')
        message = "You rummage through your possessions, taking inventory."
        room_message = f"{caller.usdesc.capitalize()} begings to quickly look through {caller_pronoun} possessions."
        caller.msg(message)
        caller.location.msg_contents(room_message, exclude=(caller,))

    def deferred_action(self):
        """check inventory"""
        caller = self.caller
        items = caller.contents

        carry_table = evtable.EvTable(border="header")
        wear_table = evtable.EvTable(border="header")
        for item in items:
            if not item.db.worn:
                carry_table.add_row("|C%s|n" % item.name, item.db.desc or "")
        if carry_table.nrows == 0:
            carry_table.add_row("|CNothing.|n", "")
        string = "|wYou are carrying:\n%s" % carry_table
        for item in items:
            if item.db.worn:
                wear_table.add_row("|C%s|n" % item.name, item.db.desc or "")
        if wear_table.nrows == 0:
            wear_table.add_row("|CNothing.|n", "")
        string += "|/|wYou are wearing:\n%s" % wear_table
        caller.msg(string)
        # Message the room
        caller_pronoun = caller.get_pronoun('|a')
        room_message = f"{caller.usdesc.capitalize()} completes {caller_pronoun} search."
        caller.location.msg_contents(room_message, exclude=(caller,))


class CmdSit(Command):
    """
    sit down

    Usage:
      sit

    Status:
      sit requires a Character to be in the ready status to use.

    Time:
      sit, by default, takes 1 second to complete.

    Future support:
      add ability to sit on objects; chairs, tables, boxes so on.
    """

    key = "sit"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command

    def custom_req_met(self):
        """
        Verifies commands custom requirements are met.
        If this method returns False the command will end.
        This method must message the caller why the command failed.

        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Automatically called at the end of self.at_pre_cmd.

        Returns:
            requirements_met=boolean
            False: will stop the command
            True: the command will continue
        """
        caller = self.caller
        if caller.position == 'sitting':
            caller.msg("You are already sitting.")
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        message = "You move to sit down."
        room_message = f"{caller.usdesc.capitalize()} moves to sit down."
        caller.msg(message)
        caller.location.msg_contents(room_message, exclude=(caller,))

    def deferred_action(self):
        """Implement command"""
        self.caller.sit()


class CmdStand(Command):
    """
    stand up

    Usage:
      stand

    Status:
      stand requires a Character to be in the ready status to use.

    Time:
      stand, by default, takes 3 seconds to complete.
    """

    key = "stand"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def custom_req_met(self):
        """
        Verifies commands custom requirements are met.
        If this method returns False the command will end.
        This method must message the caller why the command failed.

        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Automatically called at the end of self.at_pre_cmd.

        Returns:
            requirements_met=boolean
            False: will stop the command
            True: the command will continue
        """
        caller = self.caller
        if caller.position == 'standing':
            caller.msg("You are already standing.")
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        message = "You move to stand up."
        room_message = f"{caller.usdesc.capitalize()} moves to stand up."
        caller.msg(message)
        caller.location.msg_contents(room_message, exclude=(caller,))

    def deferred_action(self):
        """Implement command"""
        self.caller.stand()


class CmdLay(Command):
    """
    lay down

    Usage:
      lay

    Status:
      lay requires a Character to be in the ready status to use.

    Time:
      lay, by default, takes 1 second to complete.
    """

    key = "lay"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command

    def custom_req_met(self):
        """
        Verifies commands custom requirements are met.
        If this method returns False the command will end.
        This method must message the caller why the command failed.

        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Automatically called at the end of self.at_pre_cmd.

        Returns:
            requirements_met=boolean
            False: will stop the command
            True: the command will continue
        """
        caller = self.caller
        if caller.position == 'laying':
            caller.msg("You are already laying.")
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        message = "You move to lay down."
        room_message = f"{caller.usdesc.capitalize()} moves to lay down."
        caller.msg(message)
        caller.location.msg_contents(room_message, exclude=(caller,))

    def deferred_action(self):
        """Implement command"""
        self.caller.lay()


class UMRPSystemCmdSet(CmdSet):
    """
    Overridden RP system's commands.

    Reason:
        deny access to commands sdesc, pose and mask to those without builder permision
    """

    def at_cmdset_creation(self):
        self.add(CmdEmote)
        self.add(CmdRecog)
        self.add(CmdSdesc)
        self.add(CmdPose)
        self.add(CmdMask)


class CmdPose(rpsystem.CmdPose):
    # rpsystem overriden CmdPose
    locks = "perm(Builder)"
    help_category = "Building"


class CmdSdesc(rpsystem.CmdSdesc):
    # rpsystem overriden CmdSdesc
    locks = "perm(Builder)"
    help_category = "Building"


class CmdMask(rpsystem.CmdMask):
    # rpsystem overriden CmdMask
    locks = "perm(Builder)"
    help_category = "Building"


class CmdRecog(rpsystem.CmdRecog, Command):
    pass


class CmdEmote(rpsystem.CmdEmote, Command):
    pass
