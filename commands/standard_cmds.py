from evennia.utils import evtable
from evennia import default_cmds
from evennia.contrib import rpsystem
from evennia import CmdSet
from commands.command import Command


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


class CmdSay(Command):
    """
    speak as your character

    Usage:
      say <message>
      say to <target>, <message>
          the , is required.

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
