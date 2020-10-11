"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from typeclasses.mixins import ObjectBaseMixin
from evennia.contrib.gendersub import GenderCharacter
from utils.element import Element

# Used to adjust Element settings for stats, and the unit test for Character also
ATTRIBUTE_SETTINGS = {
    'name': None,  # name of the Element, highly recommend leaving default
    'min': 0,  # the min number the Element can be, if reached min_func runs
    'min_func': None,  # reference to a function to run when the self.value attribute reaches self.min
    'breakpoint': 0,  # number a breakpoint point occurs like falling unconshious or an object breakpoint
    'breakpoint_func': None,  # When passed breakpoint_func runs
    'max': 200,  # the max number the Element can be. When reached self.max_fun() runs
    'max_func': None,  # reference to a function to run when the self.value attribute reachs the self.max
    'dbtype': 'db'  # the database type to use can be 'db' or 'ndb'
}


class Character(ObjectBaseMixin, GenderCharacter):
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

    ATTRIBUTES:
        Character attributes are referenced as uppercase abbriviations.
        In the database as Elements they are refered to in full name form.
        Example:
            self.STR # is strength
            In the database is would be saved as strength_value
            ONLY interact with Elements via the characters Element reference.
                Do not change the database entries directly
                Do not change the protected _attribute_name attribute directly
        Full list of attributes:
            self.STR  # strength
            self.CON  # constitution
            self.OBS  # observation
            self.AGI  # agility
            self.SPD  # speed
            self.INT  # intelligence
            self.REN  # renown
    """

    # define characters's strength
    @property
    def STR(self):
        try:
            if self._strength:
                pass
        except AttributeError:
            self._strength = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._strength

    @STR.setter
    def STR(self, value):
        self._strength.set(value)

    @STR.deleter
    def STR(self):
        pass
        self._strength.delete()
        del self._strength

    # define characters's constitution
    @property
    def CON(self):
        try:
            if self._constitution:
                pass
        except AttributeError:
            self._constitution = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._constitution

    @CON.setter
    def CON(self, value):
        self._constitution.set(value)

    @CON.deleter
    def CON(self):
        pass
        self._constitution.delete()
        del self._constitution

    # define characters's observation
    @property
    def OBS(self):
        try:
            if self._observation:
                pass
        except AttributeError:
            self._observation = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._observation

    @OBS.setter
    def OBS(self, value):
        self._observation.set(value)

    @OBS.deleter
    def OBS(self):
        pass
        self._observation.delete()
        del self._observation

    # define characters's agility
    @property
    def AGI(self):
        try:
            if self._agility:
                pass
        except AttributeError:
            self._agility = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._agility

    @AGI.setter
    def AGI(self, value):
        self._agility.set(value)

    @AGI.deleter
    def AGI(self):
        pass
        self._agility.delete()
        del self._agility

    # define characters's speed
    @property
    def SPD(self):
        try:
            if self._speed:
                pass
        except AttributeError:
            self._speed = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._speed

    @SPD.setter
    def SPD(self, value):
        self._speed.set(value)

    @SPD.deleter
    def SPD(self):
        pass
        self._speed.delete()
        del self._speed

    # define characters's intelligence
    @property
    def INT(self):
        try:
            if self._intelligence:
                pass
        except AttributeError:
            self._intelligence = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._intelligence

    @INT.setter
    def INT(self, value):
        self._intelligence.set(value)

    @INT.deleter
    def INT(self):
        pass
        self._intelligence.delete()
        del self._intelligence

    # define characters's wisdom
    @property
    def WIS(self):
        try:
            if self._wisdom:
                pass
        except AttributeError:
            self._wisdom = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._wisdom

    @WIS.setter
    def WIS(self, value):
        self._wisdom.set(value)

    @WIS.deleter
    def WIS(self):
        pass
        self._wisdom.delete()
        del self._wisdom

    # define characters's renown
    @property
    def REN(self):
        try:
            if self._renown:
                pass
        except AttributeError:
            self._renown = Element(self, 100, **ATTRIBUTE_SETTINGS)
        return self._renown

    @REN.setter
    def REN(self, value):
        self._renown.set(value)

    @REN.deleter
    def REN(self):
        pass
        self._renown.delete()
        del self._renown
