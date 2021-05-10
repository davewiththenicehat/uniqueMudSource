"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from typeclasses.mixins import CharExAndObjMixin, AllObjectsMixin
from evennia.contrib.gendersub import GenderCharacter, _RE_GENDER_PRONOUN
from utils.element import Element, ListElement
from utils import um_utils
from world import status_functions
from evennia import utils
from world.rules import stats, body, damage, actions, skills as skills_rules
from evennia.contrib.rpsystem import ContribRPCharacter
from typeclasses.equipment.clothing import ClothedCharacter
from evennia.contrib.rpsystem import RPSystemCmdSet
from evennia import DefaultScript

# Used to adjust Element settings for stats, and the unit test for Character also
# min_func ascending_breakpoint_func and descending_breakpoint_func are set in self.at_init
CHARACTER_STAT_SETTINGS = {
    'name': None,  # name of the Element, highly recommend leaving default
    'min': -100,  # the min number the Element can be, if reached min_func runs
    # 'min_func': None,  # reference to a function to run when the self.value attribute reaches self.min
    'breakpoint': 0,  # number a breakpoint point occurs like falling unconshious or an object breakpoint
    # 'descending_breakpoint_func': None,  # When passed descending_breakpoint_func runs
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
        Many attributes are inheirited, refer to the docstring of that object for details.
            It is very likely what you are looking for is in typeclasses.mixins.CharExAndObjMixin
        ONLY interact with Elements via the characters Element reference.
            Do not change the database entries directly
            Do not change the protected _attribute_name attribute directly
        If a Character attribute is not described here, or in inheirited docstring it is not intended to be interacted with.

        Character stats are referenced as uppercase abbriviations.
        Character stats are instance of utils.Elements
        Character stats have a max value of 200
        In the database as Elements they are refered to in full name form.
        Example:
            self.STR # is strength
            In the database is would be saved as strength_value
        Full list of stats:
            self.STR  # strength
                adjusts max carry weight
                The default dmg_mod_stat for physical attack commands
            self.CON  # constitution
                Adjusts max hp.
                adjusts max endurance
            self.OBS  # observation
                The default action_mod_stat for physical attack commands
            self.AGI  # agility
                Default evade_mod_stat for physical attack commands
            self.SPD  # speed
                Adjusts completion time of most busy status commands
            self.INT  # intelligence
                The default dmg_mod_stat for special attacks commands
            self.WIS  # wisdom
                adjusts max sanity
                Default evade_mod_stat for mental attack commands
            self.CHR  # charisma
                Adjusts NPC shop buying and selling prices

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
            targetable = True  # can this object be targeted with an action
            container = False  # Can the object contain other objects

        usdesc = self.sdesc.get()  # a property to easy get and set the short description on an object.
            usdesc is intended for rare instance where the emote system can not apply a name to a second target.
        position=str, used to control if character is sitting standing laying.
            full list of positions in world.rules.body.POSITIONS
            This is a python property and will control setting database.
            It will not allow you to incorrectly set the position.
            Usesage:
                character_position = char.position
                char.position = "standing"
                char.position = "not standing"  # this will throw a ValueError
                del char.position  # will set position to "standing"
                    It is important that position exist. It should not be deleted
        condition=ListElement, an object to represent a Character's condition.
            Exmaple: char.condition.dead, char.condition.unconscious
            Interact with as a list Element
            char.condition.dead = True, this will be saved to the database.
            All conditions are the negative form of the condition.
                For example dead rather than alive.
            Do not interect with database entries for Elements directly.
                Manage them through the element. char.condition.attribute_name
        condition.unconscious, special note: Refer to self.set_unconscious() for full details.

        skills=object, skills is a blank object that contains ListElement of objects.
            Each of those objects contains a skill set.
            ListElements function very simular to python's dict obect.
                Full reference: utils.Element.ListElement
            For example:
                skills.unarmed, to access the unarmed skill set.
            The ListElement contains
                For each skill name:
                    skill_name, ranks in this skill
                    skill_name_exp, experience with this skill
                    skill_name_msg, If the new rank available msg should be shown.
                skill_points, skill points in this skill set.
                    Not there is one for each skill set.


        evd_max=ListElement, determins the roll_max of each stat in evade_roll.
            There is one for every stat in stats.STATS
            Example: char.evd_max.AGI or char.evd_max.WIS
            Usage:
                This is used in world.rules.actions.evade_roll.
                It determins the minimum evade roll for this Character in the
                corrisponding stat.
                For complete rules refer to world.rules.actions.evade_roll
                Change with:
                    char.evd_max.STAT_NAME = #
                    Example: char.evd_max.AGI = 3

    Methods:
        All methods are fully documented in their docstrings.
        get_pronoun(pattern), pattern is a gendersub pattern, returns Character's pronoun
        ready(), returns True if a character is ready for a 'busy' action
        stun(int() or float()), stun the Character for argument seconds
        status_stop(status_type=str, stop_message=str, stop_cmd=str), stop a stun status early
        status_stop_request(stop_message=None, stop_cmd=None), Request for a player to stop a status.
        cache_stat_modifiers(), Creates "Stat modifiers" mentioned in the Attributes section of this docstring
        at_msg_receive(force=None, force_on_unconscious=None), a Character will silence messages when they are unconscious or dead.
            To force reciving a certain message always use the force kwarg.
            This is also the argument to use to force a message when a Character is dead.
                Example:
                    char.msg('This is a message', force=True)
                    room.msg_contents('this is a message', force=True)
            To force reciving a certain message when the Character is unconscious use the force_on_unconscious kwarg.
            Example:
                char.msg('This is a message', force_on_unconscious=True)
                room.msg_contents('this is a message', force_on_unconscious=True)
        hands(), returns a list of references of Characters hands.
            As it is in self.body.***_hand
            This can include objects that are not hands or are not left_hand right_hand.
        open_hands(), returns a list of references of Characters hands that are open.
            As it is in self.body.***_hand
            This can include objects that are not hands or are not left_hand right_hand.
        is_holding(obj), Returns True if the object reference passed is in the Character's hand.
        wielding(), Returns a list of object instances the character is wielding
                    or an empty list if the Character is wielding no objects.
        is_wielding(self, obj), Returns a reference of the hand wielding the object passed.
            Returns false if the object is not being wielded by the Character

    Scripts
        Character.NaturalHealing, heals Character automatically over time.

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
        self.END  # init endurance
        return super().at_init()  # call at_init below this one, ie typeclasses.mixins.CharExAndObjMixin

    def at_object_creation(self):
        """Runs when Character is created."""
        self.at_init()  # initialize self.
        self.targetable = True  # Characters can be targeted with commands
        self.container = True  # Can the object contain other objects
        self.position = 'standing'  # Default position is standing
        # if it does not already exist, create a healing script
        if "Natural_Healing" not in str(self.scripts):
            self.scripts.add(NaturalHealing)
        super_return = super().at_object_creation()  # itentionally before RPSystemCmdSet removal
        self.cmdset.remove(RPSystemCmdSet)  # overridden and added back in at commands.standard_cmds.UMRPSystemCmdSet
        return super_return


    @property
    def skills(self):
        """
        Create object to hold characters' skill sets.

        Each skill set name is a ListElement.
        Reference utils.Element.ListElement
        The ListElement keys are:
            skill_name, for each skill name
            skill_name_exp, for each skill name
                skills current experience value
            skill_name_msg, for each skill name
                rank training available message has been shown.
            skill_points, One instance.
        The lists used to create these objects are in a dictionary world.rules.skill.SKILLS

        An example useage:
            if char.skills.unarmed.kick > 1:
                pass
            if char.skills.unarmed.kick_exp > 1:
                pass
        """
        try:
            if self._skills:
                pass
        except AttributeError:
            # create an empty object
            self._skills = type('_skills', (object,), {})()
            self._skills  # initialize the empty object
            self._skills.skills = skills_rules.SKILLS  # make copy of the skills dictionary
            # ListElements will want to know what its db method is
            self._skills.attributes = self.attributes
            for skill_set_name, skill_names in skills_rules.SKILLS.items():
                # create attributes to represent skill sets
                skill_var_names = list()
                for skill_name in skill_names:
                    if skill_name == 'skill_points':
                        continue
                    skill_var_names.append(skill_name+'_exp')
                    skill_var_names.append(skill_name+'_msg')
                skill_var_names = tuple(skill_var_names)
                setattr(self._skills, skill_set_name, ListElement(self._skills, skill_names+skill_var_names))
                # verify the newly created Element
                set_inst = getattr(self._skills, skill_set_name)
                set_inst.verify()
        return self._skills


    @property
    def learning(self):
        """Bool attribute to track if a Character is learning a skill."""
        return self.attributes.get('learning', False)

    @learning.setter
    def learning(self, value):
        if value:
            self.attributes.add('learning', True)
        else:
            self.attributes.remove('learning')

    @learning.deleter
    def learning(self):
        self.attributes.remove('learning')

    # define objects's condition
    @property
    def condition(self):
        try:
            if self._condition:
                pass
        except AttributeError:
            self._condition = ListElement(self, body.CHARACTER_CONDITIONS)
            self._condition.verify()
        return self._condition

    @condition.setter
    def condition(self, value):
        self._condition.set(value)

    @condition.deleter
    def condition(self):
        self._condition.delete()

    # define characters's position ('sitting', 'standing', 'laying')
    @property
    def position(self):
        """Get the Chracter.position attribute."""
        return self.db.position

    @position.setter
    def position(self, position):
        """set Character.position attribute. Checking for incorrect value."""
        if isinstance(position, str):
            position = position.lower()
            if position in body.POSITIONS:  # verify it is an allowed position
                self.db.position = position
                self.db.pose = f'is {position} here.'
            else:
                raise ValueError(f"Character ID {self.id}.stance, {position} is not an allowed position. Positions are: {body.POSITIONS}")
        else:
            raise ValueError(f"Character ID {self.id}.stance, can not be set to non str 'non-string' value")

    @position.deleter
    def position(self):
        """
        Deleter for Character.position.
        Simply returns Character to default position of 'standing'.
        Does NOT delete the attribute.
        """
        self.db.position = 'standing'

    @property
    def usdesc(self):
        """
        Universal method to get and set an object's description.
        Stands for Universal Short Description.

        A usdesc exists on each evennia object type Object, Character, Room and
        Exit.

        usdesc refers to self.key on Exits, Objects and rooms.
        usdesc refers to self.sdesc on Characters.

        Usage:
           caller.msg(f'You attack {target.usdesc}.)  # to get
           target.usdesc = 'a happy tree'  # to set

        Notes:
            usdesc is intended for rare instance where the emote system can not
            apply a name to a second target. Than there is no single receiver for
            obj.get_display_name(receiver).
        """
        return self.sdesc.get()

    @usdesc.setter
    def usdesc(self, value):
        """Setter property for usdesc"""
        self.sdesc.add(value)

    # define objects's evd_max
    @property
    def evd_max(self):
        """
        Adjusted the roll_max used in world.rules.actions.evade_roll.
        """
        try:
            if self._evd_max:
                pass
        except AttributeError:
            self._evd_max = ListElement(self, stats.STATS)
            self._evd_max.verify()
            for stat in stats.STATS:
                setattr(self._evd_max, stat, actions.EVADE_MAX)
        return self._evd_max

    @evd_max.setter
    def evd_max(self, value):
        self._evd_max.set(value)

    @evd_max.deleter
    def evd_max(self):
        self._evd_max.delete()

    # define a character's willpower
    @property
    def WILL(self):
        try:
            if self.willpower:
             pass
        except AttributeError:
            self.willpower = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.willpower.verify()
            self.willpower.modifier_stat = 'WIS'
        return self.willpower

    @WILL.setter
    def WILL(self, value):
        self.willpower.set(value)

    @WILL.deleter
    def WILL(self):
        self.willpower.delete()
        del self.willpower

    # define characters's endurance
    @property
    def END(self):
        try:
            if self.endurance:
                pass
        except AttributeError:
            self.endurance = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.endurance.verify()
            self.endurance.modifier_stat = 'CON'
        return self.endurance

    @END.setter
    def END(self, value):
        self.endurance.set(value)

    @END.deleter
    def END(self):
        self.endurance.delete()
        del self.endurance

    # define characters's strength
    @property
    def STR(self):
        try:
            if self.strength:
                pass
        except AttributeError:
            self.strength = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.strength.verify()
        return self.strength

    @STR.setter
    def STR(self, value):
        self.strength.set(value)

    @STR.deleter
    def STR(self):
        self.strength.delete()
        del self.strength

    # define characters's constitution
    @property
    def CON(self):
        try:
            if self.constitution:
                pass
        except AttributeError:
            self.constitution = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.constitution.verify()
        return self.constitution

    @CON.setter
    def CON(self, value):
        self.constitution.set(value)

    @CON.deleter
    def CON(self):
        self.constitution.delete()
        del self.constitution

    # define characters's observation
    @property
    def OBS(self):
        try:
            if self.observation:
                pass
        except AttributeError:
            self.observation = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.observation.verify()
        return self.observation

    @OBS.setter
    def OBS(self, value):
        self.observation.set(value)

    @OBS.deleter
    def OBS(self):
        self.observation.delete()
        del self.observation

    # define characters's agility
    @property
    def AGI(self):
        try:
            if self.agility:
                pass
        except AttributeError:
            self.agility = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.agility.verify()
        return self.agility

    @AGI.setter
    def AGI(self, value):
        self.agility.set(value)

    @AGI.deleter
    def AGI(self):
        self.agility.delete()
        del self.agility

    # define characters's speed
    @property
    def SPD(self):
        try:
            if self.speed:
                pass
        except AttributeError:
            self.speed = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.speed.verify()
        return self.speed

    @SPD.setter
    def SPD(self, value):
        self.speed.set(value)

    @SPD.deleter
    def SPD(self):
        self.speed.delete()
        del self.speed

    # define characters's intelligence
    @property
    def INT(self):
        try:
            if self.intelligence:
                pass
        except AttributeError:
            self.intelligence = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.intelligence.verify()
        return self.intelligence

    @INT.setter
    def INT(self, value):
        self.intelligence.set(value)

    @INT.deleter
    def INT(self):
        self.intelligence.delete()
        del self.intelligence

    # define characters's wisdom
    @property
    def WIS(self):
        try:
            if self.wisdom:
                pass
        except AttributeError:
            self.wisdom = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.wisdom.verify()
        return self.wisdom

    @WIS.setter
    def WIS(self, value):
        self.wisdom.set(value)

    @WIS.deleter
    def WIS(self):
        self.wisdom.delete()
        del self.wisdom

    # define characters's charisma
    @property
    def CHR(self):
        try:
            if self.charisma:
                pass
        except AttributeError:
            self.charisma = Element(self, 100, **CHARACTER_STAT_SETTINGS)
            self.charisma.verify()
        return self.charisma

    @CHR.setter
    def CHR(self, value):
        self.charisma.set(value)

    @CHR.deleter
    def CHR(self):
        self.charisma.delete()
        del self.charisma

    def ready(self, conscious_only=False):
        """Check if player is ready for a command that requires a ready status.
        This command is automatically called in Command.defer.
        It will handle the player notification message automatically.

        Args:
            conscious_only (bool): if True, only check if Character is conscious.
                Default is False.

        Returns:
            is_ready (bool): True if the Character is ready. False if it is not.

        """
        # Player is not ready if they are unconscious or dead
        if self.condition.dead:
            self.msg("You can not do that while dead.", force=True)
            return False
        if self.condition.unconscious:
            self.msg("You can not do that while unconscious.", force_on_unconscious=True)
            return False
        if conscious_only:  # stop running if only testing consciousness
            return True
        # Player is not ready if they have a status active.
        for status_type in status_functions.STATUS_TYPES:
            if self.attributes.has(status_type):
                delay_remaining = status_functions.status_delay_get(self, status_type)
                if delay_remaining > 0:
                    plural_sec = 's' if delay_remaining > 1.99 else ''
                    self.msg(f'You will be {status_type} for {round(delay_remaining)} second{plural_sec}.')
                    return False  # Tell command character is currently occupied
        return True  # player is ready

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

    def status_stop(self, status_type='busy', stop_message=None, stop_cmd=None, stopper=None):
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
        return status_functions.status_force_stop(self, stop_message, stop_cmd, status_type, stopper)

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
                message = f'caller.get_display_name(target) left an opening, dodge?'
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
            # restoration_mod(caller, stat_type, log=False)
            mod_value = stats.restoration_mod(self, stat_type)
            mod_name = stat_type + '_restoration_mod'
            setattr(self, mod_name, mod_value)
        setattr(self, 'hp_max_mod', stats.hp_max_mod(self))
        setattr(self, 'endurance_max_mod', stats.endurance_max_mod(self))
        setattr(self, 'sanity_max_mod', stats.sanity_max_mod(self))
        setattr(self, 'load_max_mod', stats.load_max_mod(self))
        setattr(self, 'busy_mod', stats.busy_mod(self))
        setattr(self, 'stunned_mod', stats.stunned_mod(self))
        setattr(self, 'purchase_mod', stats.purchase_mod(self))

    def stand(self):
        """
        Cause the Charter to stand up.
        unit test in commands.tests
        """
        return self.set_position('standing')

    def sit(self):
        """
        Cause the Charter to sit down.
        unit test in commands.tests
        """
        return self.set_position('sitting')

    def lay(self):
        """
        Cause the Charter to lay down.
        unit test in commands.tests
        """
        return self.set_position('laying')

    def set_position(self, position):
        """
        Change a character's position.

        Arguments:
            position, str of a position.
                example: 'sitting', 'standing' or 'laying'
                Full list in world.rules.body.POSITIONS
            quiet=False, if True no messages will be displayed to the room.
            force=False, change position even if player is in that position

        Includes:
            checking if the character is already in that position.
            messaging the Character and room

        unit test in commands.tests

        todo:
            support for sitting or laying on objects
            Make it use the ready function
        """
        if position not in body.POSITIONS:
            raise ValueError(f"Character ID {self.id}.stance, {position} is not an allowed position. Positions are: {body.POSITIONS}")
        self.position = position
        return True

    def set_unconscious(self, state=True):
        """
        Change a characters conscious state.

        Arguments:
            state=True, True for unconscious and False for conscious

        Notes:
            if a character is unconscious they will not have access to:
                any commands that require the ready state, Character.ready()
                    commands.Command.at_pre_cmd and commands.Command.defer
                movement
                    typeclasses.exits.UMExitCommand
                evade attacks
                    rules.actions.targeted_action
                Have very limited access to msg
                    typeclasses.characters.Character.at_msg_receive
                        Mostly as it offers a kwarg for msg, force_on_unconscious
                        force a message to unconscious Character with
                            char.msg(message, force_on_unconscious=True)

            character pose while unconscious unit test is in commands.tests

        to do:

        """
        # if already in the passed state, do nothing
        if state == self.condition.unconscious:
            return

        self.condition.unconscious = state  # Set the unconscious state

        if state:  # if setting unconscious to True
            # stop any deffered commands
            self.status_stop()
            self.msg('You fall unconscious.', force=True)
            self.position = 'laying'
            self.db.pose = 'is unconscious here.'
            room_msg = "/Me falls unconscious."
            self.emote_location(room_msg)
        else:  # setting unconscious to False
            self.msg('You recover consciousness.', force=True)
            self.db.pose = f'is {self.position} here.'
            room_msg = "/Me recovers consciousness."
            self.emote_location(room_msg)

    def at_msg_receive(self, text=None, from_obj=None, **kwargs):
        """
        This hook is called whenever someone sends a message to this
        object using the `msg` method.

        Note that from_obj may be None if the sender did not include
        itself as an argument to the obj.msg() call - so you have to
        check for this. .

        Consider this a pre-processing method before msg is passed on
        to the user session. If this method returns False, the msg
        will not be passed on.

        Args:
            text (str, optional): The message received.
            from_obj (any, optional): The object sending the message.

        Kwargs:
            This includes any keywords sent to the `msg` method.
            force_on_unconscious=False, show message even if Character is unconscious
            force=False, show message to Character under any circumstance.

        Returns:
            receive (bool): If this message should be received.

        Notes:
            If this method returns False, the `msg` operation
            will abort without sending the message.

        """
        # if force message is sent, always send the message.
        if kwargs.get('force', False):
            return True

        # silent messages when Character is unconscious
        if self.condition.unconscious:
            # force the message if character is unconscious, but no other silencing conditions
            if kwargs.get('force_on_unconscious', False):
                return True
            return False

        # silent messages when Character is dead.
        # Only the force kwarg will show a message when the Character is dead
        if self.condition.dead:
            return False

        # no silent conditions found, show message
        return True

    def heal(self, modifier=0, ammount=None):
        """
        Heal the Character.

        Arguments:
            modifier=0, number to add to the max restoration to heal by.
            ammount=None, a set ammount to heal by.
                If passed heal will ignore the standard heal check

        Notes:
            This function passes directly to Character.restore_stat
        """
        self.restore_stat(self.hp, modifier, ammount)

    def restore_stat(self, stat, modifier=0, ammount=None):
        """
        Restore a stat on a Character

        Arguments:
            stat, a reference of the stat to be restored
            modifier=0, number to add to the max restoration to restore by.
            ammount=None, a set ammount to restore by.
                If passed restore_stat will ignore the standard restore check

        Notes
            This is registered on a script, NaturalHealing.
            This script is created in at_object_creation
        """
        # dead Characters can not restore
        if self.condition.dead:
            return
        if ammount:  # if ammount pass restore by that ammount
            stat.set(stat + ammount)
            return
        # restore according to Character's natural healing
        cost_mod_type = stat.name # if this stat has no modifier_stat, default to itself
        if stat:
            # each cost attribute (hp, END, will) has a modifier_stat. types are stats WIS, END so on
            cost_mod_type = getattr(stat, 'modifier_stat', cost_mod_type)
        else: # an instance of the stat is required, cost has to be taken from something
            error_message = f"Character.restore_stat, character: {self.id}, Failed to receive an instance of {stat.name} on character."
            um_utils.error_report(error_message, self)
            return False
        # adjust restoration by the stat's restoration modifider.
        restoration_modifier = getattr(stat, f"{cost_mod_type}_restoration_mod", 0)
        restoration_modifier += modifier
        stat.set(stat + damage.restoration_roll(restoration_modifier))
        # If this restoration was hp, and the character is concious, wake them.
        if stat.name == 'hp':
            if self.condition.unconscious:
                if self.hp > self.hp.breakpoint:
                    self.wake_check()

    def wake_check(self):
        """
        Will hold future code to test if a character wakes from unconciousness.
        Currently just wakes the Character if hp is above the hp breakpoint (normally 0)
        """
        self.set_unconscious(False)

    def ascending_breakpoint(self):
        """
        This is automatically called when an object's hp rises above it's breakpoint (likely 0), when it was previous below it's breakpoint.
        Here to be overridden.

        Overriding for Characters
        """
        self.wake_check()

    def at_before_say(self, message, **kwargs):
        """
        Called before the object says or whispers anything, return modified message.

        Here to overload rpsystem's at_before_say
        """
        return message

    # define an empty hands dictionary
    HANDS = dict()

    def hands(self):
        """
        returns a list of references of Characters hands

        Returns:
            list of hand references

        Example:
        hands_state = char.hands()
        for hand in hands_state:  # loop through instances of hands that are open
            if hand.broke:  # check if the hand is broke
                pass
            if hand.missing:  # check if the hand is missing
                pass

        note:
            Some character races may have many hands or hands with odd names.
            Avoid using right_hand left_hand logic.

            Tested in commands.tests
        """
        hands_state = list()
        for hand in self.HANDS:
            hand_inst = getattr(self.body, hand, False)
            if hand_inst:
                hands_state.append(hand_inst)
                # if the item held has been delete or otherwise does not exist, unoccupy the hand
                if hand_inst.occupied:
                    item_held = self.search(hand_inst.occupied, quiet=True)
                    if not item_held:  # item does not exist in database
                        # the item is also being wielded
                        if hand_inst.occupied == hand_inst.wielding:
                            hand_inst.wielding = 0  # unwield the missing item
                        hand_inst.occupied = 0  # unoccupy the hand
        return hands_state

    def open_hands(self):
        """
        Returns:
            a list of references to attributes from self.body for each open hand or an empty
            list if hands are occupied.

            Example:
            open_hands = char.open_hands()
            if not open_hands:  # would trigger when Character's hands are full.
                pass
            open_hand = open_hands[0]  # open_hand is now a reference of the first open hand
            for hand in open_hands:  # loop through instances of hands that are open
                if hand.broke:  # check if the hand is broke
                    pass
                if hand.missing:  # check if the hand is missing
                    pass
        note:
            Some character races many have many hands or hands with odd names.
            Avoid using right_hand left_hand logic.

            Tested in commands.tests
        """
        open_hands = list()
        hands_state = self.hands()
        for hand in hands_state:
            if not hand.occupied:
                open_hands.append(hand)
        return open_hands

    def is_holding(self, obj):
        """
        If the character is holding the object, an instance of the hand holding it is returned.
        """
        hands_state = self.hands()
        for hand in hands_state:
            if hand.occupied:
                if hand.occupied == obj.dbref:
                    return hand
        return False

    def wielding(self):
        """
        Returns a list of object instances the character is wielding
        or an empty list if the Character is wielding no objects.

        Example:
            if not caller.wielding():  # triggers when character is not wielding an item
                pass
            items_equipped = caller.wielding()
            for item in items_equipped:
                if isinstance()

            Tested in commands.tests
        """
        hands_state = self.hands()
        wielded_items = list()
        for hand in hands_state:
            if hand.wielding:
                wielded_item = self.search(hand.wielding, quiet=True)
                if wielded_item:
                    wielded_item = wielded_item[0]
                    wielded_items.append(wielded_item)
        return wielded_items

    def is_wielding(self, obj):
        """
        Returns a reference of the hand wielding the object passed.
        Returns false if the object is not being wielded by the Character

        Arguments:
            obj: a reference of the object the Character may be wielding

        Notes:
            Tested in commands.tests
        """
        hands_state = self.hands()
        for hand in hands_state:
            if hand.wielding:
                wielded_item = self.search(hand.wielding, quiet=True)
                if wielded_item:
                    wielded_item = wielded_item[0]
                    if wielded_item == obj:
                        return hand
        return False

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.

        Keyword Args:
            pose (bool): Include the pose (if available) in the return.

        Returns:
            name (str): A string of the sdesc containing the name of the object,
            if this is defined.
                including the DBREF if this user is privileged to control
                said object.

        Notes:
            The RPCharacter version of this method colors its display to make
            characters stand out from other objects.

        """
        idstr = "(#%s)" % self.id if self.access(looker, access_type="control") else ""
        if looker == self:
            sdesc = self.key
        else:
            try:
                recog = looker.recog.get(self)
            except AttributeError:
                recog = None
            sdesc = recog or (hasattr(self, "sdesc") and self.sdesc.get()) or self.key
        pose = " %s" % (self.db.pose or "is here.") if kwargs.get("pose", False) else ""
        return f"{sdesc}{idstr}{pose}"

    def process_sdesc(self, sdesc, obj, **kwargs):
        """
        Allows to customize how your sdesc is displayed (primarily by
        changing colors).

        Args:
            sdesc (str): The sdesc to display.
            obj (Object): The object to which the adjoining sdesc
                belongs. If this object is equal to yourself, then
                you are viewing yourself (and sdesc is your key).
                This is not used by default.

        Returns:
            sdesc (str): The processed sdesc ready
                for display.

        """
        return f"|b{sdesc}|n"

class NaturalHealing(DefaultScript):
    """
    Script to control when Character's natural healing

    rules
        make restoration pause if character moves while bearing a load
            Make this pause longer for greater loads.
    """

    def at_script_creation(self):
        self.key = "Natural_Healing"
        self.interval = damage.HEALING_INTERVAL  # reapeat time
        self.persistent = True  # survies a reboot

    def at_repeat(self):
        # Heal when the script interval time passes
        char = self.obj
        char.restore_stat(char.hp)
        char.restore_stat(char.END)
