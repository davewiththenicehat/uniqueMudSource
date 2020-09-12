"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia import Command as BaseCommand
from typeclasses.rooms import Room
import random
from evennia import create_object
from random import randint
from evennia import InterruptCommand
from evennia.utils.search import search_tag
from typeclasses.accounts import Account
from world import rules, status_delays
from evennia import default_cmds, utils



class MuxCommand(default_cmds.MuxCommand):
    def at_post_cmd(self):
        "called after self.func()."
        caller = self.caller
        message = f"HP:{caller.db.hp} | XP:{caller.db.xp}"
        caller.msg(message, prompt=True)


class Command(MuxCommand, BaseCommand):
    """
    Inherit from this if you want to create your own command styles
    from scratch.  Note that Evennia's default commands inherits from
    MuxCommand instead.

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    """

# -------------------------------------------------------------
#
# The default commands inherit from
#
#   evennia.commands.default.muxcommand.MuxCommand.
#
# If you want to make sweeping changes to default commands you can
# uncomment this copy of the MuxCommand parent and add
#
#   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
#
# to your settings file. Be warned that the default commands expect
# the functionality implemented in the parse() method, so be
# careful with what you change.
#
# -------------------------------------------------------------

# from evennia.utils import utils
#
#
# class MuxCommand(Command):
#     """
#     This sets up the basis for a MUX command. The idea
#     is that most other Mux-related commands should just
#     inherit from this and don't have to implement much
#     parsing of their own unless they do something particularly
#     advanced.
#
#     Note that the class's __doc__ string (this text) is
#     used by Evennia to create the automatic help entry for
#     the command, so make sure to document consistently here.
#     """
#     def has_perm(self, srcobj):
#         """
#         This is called by the cmdhandler to determine
#         if srcobj is allowed to execute this command.
#         We just show it here for completeness - we
#         are satisfied using the default check in Command.
#         """
#         return super().has_perm(srcobj)
#
#     def at_pre_cmd(self):
#         """
#         This hook is called before self.parse() on all commands
#         """
#         pass
#
#     def at_post_cmd(self):
#         """
#         This hook is called after the command has finished executing
#         (after self.func()).
#         """
#         pass
#
#     def parse(self):
#         """
#         This method is called by the cmdhandler once the command name
#         has been identified. It creates a new set of member variables
#         that can be later accessed from self.func() (see below)
#
#         The following variables are available for our use when entering this
#         method (from the command definition, and assigned on the fly by the
#         cmdhandler):
#            self.key - the name of this command ('look')
#            self.aliases - the aliases of this cmd ('l')
#            self.permissions - permission string for this command
#            self.help_category - overall category of command
#
#            self.caller - the object calling this command
#            self.cmdstring - the actual command name used to call this
#                             (this allows you to know which alias was used,
#                              for example)
#            self.args - the raw input; everything following self.cmdstring.
#            self.cmdset - the cmdset from which this command was picked. Not
#                          often used (useful for commands like 'help' or to
#                          list all available commands etc)
#            self.obj - the object on which this command was defined. It is often
#                          the same as self.caller.
#
#         A MUX command has the following possible syntax:
#
#           name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]
#
#         The 'name[ with several words]' part is already dealt with by the
#         cmdhandler at this point, and stored in self.cmdname (we don't use
#         it here). The rest of the command is stored in self.args, which can
#         start with the switch indicator /.
#
#         This parser breaks self.args into its constituents and stores them in the
#         following variables:
#           self.switches = [list of /switches (without the /)]
#           self.raw = This is the raw argument input, including switches
#           self.args = This is re-defined to be everything *except* the switches
#           self.lhs = Everything to the left of = (lhs:'left-hand side'). If
#                      no = is found, this is identical to self.args.
#           self.rhs: Everything to the right of = (rhs:'right-hand side').
#                     If no '=' is found, this is None.
#           self.lhslist - [self.lhs split into a list by comma]
#           self.rhslist - [list of self.rhs split into a list by comma]
#           self.arglist = [list of space-separated args (stripped, including '=' if it exists)]
#
#           All args and list members are stripped of excess whitespace around the
#           strings, but case is preserved.
#         """
#         raw = self.args
#         args = raw.strip()
#
#         # split out switches
#         switches = []
#         if args and len(args) > 1 and args[0] == "/":
#             # we have a switch, or a set of switches. These end with a space.
#             switches = args[1:].split(None, 1)
#             if len(switches) > 1:
#                 switches, args = switches
#                 switches = switches.split('/')
#             else:
#                 args = ""
#                 switches = switches[0].split('/')
#         arglist = [arg.strip() for arg in args.split()]
#
#         # check for arg1, arg2, ... = argA, argB, ... constructs
#         lhs, rhs = args, None
#         lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
#         if args and '=' in args:
#             lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
#             lhslist = [arg.strip() for arg in lhs.split(',')]
#             rhslist = [arg.strip() for arg in rhs.split(',')]
#
#         # save to object properties:
#         self.raw = raw
#         self.switches = switches
#         self.args = args.strip()
#         self.arglist = arglist
#         self.lhs = lhs
#         self.lhslist = lhslist
#         self.rhs = rhs
#         self.rhslist = rhslist
#
#         # if the class has the account_caller property set on itself, we make
#         # sure that self.caller is always the account if possible. We also create
#         # a special property "character" for the puppeted object, if any. This
#         # is convenient for commands defined on the Account only.
#         if hasattr(self, "account_caller") and self.account_caller:
#             if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
#                 # caller is an Object/Character
#                 self.character = self.caller
#                 self.caller = self.caller.account
#             elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
#                 # caller was already an Account
#                 self.character = self.caller.get_puppet(self.session)
#             else:
#                 self.character = None


