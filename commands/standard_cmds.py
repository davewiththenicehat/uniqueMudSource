from evennia.utils import evtable, evmore
from evennia.utils.utils import fill, dedent
from evennia import default_cmds
from evennia.contrib import rpsystem
from evennia import CmdSet
from commands.command import Command
from evennia.commands.default.help import CmdHelp as EvCmdHelp
from evennia.commands.default.system import CmdObjects
from evennia.commands.default.general import CmdLook as EvCmdLook, CmdWhisper as EvCmdWhisper
from world.rules import stats
from utils.um_utils import highlighter



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


class CmdWhisper(EvCmdWhisper, Command):
    """
    Speak privately as your character to another

    Usage:
      whisper <character> = <message>
      whisper <char1>, <char2> = <message>

    Status:
      whisper requires a Character to be in the ready status.
      whispering entails being near someone, focusing on communicating with them.

    Time:
      whisper does not take any time to complete

    Talk privately to one or more characters in your current location, without
    others in the room being informed.
    """


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
    requires_ready = False  # if true this command requires the ready status before it can do anything.


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
      say to <target>, <message>
          the , is required.

    Status
      say requires a Character to be conscious.

    Time
      say requires no time to complete

    Talk to those in your current location.
    """

    key = "say"
    aliases = ['"', "'"]
    locks = "cmd:all()"

    def func(self):
        """Run the say command"""

        caller = self.caller
        if not self.args:  # if no speech stop command
            caller.msg("Say what?")
            return

        # Add support for saying to a target
        if self.args.startswith('to '):
            if len(self.lhslist) > 1: # there is a command in the command
                target_name = self.lhslist[0][2:]  # get a target name after "to "
                target_name = target_name.strip()
                target = caller.search(target_name, quiet=True)  # find the target
                if target:  # if the target exists
                    target = target[0]
                    room_message = f"{caller.usdesc.capitalize()} says to {target.usdesc}, "
                    room_message += f'"{self.lhslist[1]}"'
                    caller.location.msg_contents(room_message, exclude=(caller,))
                    caller_message = f"You say to {target.usdesc}, "
                    caller_message += f'"{self.lhslist[1]}"'
                    caller.msg(caller_message)
                    return

        speech = self.args
        # Calling the at_before_say hook on the character
        speech = caller.at_before_say(speech)
        if not speech:  # If speech is empty, stop here
            return
        # Call the at_after_say hook on the character
        caller.at_say(speech, msg_self=True)


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
    requires_ready = False  # if true this command requires the ready status before it can do anything.

    def func(self):
        """Implement command"""

        caller = self.caller
        if not self.args:
            caller.msg("Drop what?")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        obj = caller.search(
            self.args,
            location=caller,
            nofound_string="You aren't carrying %s." % self.args,
            multimatch_string="You carry more than one %s:" % self.args,
        )
        if not obj:
            return

        # This part is new!
        # You can't drop clothing items that are covered.
        if obj.db.covered_by:
            caller.msg("You can't drop that because it's covered by %s." % obj.db.covered_by)
            return
        # Remove clothes if they're dropped.
        if obj.db.worn:
            obj.remove(caller, quiet=True)

        obj.move_to(caller.location, quiet=True)
        caller.msg("You drop %s." % (obj.name,))
        caller.location.msg_contents("%s drops %s." % (caller.name, obj.name), exclude=caller)
        # Call the object script's at_drop() method.
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

    Picks up an object from your location and puts it in
    your inventory.
    """

    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    defer_time = 1  # time is seconds for the command to wait before running action of command
    can_not_target_self = True  # if True this command will end with a message if the Character targets themself
    target_required = True  # if True and the command has no target, Command.func will stop execution and message the player

    def at_pre_cmd(self):
        """
        Stop the get command if caller already has the object.
        Replace when objects in hand is implimented.
        """
        caller = self.caller
        obj = caller.search(self.args.strip(), quiet=True, location=caller)
        if obj:
            obj = obj[0]
            caller.msg(f"You are already carrying {obj.usdesc}.")
            return True
        return super().at_pre_cmd()

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        message = f"You reach for {target.usdesc}."
        room_message = f"{caller.usdesc.capitalize()} reaches for {target.usdesc}."
        caller.msg(message)
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

        success = obj.move_to(caller, quiet=True)
        if not success:
            caller.msg(f"{obj.usdesc.capitalize()} can not be picked up.")
        else:
            caller.msg(f"You pick up {obj.usdesc}.")
            caller.location.msg_contents(f"{caller.usdesc} picks up {obj.usdesc}.", exclude=caller)
            # calling at_get hook method
            obj.at_get(caller)


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
    defer_time = 1  # time is seconds for the command to wait before running action of command

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

        if not caller.contents:
            caller.msg("You are not carrying or wearing anything.")
            return

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
    defer_time = 1  # time is seconds for the command to wait before running action of command

    def at_pre_cmd(self):
        caller = self.caller
        if caller.position == 'sitting':
            caller.msg("You are already sitting.")
            return True
        return super().at_pre_cmd()

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

    def at_pre_cmd(self):
        caller = self.caller
        if caller.position == 'standing':
            caller.msg("You are already standing.")
            return True
        return super().at_pre_cmd()

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
    defer_time = 1  # time is seconds for the command to wait before running action of command

    def at_pre_cmd(self):
        caller = self.caller
        # do not run command if dead or unconscious, or otherwise not ready
        if super().at_pre_cmd():
            return True
        if caller.position == 'laying':
            caller.msg("You are already laying.")
            return True

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
        self.add(rpsystem.CmdEmote())
        self.add(rpsystem.CmdSay())
        self.add(rpsystem.CmdRecog())
        # commands that have been overridden locally
        self.add(CmdSdesc())
        self.add(CmdPose())
        self.add(CmdMask())


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
