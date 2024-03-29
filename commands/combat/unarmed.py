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

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.dmg_types = {'BLG': 0}  # dictionary of damage types this command can manipulate.
        self.unarmed_str_mod = 0  # half of the unarmed command caller's strength modifier
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.can_not_target_self = True  # if True this command will end with a message if the Character targets themself
        self.cmd_type = 'unarmed'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
        self.cost_level = 'easy' #  level this action should cost. Acceptable levels: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number
        self.required_ranks = 1  # required ranks in the commands skill_name for this command to work.
        self.range = [self.caller.location]  # caller and target must be in the same room.
        self.requires_standing = True  # Does this command require caller to be standing? False by default

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

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        super().set_instance_attributes()
        self.dmg_max = 2  # the maximum damage this command can roll
        self.pres_tense_desc = "punches"  # a present tense description for the action of this command. IE: "kicks"

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        self.weapon_desc = "fist"  # weapon description that will show up in Command.combat_action's automated messages
        caller_pronoun = self.caller.get_pronoun('|a')
        room_msg = f"Facing /target /me pulls {caller_pronoun} hand back preparing an attack."
        caller.location.emote_contents(room_msg, caller, target=target, exclude=(caller))
        #message caller
        caller_msg = f"Facing /target you pull your hand back preparing an attack."
        caller.emote(caller_msg, target=target)

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

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        super().set_instance_attributes()
        self.dmg_max = 4  # the maximum damage this command can roll
        self.defer_time = 5  # time is seconds for the command to wait before running action of command
        self.pres_tense_desc = "kicks"  # a present tense description for the action of this command. IE: "kicks"
        self.cost_level = 'hard' #  level this action should cost. Acceptable levels: 'very easy', 'easy', 'moderate' 'hard', 'daunting' or a number

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        target = self.target
        caller = self.caller
        self.weapon_desc = "foot"  # weapon description that will show up in Command.combat_action's automated messages
        caller_pronoun = self.caller.get_pronoun('|a')
        room_msg = f"Facing /target /me lifts {caller_pronoun} knee up preparing an attack."
        caller.emote_location(room_msg, target)
        caller.emote(f"Facing /target you lift your knee up preparing an attack.", target)
        # This is a slow powerful command, ask target if they would like to dodge.
        self.stop_request(target=target, stop_cmd='dodge')

    def deferred_action(self):
        """Causes the action of the kick command."""
        action_mod = self.unarmed_str_mod
        return self.combat_action(action_mod)
