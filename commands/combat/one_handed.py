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

    def at_init(self):
        """
        Called when the Command object is initialized.
        Created to bulk set local none class attributes.
        This allows for adjusting attributes on the object instances and not having those changes
        shared among all instances of the Command.
        """
        self.dmg_max = 1  # the maximum damage this command can roll
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.can_not_target_self = True  # if True this command will end with a message if the Character targets themself
        self.cmd_type = 'one_handed'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
        self.requires_wielding = True  # require a wielded item type for command to work.
        self.cost_level = 'easy' #  level this action should cost. Acceptable levels: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number
        self.required_ranks = 1  # required ranks in the commands skill_name for this command to work.


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

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        # message the room
        caller_pronoun = caller.get_pronoun('|a')
        room_msg = f"Facing /target /me raises " \
                   f"{self.weapon_desc} preparing an attack."
        caller.location.emote_contents(room_msg, caller, target=target, exclude=(caller))
        # message the caller
        caller_msg = f"Facing /target /me raise " \
                     f"{self.weapon_desc} preparing an attack."
        caller.emote(caller_msg, target=target)

        self.pres_tense_desc = "stabs"  # a present tense description for the action of this command. IE: "kicks"

    def deferred_action(self):
        """Causes the action of the stab command."""
        return self.combat_action()
