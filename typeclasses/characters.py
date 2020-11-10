"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from typeclasses.mixins import CharExAndObjMixin, AllObjectsMixin
from evennia.contrib.gendersub import GenderCharacter, _RE_GENDER_PRONOUN
from utils.element import Element
from world import status_functions
from evennia import utils
from world.rules import stats
from evennia.contrib.rpsystem import ContribRPCharacter
from typeclasses.equipment.clothing import ClothedCharacter

# Used to adjust Element settings for stats, and the unit test for Character also
CHARACTER_STAT_SETTINGS = {
    'name': None,  # name of the Element, highly recommend leaving default
    'min': -100,  # the min number the Element can be, if reached min_func runs
    'min_func': None,  # reference to a function to run when the self.value attribute reaches self.min
    'breakpoint': 0,  # number a breakpoint point occurs like falling unconshious or an object breakpoint
    'breakpoint_func': None,  # When passed breakpoint_func runs
    'max': 100,  # the max number the Element can be. When reached self.max_fun() runs
    'max_func': None,  # reference to a function to run when the self.value attribute reachs the self.max
    'dbtype': 'db'  # the database type to use can be 'db' or 'ndb'
}


class Character(AllObjectsMixin, CharExAndObjMixin, ClothedCharacter, GenderCharacter, ContribRPCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    INHERITS:
        evennia.contrib.gendersub.GenderCharacter
            A simple gender-aware Character class.
        evennia.contrib.rpsystem.ContribRPCharacter
            Roleplaying base system for Evennia
        typeclasses.mixins.CharExAndObjMixin
            Creates basic attributes that exist on all typeclasses.objects.Objects and typeclasses.characters.Character objects.
        typeclasses.mixins.AllObjectsMixin

    ATTRIBUTES:
        ONLY interact with Elements via the characters Element reference.
            Do not change the database entries directly
            Do not change the protected _attribute_name attribute directly
        If a Character attribute is not described here, it is not intended to be interacted with.

        Character stats are referenced as uppercase abbriviations.
        Character stats are instance of utils.Elements
        Character stats have a max value of 200
        In the database as Elements they are refered to in full name form.
        Example:
            self.STR # is strength
            In the database is would be saved as strength_value
        Full list of stats:
            self.STR  # strength
            self.CON  # constitution
            self.OBS  # observation
            self.AGI  # agility
            self.SPD  # speed
            self.INT  # intelligence
            self.WIS  # wisdom
            self.CHR  # charisma

        Stat modifiers:
            All stat modifiers are cached on Characters as local attributes.
            To view a full list run command: 'view_obj =stat_cache', to view all local attributes of self.
            Examples:
                char.STR_evade_mod, char.CON_action_mod, char.OBS_action_cost_mod

            Stats change: when stats change on a Character method Character.cache_stat_modifiers() needs to be called.

        Inheirited from CharExAndObjMixin:
            A large number of attributes are inheirited from CharExAndObjMixin.
            refer to CharExAndObjMixin doc string for full details.
            Nearly all variables that are used in combat are inheiried from CharExAndObjMixin.
            There are several methods inherited also.


        inheirited from AllObjectsMixin
            targetable = True  # can this exit be targeted with an action

        usdesc = self.sdesc.get()  # a property to easy get and set the short description on an object.
            Use as if it were a stanard attribute.
            usdesc = 'a happy tree'
            caller.msg(f'You attack {target.usdesc}.')

    Methods:
        All methods are fully documented in their docstrings.
        self.get_pronoun(pattern), pattern is a gendersub pattern, returns Character's pronoun
        self.ready(), returns True if a character is ready for a 'busy' action
        self.stun(int() or float()), stun the Character for argument seconds
        self.status_stop(status_type=str, stop_message=str, stop_cmd=str), stop a stun status early
        status_stop_request(stop_message=None, stop_cmd=None), Request for a player to stop a status.
        cache_stat_modifiers(), Creates "Stat modifiers" mentioned in the Attributes section of this docstring

    Final Notes:
        unit testing for Character status is done in the commands.tests.TestCommands unit test
        unit testing for hp is done in utils.tests.TestUtils.test_elements
    """

    def at_init(self):
        """
        This is always called whenever this object is initiated --
        that is, whenever it its typeclass is cached from memory. This
        happens on-demand first time the object is used or activated
        in some way after being created but also after each server
        restart or reload.

        UniqueMud:
            Used to cache stat modifiers.
        """
        self.cache_stat_modifiers()  # load stats cache when Character is initialized.
        return super().at_init()  # call at_init below this one, ie typeclasses.mixins.CharExAndObjMixin:

    def at_object_creation(self):
        """Runs when Character is created."""
        self.targetable = True
        return super().at_object_creation()

    # define characters's strength
    @property
    def STR(self):
        try:
            if self._strength:
                pass
        except AttributeError:
            self._strength = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._strength

    @STR.setter
    def STR(self, value):
        self._strength.set(value)

    @STR.deleter
    def STR(self):
        self._strength.delete()
        del self._strength

    # define characters's constitution
    @property
    def CON(self):
        try:
            if self._constitution:
                pass
        except AttributeError:
            self._constitution = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._constitution

    @CON.setter
    def CON(self, value):
        self._constitution.set(value)

    @CON.deleter
    def CON(self):
        self._constitution.delete()
        del self._constitution

    # define characters's observation
    @property
    def OBS(self):
        try:
            if self._observation:
                pass
        except AttributeError:
            self._observation = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._observation

    @OBS.setter
    def OBS(self, value):
        self._observation.set(value)

    @OBS.deleter
    def OBS(self):
        self._observation.delete()
        del self._observation

    # define characters's agility
    @property
    def AGI(self):
        try:
            if self._agility:
                pass
        except AttributeError:
            self._agility = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._agility

    @AGI.setter
    def AGI(self, value):
        self._agility.set(value)

    @AGI.deleter
    def AGI(self):
        self._agility.delete()
        del self._agility

    # define characters's speed
    @property
    def SPD(self):
        try:
            if self._speed:
                pass
        except AttributeError:
            self._speed = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._speed

    @SPD.setter
    def SPD(self, value):
        self._speed.set(value)

    @SPD.deleter
    def SPD(self):
        self._speed.delete()
        del self._speed

    # define characters's intelligence
    @property
    def INT(self):
        try:
            if self._intelligence:
                pass
        except AttributeError:
            self._intelligence = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._intelligence

    @INT.setter
    def INT(self, value):
        self._intelligence.set(value)

    @INT.deleter
    def INT(self):
        self._intelligence.delete()
        del self._intelligence

    # define characters's wisdom
    @property
    def WIS(self):
        try:
            if self._wisdom:
                pass
        except AttributeError:
            self._wisdom = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._wisdom

    @WIS.setter
    def WIS(self, value):
        self._wisdom.set(value)

    @WIS.deleter
    def WIS(self):
        self._wisdom.delete()
        del self._wisdom

    # define characters's charisma
    @property
    def CHR(self):
        try:
            if self._charisma:
                pass
        except AttributeError:
            self._charisma = Element(self, 100, **CHARACTER_STAT_SETTINGS)
        return self._charisma

    @CHR.setter
    def CHR(self, value):
        self._charisma.set(value)

    @CHR.deleter
    def CHR(self):
        self._charisma.delete()
        del self._charisma

    def ready(self):
        """
        Check if player is ready for a command that requires a ready state.
        This command is automatically called in Command.defer.
        It will handle the player notification message automatically.

        Usage:
            if Character.ready():
        """
        for status_type in status_functions.STATUS_TYPES:
            if self.attributes.has(status_type):
                delay_remaining = status_functions.status_delay_get(self, status_type)
                if delay_remaining > 0:
                    plural_sec = 's' if delay_remaining > 1.99 else ''
                    self.msg(f'You will be {status_type} for {round(delay_remaining)} second{plural_sec}.')
                    return False  # Tell command character is currently occupied
        return True

    def get_pronoun(self, pattern):
        """
        Returns a Character's pronoun.
        Requires a GenderSub regex pattern, which are:
            `|s`, `|S`: Subjective form: he, she, it, He, She, It, They
            `|o`, `|O`: Objective form: him, her, it, Him, Her, It, Them
            `|p`, `|P`: Possessive form: his, her, its, His, Her, Its, Their
            `|a`, `|A`: Absolute Possessive form: his, hers, its, His, Hers, Its, Theirs

        usage:
            Character.get_pronoun(pattern)

        Example:
            char_pos_pronoun = char.get_pronoun('|p')
        """
        return _RE_GENDER_PRONOUN.sub(self._get_pronoun, pattern)

    def stun(self, stun_time=3):
        """
        Stun this character for a time.

        Usage:
            char.stun(3)  # stuns char for 3 seconds

        Upgrade options:
            Allow a follow up command to be completed when the stun time is over.
        """
        if not isinstance(stun_time, int) or isinstance(stun_time, float):
            stun_time = float(stun_time)
        stun_time = 3 if not stun_time else stun_time
        stun_time = 10 if stun_time > 10 else stun_time
        status_functions.status_delay_set(self, None, stun_time, 'stunned')

    def status_stop(self, status_type='busy', stop_message=None, stop_cmd=None):
        """
        Remove a status from a this character.
        Returns True if the status was successfully stopped.
        Has a sister method in Command.stop_forced

        Supports:
            all status types
            Showing a message to the receiver
            running a follow up command after the status is removed
            Returns True if the status was successfully stopped.

        Arguments:
            status_type = 'stunned' | 'busy'  # the status type being ended
            stop_message = str()  # A message to display when the status ends.
                Note the "You are no longer status_type." message will still show.
            stop_cmd = str()  # A command that is Character.execute_cmd compabible.
                Example stop_cmd = 'look'

        Examples:
            From within a command
            self.caller.status_stop('stunned', "Stunned stopped message successful.", 'test_cmd')
        """
        return status_functions.status_force_stop(self, stop_message, stop_cmd, status_type)

    def status_stop_request(self, stop_message=None, stop_cmd=None):
        """
        Request for a player to stop a status.
        status_stop_request will verify that the target has a deffered command.
        If stop_cmd was provided and there is no deffered command.
            stop_request will suggest the stop_cmd to the target.
        Returns True if the command was successfully stopped.

        Arguments:
            stop_message=str, message shown to target.
                Default: f'Stop your {target.nbd.deffered_command.key} command?'
            stop_cmd=str, command to run if the stop request is done.
                Default: None
                Example: 'look'

        Reason:
            Allows for support of commands that allow for openings.
            Possible to receive assistance from someone else.
            Much more.

        Useage:
            If not calling on self:
                call within Command.func or Command.deffered_action methods
                message = f'{self.caller.usdesc} left an opening, dodge?'
                target.status_stop_request(message, 'dodge')
            If calling on self
                message = 'You are at 20 hp, would you like to teleport home?'
                target.status_stop_request(message, 'tel home')

        Limitations:
            Is NOT compatible with settings.MULTISESSION_MODE = 3
            Only supports requesting a stop for the 'busy' status

        References:
        https://github.com/evennia/evennia/wiki/EvMenu#the-get_input-way
        """
        if self.nattributes.has('deffered_command'):
            if not stop_message:
                stop_message = f'Stop your {self.ndb.deffered_command.key} command'
            self_sessions = self.sessions.get()
            self.ndb.cmd_stop_request = status_functions.status_user_request_stop
            if stop_cmd:
                utils.evmenu.get_input(self, f"{stop_message} to |lc{stop_cmd}|lt{stop_cmd}|le? 'y' for yes or 'i' to ignore.",
                                       self.ndb.cmd_stop_request, self_sessions, stop_cmd)
            else:
                utils.evmenu.get_input(self, f"{stop_message}? 'y' for yes or 'i' to ignore.",
                                       self.ndb.cmd_stop_request, self_sessions)
            return True
        else:  # if no command is waiting, suggest the stop_cmd
            if stop_cmd:
                self.msg(f'You may want to |lc{stop_cmd}|lt{stop_cmd}|le.')
            return False

    def cache_stat_modifiers(self):
        """
        Create a cache of meaningful ability modifiers.
        To view a full list run command: 'view_obj =stat_cache', to view all local attributes of self.
        Code to view stat cache is in commands.developer_cmds.CmdViewObj.view_cache_stat_modifiers

        Example caches:
            char.STR_evade_mod, char.CON_action_mod, char.OBS_action_cost_mod
        """
        stats_dictionary = stats.STAT_MAP_DICT
        for stat_type, long_name in stats_dictionary.items():
            mod_value = stats.evade_mod(self, stat_type)
            mod_name = stat_type + '_evade_mod'
            setattr(self, mod_name, mod_value)
            mod_value = stats.action_mod(self, stat_type)
            mod_name = stat_type + '_action_mod'
            setattr(self, mod_name, mod_value)
            mod_value = stats.action_cost_mod(self, stat_type)
            mod_name = stat_type + '_action_cost_mod'
            setattr(self, mod_name, mod_value)
            mod_value = stats.dmg_mod(self, stat_type)
            mod_name = stat_type + '_dmg_mod'
            setattr(self, mod_name, mod_value)
        setattr(self, 'hp_max_mod', stats.hp_max_mod(self))
        setattr(self, 'endurance_max_mod', stats.endurance_max_mod(self))
        setattr(self, 'sanity_max_mod', stats.sanity_max_mod(self))
        setattr(self, 'load_max_mod', stats.load_max_mod(self))
        setattr(self, 'busy_mod', stats.busy_mod(self))
        setattr(self, 'stunned_mod', stats.stunned_mod(self))
        setattr(self, 'purchase_mod', stats.purchase_mod(self))

    @property
    def usdesc(self):
        """
        Universal method to get and set an object's description.
        Universal Short Description

        A usdesc exists on each evennia object type Object, Character, Room and Exit

        usdesc refers to self.key on Exits, Objects and rooms
        usdesc refers to self.sdesc on Characters

        Usage:
           caller.msg(f'You attack {target.usdesc}.)  # to get
           target.usdesc = 'a happy tree'  # to set
        """
        return self.sdesc.get()

    @usdesc.setter
    def usdesc(self, value):
        """Setter property for usdesc"""
        self.sdesc.add(value)
