from commands.command import Command
from evennia import CmdSet
from evennia.utils.logger import log_info, log_warn
from world.rules import stats, actions


class EvasionCmdSet(CmdSet):
    """Command set for evading attacks."""

    def at_cmdset_creation(self):
        """Create unarmed command set."""
        self.add(CmdDodge)


class EvasionCommand(Command):
    """
    A command structure for evasion.

    Methods:
        at_pre_cmd , has been overridden to create a message to display when the character attempts to evade
            saves as self.evade_msg

    Attributes:
        self.evade_msg, message to display when the character attempts to evade

    Reason:
        Evasion commands adjust the default evasion rules in rules.actions.evade_roll
        If an attack is received by the Character with an active evasion command:
            evade_roll will use the Evasion commands roll_max over the default
            evade_roll will automatically stop this command and display a message to players in the room


    Inheirits commands.command.Command
    """

    help_category = 'evasion'

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.cmd_type = 'evasion'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
        self.cost_level = 'very easy' #  level this action should cost. Acceptable levels: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number
        self.required_ranks = 1  # required ranks in the commands skill_name for this command to work.
        self.defer_time = 10  # time is seconds for the command to wait before running action of command
        self.evade_msg = f'to {self.key} the incoming attack.'


class CmdDodge(EvasionCommand):
    """
    A basic evasion action to avoid an attack.

    Modifier:
        dodge is modified with observation and half of the Characters strength action modifier.
        evasion ranks
        dodge ranks
    Damage:
        dodge does not affect the loss of health
    time:
        by default dodge will stay active for 5 seconds or an attack is received.
    Returns:
        True, if the command completed successfully
    """

    key = "dodge"

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        room_message = f'/Me begins to sway warily.'
        caller_message = 'You begin to sway warily.'
        caller.location.emote_contents(room_message, caller, exclude=(caller))
        caller.msg(caller_message)

    def deferred_action(self):
        """The command completed, without receiving an attack."""
        caller = self.caller
        room_message = f'/Me stops swaying warily.'
        caller.location.emote_contents(room_message, caller, exclude=(caller))
        caller.msg('You stop moving warily.')
