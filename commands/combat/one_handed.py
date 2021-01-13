from commands.command import Command
from evennia import CmdSet
from evennia.utils.logger import log_info, log_warn
from evennia.utils import inherits_from
from world.rules import stats, actions, damage


class OneHandedCmdSet(CmdSet):
    """Command set for one handed combat."""

    def at_cmdset_creation(self):
        """Create one handed command set."""
        self.add(CmdStab)


class OneHandedCommand(Command):
    """
    A command structure for one handed combat.

    Attributes:
        help_category = "one handed"
        can_not_target_self = True  # if True this command will end with a message if the Character targets themself
        target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        cmd_type = 'one_handed'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd

    Inheirits commands.command.Command
    """

    help_category = "one handed"
    target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
    cmd_type = 'one_handed'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
    required_wielding = "one_handed"  # require a wielded item type for command to work.
    dmg_max = 1  # the maximum damage this command can cause
    can_not_target_self = True  # if True this command will end with a message if the Character targets themself
    cost_level = 'mid' #  level this action should cost. Acceptable levels: 'low', 'mid', 'high'

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.

        If overridden call super().at_init()
        """
        super().at_init()  # uncomment when overridden



class CmdStab(OneHandedCommand):
    """
    A basic fast one handed attack.

    Modifier:
      observation
      one handed ranks
      punch ranks
    Damage:
      stab does minimum of 1 damage.
      stab's max damage is determined by the onehanded weapon your Character is wielding.
      punch's damage is modifider by strength damage modifier.
    Dodge:
      stab is evaded by agility.
    Time:
      stab's default completion time is 3 seconds.
    Requires:
      Your Character to be wielding a one handed weapon.
      Your Character's status must be ready.
    """

    key = "stab"
    defer_time = 3  # time is seconds for the command to wait before running action of command
    desc = "stabs"  # a present tense description for the action of this command. IE: "kicks"

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller_pronoun = self.caller.get_pronoun('|a')
        message = f"Facing {self.target.usdesc} {self.caller.usdesc} raises " \
                  f"{self.weapon_desc} preparing an attack."
        self.caller.location.msg_contents(message)

    def deferred_action(self):
        """Causes the action of the stab command."""
        return self.combat_action()