class CmdAbilities(Command):
        """
        List abilities

        Usage:
          abilities

        Displays a list of your current ability values.
        """
        key = "abilities"
        aliases = ["abi"]
        lock = "cmd:all()"
        help_category = "General"

        def func(self):
            "implements the actual functionality"

            level, HP, XP, STR, combat = self.caller.get_abilities()
            string = f"level {level}, HP {HP}, XP {XP}, STR {STR}, combat {combat}"
            self.caller.msg(string)

class CmdSetPower(Command):
    """
    set the power of a character

    Usage:
      +setpower <1-10>

    This sets the power of the current character. This can only be
    used during character generation.
    """

    key = "+setpower"
    help_category = "mush"

    def func(self):
        "This performs the actual command"
        errmsg = "You must supply a number between 1 and 10."
        if not self.args:
            self.caller.msg(errmsg)
            return
        try:
            power = int(self.args)
        except ValueError:
            self.caller.msg(errmsg)
            return
        if not (1 <= power <= 10):
            self.caller.msg(errmsg)
            return
        # at this point the argument is tested as valid. Let's set it.
        self.caller.db.power = power
        self.caller.msg("Your Power was set to %i." % power)

# ...

class CmdTestAttack(Command):
    """
    issues an attack

    Usage:
        +attack

    This will calculate a new combat score based on your Power.
    Your combat score is visible to everyone in the same location.
    """
    key = "+attackmush"
    help_category = "mush"

    def func(self):
        "Calculate the random score between 1-10*Power"
        caller = self.caller
        power = caller.db.power
        if not power:
            # this can happen if caller is not of
            # our custom Character typeclass
            power = 1
        combat_score = random.randint(1, 10 * power)
        caller.db.combat_score = combat_score

        # announce
        message = "%s +attack%s with a combat score of %s!"
        caller.msg(message % ("You", "", combat_score))
        caller.location.msg_contents(message %
                                     (caller.key, "s", combat_score),
                                     exclude=caller)

class CmdCreateNPC(Command):
    """
    create a new npc

    Usage:
        +createNPC <name>

    Creates a new, named NPC. The NPC will start with a Power of 1.
    """
    key = "+createnpc"
    aliases = ["+createNPC"]
    locks = "call:not perm(nonpcs)"
    help_category = "mush"

    def func(self):
        "creates the object and names it"
        caller = self.caller
        if not self.args:
            caller.msg("Usage: +createNPC <name>")
            return
        if not caller.location:
            # may not create npc when OOC
            caller.msg("You must have a location to create an npc.")
            return
        # make name always start with capital letter
        name = self.args.strip().capitalize()
        # create npc in caller's location
        npc = create_object("characters.Character",
                      key=name,
                      location=caller.location,
                      locks="edit:id(%i) and perm(Builders);call:false()" % caller.id)
        # announce
        message = "%s created the NPC '%s'."
        caller.msg(message % ("You", name))
        caller.location.msg_contents(message % (caller.key, name),
                                                exclude=caller)


