from evennia import Command
from evennia import CmdSet


class StunnedCmdSet(CmdSet):
    """
    Locks out commands when character has the stunned state
    """
    key = "stunnedcmdset"
    # https://github.com/evennia/evennia/wiki/evennia.commands.cmdset#cmdset
    priority = 100
    key_mergetype = {"DefaultCharacter": "Replace"}
    duplicates = False  # will not allow for duplicate commands, higher priority replaces
    no_exits = True  # licks out exit commands
    no_objs = True  # prevents searching for objects

    def at_cmdset_creation(self):
        "Called once, when cmdset is first created"
        self.add(CmdBlaze)


class StunnedCommand(Command):
    """
    You are stunned. Many character commands will no longer function.
    """
    key = "stunned"
    locks = "cmd:all()"

    def get_help(self, caller, cmdset):
        """Returns same help string for all commands"""
        return """
    You are sleeping. Many character commands will no longer function.
    """

    def func(self):
        """Let the player know they can't do anything."""
        self.msg("You can not do that while stunnded.")
        return


class CmdBlaze(StunnedCommand):
    """
    There are may things you can not do while you are stunned.
    """
    key = "blaze"


"""
Method taken from:
https://github.com/Arx-Game/arxcode/blob/stable_orphan/commands/cmdsets/sleep.py

Test with:
py self.cmdset.add("commands.stunned.StunnedCmdSet")
run cmmand blaze
py self.cmdset.remove("commands.stunned.StunnedCmdSet")
"""
