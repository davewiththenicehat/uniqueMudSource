from commands.command import Command
from evennia import CmdSet
from evennia.utils.logger import log_info, log_warn
from world.rules import stats, actions


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

    Inheirits commands.command.Command
    """

    help_category = "unarmed"
    target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
    cmd_type = 'unarmed'  # Should be a string of the cmd type. IE: 'evasion' for an evasion cmd
    unarmed_str_mod = 0  # half of the unarmed command caller's strength modifier

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
        punch is dodged by agility.
    time:
        punch's default completion time is 3 seconds.
    Returns:
        True, if the command completed successfully
    """

    key = "punch"
    defer_time = 3  # time is seconds for the command to wait before running action of command
    dmg_max = 2  # the maximum damage this command can cause
    cmd_type = 'unarmed'  # Should be a string of the command type. IE: 'evasion' for an evasion command

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller_pronoun = self.caller.get_pronoun('|a')
        message = f"Facing {self.target.name} {self.caller.name} pulls {caller_pronoun} hand back preparing an attack."
        self.caller.location.msg_contents(message)

    def deferred_action(self):
        """Causes the action of the punch command."""
        # verify the target is still in range
        caller = self.caller
        target_name = self.lhs.strip()
        target = self.caller.search(target_name, quiet=True)
        if not target:
            caller.msg(f'You can no no longer reach {target_name}.')
            return False
        target = self.target
        result, action_result, dodge_result = actions.targeted_action(caller, target)
        result += self.unarmed_str_mod
        caller_message = f"{self.key} {action_result} VS evade {dodge_result}: You {self.key} at {target.name} "
        target_message = f"evade {dodge_result} VS {self.key} {action_result}: You attempt to evade {caller.name}'s {self.key} "
        room_message = f"{caller.name} {self.key}es at {target.name} and "
        if result > 0:
            damage = actions.dmg_roll(self)
            if damage > 0:  # make certain punch can not heal
                target.hp -= damage
            caller_message += f"and connect. Dealing {damage} damage."
            target_message += f"but fail. Receiving {damage} damage."
            room_message += "connects."
            self.successful(True)
        else:
            caller_message += "but miss."
            target_message += "and are successful."
            room_message += "misses."
            self.successful(False)
        caller.msg(caller_message)
        target.msg(target_message)
        caller.location.msg_contents(room_message, exclude=(target, caller))
        return True


class CmdKick(UnarmedCommand):
    """
    A basic slow unarmed attack.

    Modifier:
        kick is modified with observation and half of the Characters strength action modifier.
    Damage:
        kick does 1 to 4 damage.
        kick's damage is modifider by strength damage modifier.
    Dodge:
        kick is dodged by agility.
    time:
        kick's default completion time is 5 seconds.
    """

    key = "kick"
    defer_time = 5  # time is seconds for the command to wait before running action of command
    dmg_max = 4  # the maximum damage this command can cause

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        target = self.target
        caller = self.caller
        caller_pronoun = self.caller.get_pronoun('|a')
        message = f"Facing {target.name} {caller.name} lifts {caller_pronoun} knee up preparing an attack."
        caller.location.msg_contents(message)
        # This is a slow powerful command, ask target if they would like to dodge.
        target.status_stop_request(stop_cmd='dodge')

    def deferred_action(self):
        """Causes the action of the kick command."""
        caller = self.caller
        target_name = self.lhs.strip()
        target = self.caller.search(target_name, quiet=True)
        if not target:
            caller.msg(f'You can no no longer reach {target_name}.')
            return False
        target = self.target
        result, action_result, dodge_result = actions.targeted_action(caller, target)
        result += self.unarmed_str_mod
        caller_message = f"{self.key} {action_result} VS evade {dodge_result}: You {self.key} at {target.name} "
        target_message = f"evade {dodge_result} VS {self.key} {action_result}: You attempt to evade {caller.name}'s {self.key} "
        room_message = f"{caller.name} {self.key}s at {target.name} and "
        if result > 0:
            damage = actions.dmg_roll(self)
            if damage > 0:  # make certain unarmed attack can not heal
                target.hp -= damage
            caller_message += f"and connect. Dealing {damage} damage."
            target_message += f"but fail. Receiving {damage} damage."
            room_message += "connects."
            self.successful(True)
        else:
            caller_message += "but miss."
            target_message += "and are successful."
            room_message += "misses."
            self.successful(False)
        caller.msg(caller_message)
        target.msg(target_message)
        caller.location.msg_contents(room_message, exclude=(target, caller))
        return True
