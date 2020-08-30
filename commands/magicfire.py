from evennia import Command
from evennia import CmdSet


class CmdBlaze(Command):
    """
    echo a message

    Useage:
        blaze
    """

    key = "blaze"

    def func(self):
        caller = self.caller
        location = caller.location

        # no argument given to command - shoot in the air
        message = f"{caller.key} summons blazing fire that lights the room."
        location.msg_contents(message)
        return


class MagicFireCmdSet(CmdSet):
    """
    Grants access to fire command set
    """
    key = "magicfirecmdset"

    def at_cmdset_creation(self):
        "Called once, when cmdset is first created"
        self.add(CmdBlaze())


"""
Running command: @py self.cmdset.add("commands.magicfire.MagicFireCmdSet")
Than rebooting the server, command no longer available. As expected.

run command: @py self.cmdset.add("commands.magicfire.MagicFireCmdSet", permanent=True)
command stays after restarting server, as expected

run command: py self.at_object_creation()
command stays if the objects creation script is rerun.
Obviously dependant on at_objectCreation
"""
