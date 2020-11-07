"""
contains functions and variables that interact with game damage.

Attributes:
    MAP_DICT = dict, a mapping of damage types and full names
        aliase: MAP
        in format: 'ACD': 'acid'
    TYPES = tuple, damage types to iterate through

Modules:
    roll, Get a damage roll adjusted by a character's damage stat modifier.
"""

from random import randint
import weakref
from evennia.utils.logger import log_info, log_warn
from evennia.utils import inherits_from

# a mapping of damage types and full names
MAP_DICT = {
    'ACD': 'acid',
    'BLG': 'bludgeoning',
    'CLD': 'cold',
    'FIR': 'fire',
    'ELC': 'electric',
    'MNT': 'mental',
    'PRC': 'piercing',
    'POI': 'poison',
    'RAD': 'radiation',
    'SLS': 'slashing'
}
MAP = MAP_DICT

# damage types to iterate through
TYPES = (
    'ACD',
    'BLG',
    'CLD',
    'FIR',
    'ELC',
    'MNT',
    'PRC',
    'POI',
    'RAD',
    'SLS'
)

def roll(command, use_mod=True, log=False):
    """
    Get a damage roll adjusted by a character's damage stat modifier.

    Arguments:
        command, the command that is manipulating damage
        use_mod=True,
        log=False, if True log the variables used

    Returns:
        random int between 1 and damage max plus character's stat damage modifier

    Equation:
        Each action can have it's own max damage.
            Default max damage is 4.
        Each action can have it's own stat used to modify damage
            Default stat used to modify damage is strength
        Damage manipulated is from 1 to max damage plus the stat's damage modifier.
    """
    dmg_max = 4
    dmg_mod_stat = 'STR'
    dmg_mod = 0
    caller = command.caller
    if hasattr(command, 'dmg_max'):  # if the command has a damage maximum use it instead
        dmg_max = getattr(command, 'dmg_max')
    # only get stat modifier if use_mod is True
    if use_mod:
        if hasattr(command, 'dmg_mod_stat'):  # if the command has a custom damage modifier stat use it instead
            dmg_mod_stat = getattr(command, 'dmg_mod_stat')
        dmg_mod_name = dmg_mod_stat+'_dmg_mod'
        if hasattr(caller, dmg_mod_name):  # if the caller of the command has the stat damage modifier use it.
            dmg_mod = getattr(caller, dmg_mod_name)
    return randint(1, dmg_max) + dmg_mod


