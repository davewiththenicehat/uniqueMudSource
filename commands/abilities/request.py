from datetime import datetime

from evennia.utils import gametime
from evennia import CmdSet

from commands.command import Command


class RequestCmdSet(CmdSet):
    """Command set for request commands."""

    def at_cmdset_creation(self):
        """Create request command set."""
        self.add(CmdUniversalTime)


class RequestCommand(Command):
    """
    A command structure for Request commands.

    Inheirits commands.command.Command
    """

    help_category = 'request'

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.cmd_type = 'request'  # Name the command type
        #  level this action should cost.
        # Acceptable levels: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number
        self.cost_level = 'very easy'
        # required ranks in the commands skill_name for this command to work.
        # self.required_ranks = 1
        # self.cost_stat = 'PERM'  # stat this command will use for the action's cost


class CmdUniversalTime(RequestCommand):
    key = "utime"
    aliases = "universal time"
    locks = "cmd:perm(time) or perm(Player)"

    def func(self):
        utime = f"Current time {datetime.fromtimestamp(gametime.gametime(absolute=True))}"
        self.caller.msg(utime)