class CmdEditNPC(Command):
    """
    edit an existing NPC

    Usage:
      +editnpc <name>[/<attribute> [= value]]

    Examples:
      +editnpc mynpc/power = 5
      +editnpc mynpc/power    - displays power value
      +editnpc mynpc          - shows all editable
                                attributes and values

    This command edits an existing NPC. You must have
    permission to edit the NPC to use this.
    """
    key = "+editnpc"
    aliases = ["+editNPC"]
    locks = "cmd:not perm(nonpcs)"
    help_category = "mush"

    def parse(self):
        "We need to do some parsing here"
        args = self.args
        propname, propval = None, None
        if "=" in args:
            args, propval = [part.strip() for part in args.rsplit("=", 1)]
        if "/" in args:
            args, propname = [part.strip() for part in args.rsplit("/", 1)]
        # store, so we can access it below in func()
        self.name = args
        self.propname = propname
        # a propval without a propname is meaningless
        self.propval = propval if propname else None

    def func(self):
        "do the editing"

        allowed_propnames = ("power", "attribute1", "attribute2")

        caller = self.caller
        if not self.args or not self.name:
            caller.msg("Usage: +editnpc name[/propname][=propval]")
            return
        npc = caller.search(self.name)
        if not npc:
            return
        if not npc.access(caller, "edit"):
            caller.msg("You cannot change this NPC.")
            return
        if not self.propname:
            # this means we just list the values
            output = f"Properties of {npc.key}:"
            for propname in allowed_propnames:
                output += f"\n {propname} = {npc.attributes.get(propname, default='N/A')}"
            caller.msg(output)
        elif self.propname not in allowed_propnames:
            caller.msg(f"You may only change {', '.join(allowed_propnames)}.")
        elif self.propval:
            # assigning a new propvalue
            # in this example, the properties are all integers...
            intpropval = int(self.propval)
            npc.attributes.add(self.propname, intpropval)
            caller.msg(f"Set {npc.key}'s property {self.propname} to {self.propval}")
        else:
            # propname set, but not propval - show current value
            caller.msg(f"{npc.key} has property {self.propname} = {npc.attributes.get(self.propname, default='N/A')}")


class CmdPoke(Command):
    """
    Pokes someone.

    Usage: poke <target>
    """
    key = "poke"

    def func(self):
        """Executes poke command"""
        target = self.caller.search(self.args.lstrip())
        if not target:
            # we didn't find anyone, but search has already let the
            # caller know. We'll just return, since we're done
            return
        # we found a target! we'll do stuff to them.
        target.msg(f"{self.caller} pokes you.")
        self.caller.msg(f"You poke {target}.")


class CmdNPC(Command):
    """
    controls an NPC

    Usage:
        +npc <name> = <command>

    This causes the npc to perform a command as itself. It will do so
    with its own permissions and accesses.
    """
    key = "+npc"
    locks = "call:not perm(nonpcs)"
    help_category = "mush"

    def parse(self):
        "Simple split of the = sign"
        name, cmdname = None, None
        if "=" in self.args:
            name, cmdname = self.args.rsplit("=", 1)
            name = name.strip()
            cmdname = cmdname.strip()
        self.name, self.cmdname = name, cmdname

    def func(self):
        "Run the command"
        caller = self.caller
        if not self.cmdname:
            caller.msg("Usage: +npc <name> = <command>")
            return
        npc = caller.search(self.name)
        if not npc:
            return
        if not npc.access(caller, "edit"):
            caller.msg("You may not order this NPC to do anything.")
            return
        # send the command order
        npc.execute_cmd(self.cmdname, sessid=caller.sessid)
        caller.msg(f"You told {npc.key} to do '{self.cmdname}'.")

