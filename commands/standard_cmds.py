from evennia.utils import evtable
from evennia.commands.default.muxcommand import MuxCommand
from evennia import default_cmds

class StandardCmdsCmdSet(default_cmds.CharacterCmdSet):
    """
    Collection of very basic game command.
    That have no specific grouping.
    That must in some way be altered from evennias provided version.
    examples drop, inventory

    Unit tests for these commands are in commands.tests.TestClothingCmd
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        self.add(CmdDrop)
        self.add(CmdInventory)

class CmdDrop(MuxCommand):
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


class CmdInventory(MuxCommand):
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

    def func(self):
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
