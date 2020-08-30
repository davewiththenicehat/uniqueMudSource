from evennia import Command
from evennia import CmdSet


class CmdShoot(Command):
    """
    Firing the mech’s gun

    Usage:
      shoot [target]

    This will fire your mech’s main gun. If no
    target is given, you will shoot in the air.
    """
    key = "shoot"
    aliases = ["fire", "fire!"]

    def func(self):
        "This actually does the shooting"

        caller = self.caller
        location = caller.location

        if not self.args:
            # no argument given to command - shoot in the air
            message = "BOOM! The mech fires its gun in the air!"
            location.msg_contents(message)
            return

        # we have an argument, search for target
        target = caller.search(self.args.strip())
        if target:
            message = f"BOOM! The mech fires its gun at {target.key}"
            location.msg_contents(message)


class CmdLaunch(Command):
    # make your own 'launch'-command here as an exercise!
    # (it's very similar to the 'shoot' command above).
    pass  # remove pass when you make your CmdLaunch method


class MechCmdSet(CmdSet):
    """
    This allows mechs to do do mech stuff.
    """
    key = "mechcmdset"

    def at_cmdset_creation(self):
        "Called once, when cmdset is first created"
        self.add(CmdShoot())
        self.add(CmdLaunch())