class CmdRoll(Command):

    """
    Play random, enter a number and try your luck.

    Specify two numbers separated by a space.  The first number is the
    number of dice to roll (1, 2, 3) and the second is the expected sum
    of the roll.

    Usage:
      roll <dice> <number>

    For instance, to roll two 6-figure dice, enter 2 as first argument.
    If you think the sum of these two dice roll will be 10, you could enter:

        roll 2 10

    """

    key = "roll"

    def parse(self):
        """Split the arguments and convert them."""
        args = self.args.lstrip()

        # Split: we expect two arguments separated by a space
        try:
            number, guess = args.split(" ", 1)
        except ValueError:
            self.msg("Invalid usage.  Enter two numbers separated by a space.")
            raise InterruptCommand

        # Convert the entered number (first argument)
        try:
            self.number = int(number)
            if self.number <= 0:
                raise ValueError
        except ValueError:
            self.msg(f"{number} is not a valid number of dice.")
            raise InterruptCommand

        # Convert the entered guess (second argument)
        try:
            self.guess = int(guess)
            if not 1 <= self.guess <= self.number * 6:
                raise ValueError
        except ValueError:
            self.msg(f"{self.guess} is not a valid guess.")
            raise InterruptCommand

    def func(self):
        # Roll a random die X times (X being self.number)
        figure = 0
        for _ in range(self.number):
            figure += randint(1, 6)

        self.msg(f"You roll {self.number} dice and obtain the sum {figure}.")

        if self.guess == figure:
            self.msg(f"You played {self.guess}, you have won!")
        else:
            self.msg(f"You played {self.guess}, you have lost.")


class CmdListHangouts(Command):
    """Lists hangouts"""
    key = "hangouts"

    def func(self):
        """Executes 'hangouts' command"""
        hangouts = search_tag(key="hangout", category="location tags")
        self.caller.msg(f"Hangouts available: {', '.join(str(ob) for ob in hangouts)}")


class CmdListEUsers(Command):
    """List user accounts with the letter e in them"""
    key = "userswith"

    def func(self):
        """List accounts with e in them"""
        args = self.args.lstrip()
        message = f"Accounts with {args} in them: "
        queryset = Account.objects.filter(username__contains=args)
        accounts = list(queryset)  # this fills list with matches
        for account in queryset:
            message = message + "" + account.username
        self.caller.msg(message + ".")


class CmdRoomsWithObjCount(Command):
    """List rooms with x number of objects within."""
    key = "roomswithobjects"

    def func(self):
        """List rooms with a number of objects in them"""
        args = int(self.args.lstrip())
        message = f"Rooms with {args} or more objects in them: "
        queryset = Room.objects.all()  # get all Rooms
        rooms = [room for room in queryset if len(room.contents) >= args]
        for room in rooms:
            message = message + room.name
        self.caller.msg(message + ".")

class CmdCheckUnicodeSpacing(Command):
    key = "checkspacing"

    def func(self):
        """prints some unicode characters that should align."""
        self.caller.msg(u'\U0001F3DC\t'+u' '+u' '+u'\u2610'+u' '+u'\t\U0001F332')
        self.caller.msg(u'\U0001F332\t'+u' '+u' '+u'\u2610'+u' '+u'\t\U0001F332')


class CmdAttack(Command):
    """
    attack an opponent

    Usage:
      attack <target>

    This will attack a target in the same room, dealing
    damage with your bare hands.
    """
    key = "attack"
    help_category = "mush"

    def func(self):
        "Implementing combat"

        caller = self.caller

        cool_down = status_delays.get_cool_down(caller)
        if cool_down > 0:
            caller.msg(f"You will be busy for {int(cool_down)} more seconds.")
            return
        stunned_time = status_delays.get_stunned(caller)
        if stunned_time > 0:
            caller.msg(f"You will be stunned for {int(stunned_time)} more seconds.")
            return

        if not self.args:
            caller.msg("You need to pick a target to attack.")
            return

        target = caller.search(self.args)
        if target:
            rules.roll_challenge(caller, target, "combat")
            status_delays.set_cool_down(caller, 5)


class CmdStunSelf(Command):
    """
    Stun yourself to test chaging character's state.

    usage:
        stunself
    """
    key = "stunself"
    help_category = "developer"

    def func(self):
        caller = self.caller
        status_delays.set_stunned(caller, 5)


