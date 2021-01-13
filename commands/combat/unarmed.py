from commands.command import Command
from evennia import CmdSet
from evennia.utils.logger import log_info, log_warn
from evennia.utils import inherits_from
from world.rules import stats, actions, damage


class UnarmedCmdSet(CmdSet):
    """Command set for unarmed combat."""

    def at_cmdset_creation(self):
        """Create unarmed command set."""
        self.add(CmdPunch)
        self.add(CmdKick)


class UnarmedCommand(Command):
    """
    A command structure for unarmed combat.

    Methods:
        at_pre_cmd, has been overridden to collect half of a Characters strength action modifier.
            Saves is as self.unarmed_str_mod

    Attributes:
        unarmed_str_mod = int()  # half of the Characters.STR_action_mod
        help_category = "unarmed"
        can_not_target_self = True  # if True this command will end with a message if the Character targets themself
        target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        cmd_type = 'unarmed'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
        unarmed_str_mod = 0  # half of the unarmed command caller's strength modifier

    Inheirits commands.command.Command
    """

    help_category = "unarmed"
    target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
    cmd_type = 'unarmed'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
    unarmed_str_mod = 0  # half of the unarmed command caller's strength modifier
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
        self.dmg_types = {'BLG': 0}  # dictionary of damage types this command can manipulate.

    def at_pre_cmd(self):
        """
        Gets half of the unarmed command caller's strength modifier.
        Store is as Command.unarmed_str_mod.
        """
        caller = self.caller
        if hasattr(caller, 'STR_action_mod'):
            str_action_mod = getattr(caller, 'STR_action_mod')
            str_action_mod *= .5
            self.unarmed_str_mod = stats.stat_round(str_action_mod)
        return super().at_pre_cmd()


class CmdPunch(UnarmedCommand):
    """
    A basic fast unarmed attack.

    Modifier:
      observation and half of the Characters strength action modifier.
      unarmed ranks
      punch ranks
    Damage:
      punch does 1 or 2 damage.
      punch's damage is modifider by strength damage modifier.
    Dodge:
      punch is evaded by agility.
    time:
      punch's default completion time is 3 seconds.
    """

    key = "punch"
    defer_time = 3  # time is seconds for the command to wait before running action of command
    dmg_max = 2  # the maximum damage this command can cause
    cmd_type = 'unarmed'  # Should be a string of the command type. IE: 'evasion' for an evasion command
    desc = "punches"  # a present tense description for the action of this command. IE: "kicks"

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        self.weapon_desc = "fist"  # weapon description that will show up in Command.combat_action's automated messages
        caller_pronoun = self.caller.get_pronoun('|a')
        message = f"Facing {self.target.usdesc} {self.caller.usdesc} pulls {caller_pronoun} hand back preparing an attack."
        self.caller.location.msg_contents(message)

    def deferred_action(self):
        """Causes the action of the punch command."""
        action_mod = self.unarmed_str_mod
        return self.combat_action(action_mod)


class CmdKick(UnarmedCommand):
    """
    A basic slow unarmed attack.

    Modifier:
      kick is modified with observation and half of the Characters strength action modifier.
    Damage:
      kick does 1 to 4 damage.
      kick's damage is modifider by strength damage modifier.
    Dodge:
      kick is evaded by agility.
    time:
      kick's default completion time is 5 seconds.
    """

    key = "kick"
    defer_time = 5  # time is seconds for the command to wait before running action of command
    dmg_max = 4  # the maximum damage this command can cause
    desc = "kicks"  # a present tense description for the action of this command. IE: "kicks"
    cost_level = 'high' #  level this action should cost. Acceptable levels: 'low', 'mid', 'high'

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        target = self.target
        caller = self.caller
        self.weapon_desc = "foot"  # weapon description that will show up in Command.combat_action's automated messages
        caller_pronoun = self.caller.get_pronoun('|a')
        message = f"Facing {target.usdesc} {caller.usdesc} lifts {caller_pronoun} knee up preparing an attack."
        caller.location.msg_contents(message)
        # This is a slow powerful command, ask target if they would like to dodge.
        self.stop_request(target=target, stop_cmd='dodge')

    def deferred_action(self):
        """Causes the action of the kick command."""
        action_mod = self.unarmed_str_mod
        return self.combat_action(action_mod)