class DamageElement:
    """
    A DamageElement is used to easily reference damage types in UM.
        For example:
            It will be used to represent damage reduction on armor.
            It will be used to represent damage bonus on a weapon.
    Within a Damage Element there are attributes for each damage type.
    Damage types exist in a damage global dictionary damage.MAP_DICT
        That has an alias of damage.MAP
        It is formated as:
            MAP_DICT = {
                'ACD': 'acid',
                'BLG': 'bludgeoning',
                'CLD': 'cold',
                'FIR': 'fire',
                'ELC': 'electric',
                'MNT': 'mental',
                'PRC': 'piercing',
                'POI': 'poison',
                'RAD': 'radiation',
                'SLS': 'slashing'
            }
        Each key is used as an attribute.
            For example:
                DamageElement.ACD
        Each key is used to create a database prepresentation of the attribute.
            Example:
                character.dr.ACD = 3, would appear as 'dr_acd' in the database
        Do not use a DamageElement's datbase entry.
        Usage is explained in the Usage section.

    Creation:
    You will need to make a propery on the class that will contain the DamageElement
    Here is an example of a DamageElement on a class named FakeCharacter:
        class FakeCharacter(Object):
            # define characters's damage reduction
            @property
            def dr(self):
                try:
                    if self._dr:
                        pass
                except AttributeError:
                    self._dr = DamageElement(self)
                    self._dr.verify()
                return self._dr

            @dr.setter
            def dr(self, value):
                self._dr.set(value)

            @dr.deleter
            def dr(self):
                self._dr.delete()
    Usage is explained in the Usage: section

    Creation settings:
    Two key word arguments are supported.
        'name': None,  # name of the Element, highly recommend leaving default
        'log': False,  # if logging should be enabled
    When you create an Element it can accept a dictionary or a list of kwargs.
    Settings will set to their default if they are not passed on creation.
        No need to pass a full dictionary of arguments.
    Below is a list of those setting, in ditionary format with their default settings.
        arguments = {
            'name': None,  # name of the Element, highly recommend leaving default
            'log': False,  # if logging should be enabled
        }

    Usage:

        Do NOT access a DamageElements database entry directory.
        DamageElements are intended to be accessed in code as attributes only.

        This is really important.
        Really do not access a DamageElement's database entry.

        Using the example property `dr` in the Creation: section.
            If char is an instance of FakeCharacter
            char.dr.ACD = 10  # sets objects acid damage reduction to 10
            setattr(char.dr, 'MNT', 1)  # set mental damage reduction to 1
            # set all dr on an Object to 1
            for type in TYPES:
                db_key = 'dr_'+type.lower()
                setattr(char.dr, type, 1)
            # reduce damage dealt by characters bludgeoning damage reduction.
            damage = damage - char.dr.BLD


    Notes:
    Default values will NOT record to the database.
    Do NOT access a DamageElements database entry directory.
    self.db_fields_dict is a dictionary of damage types and their default value
        example: self.dbfields = [(key),(default_value)]
        default_value should be 0
    self.__str__ returns a representation of the DamageElement
        IE: ACD: 3 | BLG: 0 | CLD: 0 | FIR: 0 | ELC: 0 | MNT: 0 | PRC: 3 | POI: 0 | RAD: 0 | SLS: 0 |
    """

    def __init__(self, container, **kwargs):
        """
        Initialize a DamageElement object.

        Records a weak reference of the container object
        Pulls settings from kwargs
        """
        self.verified = False  # Used to avoid multiple verification tests
        self.log = False  # Used for logging message
        # check if logging kwarg was passed
        if 'log' in kwargs:
            self.log = kwargs.get('log')
        elif 'name' in kwargs:
            name = kwargs.get('name')
            if isinstance(name, str):
                self.name = name
                if self.log:
                    log_info(f"DamageElement __init__, name passed and used {self.name}")
            else:
                raise ValueError("DamageElement object, kwarg name must be a string variable or ommited at declaration.")
        # collect an instance of the container object
        try:
            if container:
                self.container = weakref.proxy(container)
        except ValueError:
            raise ValueError("DamageElement object, positional argument 1 reference of container class required.")
        # verify container is a db object
        if not inherits_from(container, "evennia.objects.models.ObjectDB"):
            raise ValueError("DamageElement Object, must inherit evennia.objects.models.ObjectDB")
        # create a reference of the database attribute
        self.db = weakref.proxy(container.attributes)

    def get(self, instance=None, owner=None):
        """Returns a reference of the DamageElement"""
        self.verify()
        if self.log:
            log_info(f"DamageElement {self.name} for db object {self.container.dbref}, selfget called")
        return self

    def __get__(self, instance=None, owner=None):
        """descriptor wrapper for DamageElement's self.get"""
        return self.get()

    def set(self, value=None):
        """DamageElements should not be set"""
        self.verify()
        if self.log:
            log_info(f"DamageElement {self.name} for db object {self.container.dbref}, self.__set__ called. value is {value}")
        raise ValueError(f"DamageElement {self.name} for db object {self.container.dbref}, DamageElement instance can not be set. Only DamageElement attributes can be set.")

    def __str__(self):
        """
        return a string version of the Element.
        Example:
        ACD: 3 | BLG: 0 | CLD: 0 | FIR: 0 | ELC: 0 | MNT: 0 | PRC: 3 | POI: 0 | RAD: 0 | SLS: 0 |
        """
        self.verify()  # verify this object instance if it has not been already
        str_ver = ''
        for type in TYPES:
            type_value = getattr(self, type)
            str_ver = f"{str_ver}{type}: {type_value} | "
        return str(str_ver)

    def delete(self):
        """Delete all attributes' database entries, leaving the Element."""
        for type in TYPES:
            delattr(self, type)

    def verify(self):
        """
        Verify a DamageElement is useable.
        that the container has database access
        will name a name for the DamageElement if none was provided at init
        Created a dictionary to easily reference attributes in DamageElement
        """
        # this object has been verified, skip the test
        if self.verified:
            return
        # find reference of this Element in container and get the name of this Element
        for for_key, for_value in self.container.__dict__.items():
            if for_value.__repr__ == self.__repr__:
                # if the name has not yet been set, set it now
                try:
                    if self.name:
                        pass
                except AttributeError:
                    # record the elements name remove prefix _ if it exists
                    if for_key[0] == '_':
                        self.name = for_key[1:]
                    else:
                        self.name = for_key
                self.verified = True  # record that this Element instance is good
                if self.log:
                    log_info(f"DamageElement {self.name}, in container {self.container} verified")
        # if element instance was not found in container reference.
        try:
            if self.verified:
                pass
        except AttributeError:
            raise RuntimeError("DamageElement object declaration received a container reference that does not contain the element instance created.")
        # Create a dictionary to easily reference attributes & database keys
        self.db_fields_dict = dict()
        el_def_value = 0  # default value for a DamageElement attribute
        for type in TYPES:
            el_db_key = self.name+'_'+type
            self.db_fields_dict.update({type: (el_db_key, el_def_value)})

    def __setattr__(self, name, value):
        """
        DamageElement's __setattr__ descriptor
        DamageElement attributes do not actuall exist.
        They are forwarded to the database.
        Only set an attribute if it is not the default value of 1
        """
        super().__setattr__(name, value)
        try:  # if verified does not exist ignore it.
            if name in self.db_fields_dict:
                db_key, db_key_def_val = self.db_fields_dict.get(name)
                # if the db field exists record the change.
                # if the db field does not exist only record to the db if the value is not the default
                if self.db.has(db_key):
                    if self.log:
                        log_info(f"DamageElement {self.name} for db object {self.container.dbref} __setattr__ attribute {name} and database key {db_key} getting set to non default value {value}")
                    # If setting to default value do not store in the database.
                    if value == db_key_def_val:
                        self.db.remove(db_key)
                    else:
                        self.db.add(db_key, value)
                else:
                    if value != db_key_def_val:  # do not record default values
                        if self.log:
                            log_info(f"DamageElement {self.name} for db object {self.container.dbref} __setattr__ attribute {name} and database key {db_key} getting set to non default value {value}")
                        self.db.add(db_key, value)
        except AttributeError:
                pass

    def __getattribute__(self, name):
        """
        Used to access any attribute in the DamageElement.
        DamageElement attributes do not actuall exist.
        If there is a database entry it is returend.
        If not in database default damageElement attribute of 0 is returned
        """
        # if the attribute is a database attribute retreive it from the database
        if super(DamageElement, self).__getattribute__('verified'):
            if name in TYPES:
                db_key, db_key_def_val = self.db_fields_dict.get(name)
                value = self.db.get(db_key, default=db_key_def_val)
                if self.log:
                    log_info(f"DamageElement {self.name} for db object {self.container.dbref} __getattribute__ attribute {name} and database key {db_key} got value {value}")
                return value
        # Calling the super class to avoid recursion
        return object.__getattribute__(self, name)

    def __delattr__(self, name):
        """
        __delattr__ descriptor
        Called when a DamageElement's attribute is deleted.
        Will remove a DamageElement's entry in the database.
            There is no actual attribute to delete
        """
        if name in TYPES:
            el_db_key = self.name+'_'+name
            el_db_key, _ = self.db_fields_dict.get(name, el_db_key)
            # if the attribute exists in the database, remove it
            if self.db.has(el_db_key):
                self.db.remove(el_db_key)
        else:
            # delete the nondatabase attribute, calling the origional version of __delattr__ to avoid recursion
            object.__delattr__(self, name)