class CmdDiagnose(Command):
    """
    see how hurt your are

    Usage:
      diagnose [target]

    This will give an estimate of the target's health. Also
    the target's prompt will be updated.
    """
    key = "diagnose"

    def func(self):
        # https://github.com/evennia/evennia/wiki/Tutorial-Searching-For-Objects#searching-using-objectsearch
        if self.args:
            target_name = self.args.lstrip()  # get the string name of desired object. From the commands arguments
            target = self.caller.search(target_name)  # search caller object inventory than room for object with that name
        else:
            target = self.caller

        hp = target.db.hp
        xp = target.db.xp

        if None in (hp, xp):
            # Attributes not defined
            self.caller.msg("Not a valid target!")
            return

        # text = f"{target.name} has {hp} hp"
        # prompt = f"HP: {int(hp)}"
        # self.caller.msg(text, prompt=prompt)
        text = f"You diagnose {target.name} as having {hp} health."
        self.caller.msg(text)


class CmdChangeHP(Command):
    """Used to change hp for testing."""

    key = "sethp"

    def func(self):
        caller = self.caller
        # https://github.com/evennia/evennia/wiki/Tutorial-Searching-For-Objects#searching-using-objectsearch
        if self.args:
            hp = int(self.args.lstrip())  # get the string name of desired object. From the commands arguments
        else:
            caller.msg("Please enter a number to set your HP to.")
            return

        if not isinstance(hp, int):
            caller.msg("Please enter a number to set your HP to.")
            return

        caller.db.hp = hp
        caller.msg(f"Set your hp to {hp}")

class CmdTestColor(Command):
    """Test colors"""

    key = "testcolors"

    def func(self):
        caller = self.caller
# red, green, yellow, blue, magenta, cyan, white and black
        caller.msg("|rRed |RRed")
        caller.msg("|gGreen |GGreen")
        caller.msg("|yYellow |YYellow")
        caller.msg("|bBlue |BBlue")
        caller.msg("|mMangenta |MMagenta")
        caller.msg("|cCyan |CCyan")
        caller.msg("|wWhite |WWhite|n Default")
        caller.msg("|[G|BGreen Back Blue fore")
        caller.msg("|WThis is|/Two Lines")
        caller.msg("|=zmidway gray scale")
        caller.msg("|lcnorth|lt|bGo north|le")


class CmdTestYield(Command):

    """
    A test command just to test waiting.

    Usage:
        test

    """

    key = "testyield"
    locks = "cmd:all()"

    def func(self):
        self.msg("After 5 seconds.")
        yield 5
        self.msg("Afterwards.")


class CmdEcho(Command):
    """
    wait for an echo
    Tests persistent command delays

    Usage:
      echo <string>

    Calls and waits for an echo
    """
    key = "echo"
    locks = "cmd:all()"

    def func(self):
        """
         This is called at the initial shout.
        """
        self.caller.msg("You shout '%s' and wait for an echo ..." % self.args)
        # this waits non-blocking for 10 seconds, then calls echo(self.caller, self.args)
        utils.delay(10, echo, self.caller, self.args, persistent=True)  # changes!


# this is now in the outermost scope and takes two args!
def echo(caller, args):
    "Called after 10 seconds."
    shout = args
    string = "You hear an echo: %s ... %s ... %s"
    string = string % (shout.upper(), shout.capitalize(), shout.lower())
    caller.msg(string)


class CmdTestYieldInput(Command):
    key = "testyieldinput"
    def func(self):
        result = yield("Please enter something:")
        self.caller.msg(f"You entered {result}.")
        result2 = yield("Now enter something else:")
        self.caller.msg(f"You now entered {result2}.")


def callback(caller, prompt, user_input):
    """
    This is a callback you define yourself.

    Args:
        caller (Account or Object): The one being asked
          for input
        prompt (str): A copy of the current prompt
        user_input (str): The input from the account.

    Returns:
        repeat (bool): If not set or False, exit the
          input prompt and clean up. If returning anything
          True, stay in the prompt, which means this callback
          will be called again with the next user input.
    """
    caller.msg(f"When asked '{prompt}', you answered '{user_input}'.")


class CmdTestGet_Input(Command):
    key = "testgetinput"

    def func(self):
        utils.evmenu.get_input(self.caller, "Write something! ", callback)


def yesno(caller, prompt, result):
    if result.lower() in ("y", "yes", "n", "no"):
        caller.msg(f"You entered {result}")
    else:
        # the answer is not on the right yes/no form
        caller.msg(f"Please answer Yes or No. |/{prompt}")
        # returning True will make sure the prompt state is not exited
        return True


class CmdTestGet_Input(Command):
    key = "testyninput"

    def func(self):
        utils.evmenu.get_input(self.caller, "Is Evennia great (Yes/No)?", yesno)
