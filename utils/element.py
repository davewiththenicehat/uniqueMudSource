import weakref
from evennia.utils.logger import log_info, log_warn
from evennia.utils import inherits_from
from evennia.typeclasses.attributes import Attribute


class ListElement:
    """
    A ListElement allows a developer to work with a list of database fields as
    if they are python attributes.
        For example:
            It will be used to represent:
                damage reduction on armor.
                damage bonus on a weapon.
                body parts on Characters
    Within a ListElement there are attributes for each key in the list.
        Each key is used as an attribute.
            For example:
                ListElement.ACD
        Each key is used to create a database resentation of the attribute.
            Example:
                character.dr.ACD = 3, would appear as 'dr_acd' in the database
        Do not use a ListElement's datbase entry.
        Usage is explained in the Usage section.

    Arguments:
        ListElement(container, el_list, log=True, name=None)
        container, is the container this Element will be stored on.
        el_list, is the list to turn into Elements
        log=True, if none error logging should be enabled.
        name=None, is the name of the ListElement.
            It is HIGHLY recommended that you do no use this.
            ListElement will get the name you gave the attribute
            in created.
                IE:
                self._dr.name == 'dr'
                self._dr = ListElement(self, DAMAGE_TYPES)
                The preceeding '_' will be automatically removed.

    Attributes, on each ListElement individually:
        name(str): name of the ListElement. (Normally what you named the container)
        value: the value of this Element.
        db_fields_dict(dict): Key is the db key for this Element, value is its
            default value.
        el_list(tuple): A tuple of element names in ListElement.

    Methods:
        items(return_obj=False): Returns an iterator of db_key, value or Attribute instance.
            Reference: evennia.typeclasses.attributes.Attribute
        get(key, default=None, return_obj=False): Returns the value of the key
            or it's instance.

        Note: while working with methods the key arguments are the short hand
            description of the Elements. For example 'occupied', not
            'right_hand_occupied'. To work on that level you can call
            object_instance.attributes.get('right_hand_occupied').

    Creation:
    You will need to make a propery on the class that will contain the
    ListElement.
    In the example below, self._dr = ListElement(self, DAMAGE_TYPES)
        self, is the container this ListElement will be stored in.
        DAMAGE_TYPES, is a tuple of damage. Could be a list also.
    Here is an example of a ListElement on a class named FakeCharacter:

    class FakeCharacter(Character):
        # define objects's Damage Reduction
        @property
        def dr(self):
            try:
                if self._dr:
                    pass
            except AttributeError:
                self._dr = ListElement(self, DAMAGE_TYPES)
                self._dr.verify()
            return self._dr

        @dr.setter
        def dr(self, value):
            self._dr.set(value)

        @dr.deleter
        def dr(self):
            self._dr.delete()

    Creation settings:
    Two key word arguments are supported.
        'name': None,  # name of the Element, highly recommend leaving default
        'log': False,  # if logging should be enabled
    When you create a ListElement it can accept a dictionary or a list of kwargs.
    Settings will set to their default if they are not passed on creation.
        No need to pass a full dictionary of arguments.
    Below is a list of those setting, in ditionary format with their default settings.
        arguments = {
            'name': None,  # name of the Element, highly recommend leaving default
            'log': False,  # if logging should be enabled
        }

    Usage:

        Do NOT access a ListElements database entry directory.
        ListElements are intended to be accessed in code as attributes only.

        This is really important.
        Really do not access a ListElement's database entry.

        Using the example property `dr` in the Creation: section.
            If char is an instance of FakeCharacter
            char.dr.ACD = 10  # sets objects acid damage reduction to 10
            setattr(char.dr, 'MNT', 1)  # set mental damage reduction to 1
            # set all dr on an Object to 1
            for type in LIST:
                db_key = 'dr_'+type.lower()
                setattr(char.dr, type, 1)
            # reduce damage dealt by characters bludgeoning damage reduction.
            damage = damage - char.dr.BLD

    Iteration:
        Basic iteration will return an iterator of Attribibute objects.
        Reference: evennia.typeclasses.attributes.Attribute.
        Instances that are the default value are not returned. For example
        if a Character's body part is not broken there will be no Attribute
        instance of broken for that body part. So there is not one to return.

        There are other methods that return iteratables.
        items, returns a db_key and value or Attribute instance.



    Notes:
    Default values 0 will NOT record to the database.
    Do NOT access a ListElements database entry directory.
    self.db_fields_dict is a dictionary of Element attributes and their default value
        example: self.db_fields_dict = {attr: (el_db_key, el_def_value)}
        default_value should be 0
    It is recommended store only, numbers, strings and booleans.
        Anything more complex may be difficult to work with in code.
    self.__str__ returns a representation of the ListElement
        IE: ACD: 3 | BLG: 0 | CLD: 0 | FIR: 0 | ELC: 0 | MNT: 0
    """

    def __init__(self, container, el_list, **kwargs):
        """
        Initialize a ListElement object.

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
                    log_info(f"ListElement __init__, name passed and used {self.name}")
            else:
                raise ValueError("ListElement object, kwarg name must be a string variable or ommited at declaration.")
        # collect an instance of the container object
        try:
            if container:
                self.container = weakref.proxy(container)
        except ValueError:
            raise ValueError("ListElement object, positional argument 1 reference of container class required.")
        try:
            self.container.attributes
        except ValueError:
            raise ValueError("ListElement Object, must inherit evennia.objects.models.ObjectDB")
        # create a reference of the database attribute
        self.db = weakref.proxy(container.attributes)
        # verify the list provided is useable
        if isinstance(el_list, list) or isinstance(el_list, tuple):
            self.el_list = el_list
        else:
            raise ValueError("ListElement Object, argument 2 must be a list or tuple.")

    def get(self, key, default=None, return_obj=False):
        """
        Returns the value of the key or it's instance.

        Attributes:
            key(str): The key for the element requested.
                Example: body.right_arm.get('bleeding')
            default=None: the value to return if none was found.
            return_obj(bool, optional): If set, the return is not the value of
                the Attribute but the Attribute object itself.

        Returns:
            value or instance of element or None if

        """
        self.verify()
        value = self.__getattribute__(key, default, return_obj=return_obj)
        return value

    def __get__(self, instance=None, owner=None):
        """__get__ descriptor, returns self"""
        return self

    def set(self, value=None):
        """ListElements should not be set"""
        self.verify()
        if self.log:
            log_info(f"ListElement {self.name} for db object {self.container.dbref}, self.__set__ called. value is {value}")
        raise ValueError(f"ListElement {self.name} for db object {self.container.dbref}, ListElement instance can not be set. Only ListElement attributes can be set.")

    def __str__(self):
        """
        return a string version of the Element.
        Example:
        ACD: 3 | BLG: 0 | CLD: 0 | FIR: 0 | ELC: 0 | MNT: 0 | PRC: 3 | POI: 0 | RAD: 0 | SLS: 0 |
        """
        self.verify()  # verify this object instance if it has not been already
        str_ver = ''
        for attr in self.el_list:
            attr_value = getattr(self, attr)
            str_ver = f"{str_ver}{attr}: {attr_value} | "
        return str(str_ver)

    def delete(self):
        """Delete all attributes' database entries, leaving the Element."""
        for attr in self.el_list:
            delattr(self, attr)

    def verify(self):
        """
        Verify a ListElement is useable.
        that the container has database access
        will name a name for the ListElement if none was provided at init
        Created a dictionary to easily reference attributes in ListElement
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
                    log_info(f"ListElement {self.name}, in container {self.container} verified")
        # if element instance was not found in container reference.
        try:
            if self.verified:
                pass
        except AttributeError:
            raise RuntimeError("ListElement object declaration received a container reference that does not contain the element instance created.")
        # Create a dictionary to easily reference attributes & database keys
        self.db_fields_dict = dict()
        el_def_value = 0  # default value for a ListElement attribute
        for attr in self.el_list:
            el_db_key = self.name+'_'+attr
            self.db_fields_dict.update({attr: (el_db_key, el_def_value)})

    def __setattr__(self, name, value):
        """
        ListElement's __setattr__ descriptor
        ListElement attributes do not actuall exist.
        They are forwarded to the database.
        Only set an attribute if it is not the default value of 1
        """
        try:  # if verified does not exist ignore it.
            if name in self.db_fields_dict:
                db_key, db_key_def_val = self.db_fields_dict.get(name)
                # if the db field exists record the change.
                # if the db field does not exist only record to the db if the value is not the default
                if self.db.has(db_key):
                    if self.log:
                        log_info(f"ListElement {self.name} for db object {self.container.dbref} __setattr__ attribute {name} and database key {db_key} getting set to non default value {value}")
                    # If setting to default value do not store in the database.
                    if value == db_key_def_val:
                        self.db.remove(db_key)
                    else:
                        self.db.add(db_key, value)
                else:
                    if value != db_key_def_val:  # do not record default values
                        if self.log:
                            log_info(f"ListElement {self.name} for db object {self.container.dbref} __setattr__ attribute {name} and database key {db_key} getting set to non default value {value}")
                        self.db.add(db_key, value)
                return
        except AttributeError:
                pass
        super().__setattr__(name, value)

    def __getattribute__(self, name, default=None, **kwargs):
        """
        Used to access any attribute in the ListElement.
        ListElement attributes do not actuall exist.
        If there is a database entry it is returend.
        If not in database default ListElement attribute of 0 is returned
        """
        # if the attribute is a database attribute retreive it from the database
        if name == 'el_list':
            return object.__getattribute__(self, name)
        if super(ListElement, self).__getattribute__('verified'):
            if name in self.el_list:
                db_key, db_key_def_val = self.db_fields_dict.get(name)
                if default is None:
                    default = db_key_def_val
                value = self.db.get(db_key, default=default, **kwargs)
                if self.log:
                    log_info(f"ListElement {self.name} for db object {self.container.dbref} __getattribute__ attribute {name} and database key {db_key} got value {value}")
                return value
        # Calling the super class to avoid recursion
        return object.__getattribute__(self, name)

    def __delattr__(self, name):
        """
        __delattr__ descriptor
        Called when a ListElement's attribute is deleted.
        Will remove a ListElement's entry in the database.
            There is no actual attribute to delete.
            The attribute will only be set to its default state.
        Attributes that are not part of the list passed on creation are deleted.
        """
        if name in self.el_list:
            el_db_key = self.name+'_'+name
            el_db_key, _ = self.db_fields_dict.get(name, el_db_key)
            # if the attribute exists in the database, remove it
            if self.db.has(el_db_key):
                self.db.remove(el_db_key)
        else:
            # delete the nondatabase attribute, calling the origional version of __delattr__ to avoid recursion
            object.__delattr__(self, name)

    def __iter__(self):
        """
        ListElement __iter__ descriptor
        Called when there is a request for iteration.

        Returns:
            An iteratable with instances of the ListElements' evennia Attributes.
            Reference: evennia.typeclasses.attributes.Attribute
            It is possible for these to be None.
        """
        ret = []
        for key in self.el_list:
            value = self.__getattribute__(key, return_obj=True)
            if value:
                ret.append(value)
        return iter(ret)

    def __contains__(self, item):
        """ListElement's __contains__ descriptor method"""
        if isinstance(item, str):
            return item in self.el_list
        elif isinstance(item, Attribute):
            for el in self:
                if item == el:
                    return True
        return False

    def __getitem__(self, key):
        """ListElement's __getitem__ descriptor."""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """ListElement's __setitem__ descriptor."""
        if key not in self.el_list:
            raise KeyError(f'{value} can not be set in {self.name}. Only {self.el_list} can be set.')
        else:
            setattr(self, key, value)

    def items(self, return_obj=False):
        """
        Returns an iterator of db_key, value or Attribute instance.
        Reference: evennia.typeclasses.attributes.Attribute

        Arguments:
            return_obj (bool, optional): If set, the return is not the value of
            the Attribute but the Attribute object itself.

        Returns:
            (el_desc=str, db_value=?): Element's description and the value of
                the database field.

            If return_obj is True:
            (el_desc=str, attr_inst=Attribute): Element's description and an
                instance of the attribute
                Reference: evennia.typeclasses.attributes.Attribute
        """
        ret = []
        for key in self.el_list:
            value = self.__getattribute__(key,  return_obj=return_obj)
            ret.append((key, value))
        return iter(ret)


# element attributes that will be saved to database
ELEMENT_DB_FIELDS = [
    ('value', 100),
    ('min', -100),
    ('breakpoint', 0),
    ('max', 100)
]
# element attributes that will not be saved to the database
ELEMENT_LOCAL_ATTRIBUTES = [
    ('dbtype', 'db'),
    ('min_func', None),
    ('max_func', None),
    ('descending_breakpoint_func', None),
    ('ascending_breakpoint_func', None)
]
ELEMENT_OPTIONS = ELEMENT_DB_FIELDS + ELEMENT_LOCAL_ATTRIBUTES
# Used to check if an attribute of the Element is a database element
ELEMENT_DB_KEYS = {
    'value': 100,
    'min': -100,
    'breakpoint': 0,
    'max': 100
}


class Element:
    """
    An Element allows a devloper to work with a complex fully managed object as if it were a standard python attribute.
        An Element will handle the float to int and int to float conversions
        An Element handles database interactions.
        An Element will handle many misc settings for the attribute.
            Examples:
                will not allow operators to set the Element below min
                    will run Element.min_func when min is reached
                will not allow operators to set the Element above max
                    will run Element.max_func when max is reached
                has a breakpoint attribute default is 0
                    will run Element.descending_breakpoint_func when the element's value falls below the breakpoint after being above it.
                        will ONLY run when it is passed
                        if element is 10 below the break point and is subtracted further the descending_breakpoint_func will not run.
                    will run Element.ascending_breakpoint_func when the element's value rises above the breakpoint after being below it.
                        Will only run when it is passed
                        Rising an element that is already above the breakpoint will not trigger this function
        Declaration of the Element requires creating a class attribute that is a proper which steps to do so is covered here.

    Creation:
    You will need to make a propery on the class you would like to contain the element.
    Here is an example of an element that will be named hp for a class named FakeCharacter:
        class FakeCharacter(Object):
            # define characters's HP
            @property
            def hp(self):
                try:
                    if self._hp:
                        pass
                except AttributeError:
                    #if using a kwarg dict Element(self, #, **argument_dict)
                    self._hp = Element(self)
                return self._hp

            @hp.setter
            def hp(self, value):
                self._hp.set(value)

            @hp.deleter
            def hp(self):
                self._hp.delete()
                del self._hp
    Above the property self.hp can be access as if it were an integer or float.
    Usage is explained in the Usage: section

    Creation settings:
    When you create an Element it accepts a dictionary or a list of kwargs.
    Settings will set to their default if they are not passed on creation. No need to pass a full dictionary of arguments.
    Below is a list of those setting, in ditionary format with their default settings.
        arguments = {
            'name': None,  # name of the Element, highly recommend leaving default
            'min': -100,  # the min number the Element can be, if reached min_func runs
            'min_func': None,  # reference to a function to run when the self.value attribute reaches self.min
            'breakpoint': 0,  # number a breakpoint point occurs like falling unconshious or an object breakpoint
            'descending_breakpoint_func': None,  # When Element's value falls below the breakpoint after being above it, this function is called.
            'ascending_breakpoint_func': None,  # When Element's value rises above breakpoint after being below it, this function is called
            'max': 100,  # the max number the Element can be. When reached self.max_fun() runs
            'max_func': None  # reference to a function to run when the self.value attribute reachs the self.max
            'dbtype': 'db',  # the database type to use can be 'db' or 'ndb'
        }

    Usage:
        Using the example property `hp` in the Creation: section.
        If char is an instance of FakeCharacter
        char.hp = 10  # sets objects hp to 10
        char.hp = 5 + 5  # sets objects hp to 10
        char.hp += 5  # object's hp is now 5 higher.
        char.hp -= dmg  # will subtract dmg from char's hp total
        hp = getattr(char, 'hp')  # returns a reference of the Element
        hpref = getattr(char, 'hp').get  # returns a value of the instance
            Use hpref.get() over the example above.
            It is easier to read and understand.
        hpref = char.hp  # returns a reference of the Element
        hp = char.hp.get()  # returns a int or float value of the instance

        IMPORTANT:
        char.hp += 10000  # object's hp is now 100. Because Elements' default max is 100.
            ^ If the element was passed a reference of a function with kwarg max_func it will be called now

        IMPORTANT:
        Using a reference requires you use .set for any equals operations
        Example:
            for stat in (char.END, char.CHR):
                stat.set(22)
                # stat = 22 # Will turn your reference into an int

    Element operators supported:
        +,  -,  *,  /,  //,  %,  **, pow()
        +=, -=, *=, /=, //=, %=, **=
        ==, !=, <, <=, >, >=
    All bitwise support is not available as well as @

    Methods:
        percent()  # returns the % the current value is from 0 to Element.max
        breakpoint_percent()  # returns the % the current value is from Element.breakpoint to Element.max
            # both return a float rounded to the 2 point
        clear()  # set all Element attributes to default.

    Notes:
    Default values will NOT record to the database.
    self.value is the local reference to Element's value. Changing this changes the Element's attribute as well as database field.
    self.db is a reference of the attributes or nattributes method for the object containing the Element.
    self.db_fields_list is a list of two tuples containing a key and default value for database fields.
        example: self. = [(key),(value)]
    self.db_fields_dict, contains a dictionary of the elements database fields.
        Using the setting kwarg from creation as the key
        value is a tuple with the db field, and default value
        example: self.db_fields_dict.update({el_key: (self.name+'_'+el_key, el_def_value)})
    self.settings is a dictionary containing settings in kwarg format. Will contain default settings where developer did not override also.
    self.__str__ returns a rounded version of Element. The actual element is a float that can be longer than the str represents
    """

    def __init__(self, container, value=100, **kwargs):
        """
        Initialize an Element object.

        Records a weak reference of the container object
        Records desired settings with kwargs
        """
        self.verified = False  # Used to avoid multiple verification tests
        # check if logging kwarg was passed
        try:
            if kwargs['log']:
                self.log = True
            else:
                self.log = False
            if kwargs['name']:
                name = kwargs.get('name')
                if name:
                    if isinstance(name, str):
                        self.name = name
                        if self.log:
                            log_info(f"Element __init__, name passed and used {self.name}")
                    else:
                        raise ValueError("Element object, kwarg name must be a string variable or ommited at declaration.")
        except KeyError:  # No log kwarg passed
            self.log = False

        # collect an instance of the container object
        try:
            if container:
                self.container = weakref.proxy(container)
        except ValueError:
            raise ValueError("Element object, positional argument 1 reference of container class required.")
        # verify container is a db object
        if not inherits_from(container, "evennia.objects.models.ObjectDB"):
            raise ValueError("Element Object, must inherit evennia.objects.models.ObjectDB")
        # Check that the value setting passed is valid.
        if not (isinstance(value, int) or isinstance(value, float)):
            raise ValueError("Element object, argument 3 or kwarg value=number must be an int or float variable")
        # configure settings
        self.settings = dict()
        for for_key, for_value in ELEMENT_OPTIONS:
            if for_key == 'dbtype':  # get reference of containers database method
                if for_key == 'ndb':
                    self.db = weakref.proxy(container.nattributes)
                else:
                    self.db = weakref.proxy(container.attributes)
                continue
            if for_key == 'name' or for_key == 'container':  # do not auto set these kwargs
                continue
            kwarg_value = kwargs.get(for_key, for_value)  # use default if no kwarg was passed
            self.settings.update({for_key: kwarg_value})

    def get(self, instance=None, owner=None):
        "If database has a value return it, if not return the default value"
        self.verify()  # verify this object instance if it has not been already
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, selfget called")
        # Element.__getattribute__ handles returning the database value
        return self.value

    def __get__(self, instance=None, owner=None):
        "descriptor wrapper for Element's self.get"
        return self.get()

    def set(self, value=None):
        "Records Elements change to the database. Verifies the value first."
        self.verify()  # verify this object instance if it has not been already
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, self.__set__ called. value is {value}")
        # record the value change
        value = self.verify_num_arg(value, 'set')  # returns false if value argument can not convert to int
        value = self._state_check(value)
        if self.log:
            log_info(f"Element value after checks {value}")
        self.value = value

    def __set__(self, instance, value):
        "descriptor wrapper for Element's self.set"
        self.set(value)

    def _state_check(self, value):
        """
        Internal method, do not use.
        Checks if Elements min, max or breakpoint has been reached.
        Call only after verify_num_arg has been
        Call only after the the math has been completed on the value but before it has been written to the database.
        """
        value = self._min_check(value)
        value = self._max_check(value)
        value = self._breakpoint_check(value)
        return value

    def _min_check(self, value):
        """
        Internal method, do not use.
        Checks is Element's min number has been reached.
        Runs self.min_func if min was reached.
        Call only after value was verified by verify_num_arg
        Call only after the the math has been completed on the value but before it has been written to the database.
        """
        if value <= self.min:
            if self.log:
                log_info(f"Element {self.name} for db object {self.container.dbref}, method min_check encountered min.")
            value = self.min
            if self.min_func:
                self.min_func()
            return value
        return value

    def _max_check(self, value):
        """
        Internal method, do not use.
        Checks is Element's max number has been reached.
        Runs self.max_func if max was reached.
        Call only after value was verified by verify_num_arg
        Call only after the the math has been completed on the value but before it has been written to the database.
        """
        if value >= self.max:
            if self.log:
                log_info(f"Element {self.name} for db object {self.container.dbref}, method max_check encountered max.")
            value = self.max
            if self.max_func:
                self.max_func()
            return value
        return value

    def _breakpoint_check(self, value):
        """
        Internal method, do not use.
        Checks is Element's breakpoint number has been reached.
        Runs self.descending_breakpoint_func if breakpoint was reached.
        Call only after value was verified by verify_num_arg
        Call only after the the math has been completed on the value but before it has been written to the database.
        """
        el_current_value = self.get()
        if el_current_value > self.breakpoint:
            if value <= self.breakpoint:
                if self.log:
                    log_info(f"Element {self.name} for db object {self.container.dbref}, method breakpoint_check encountered descending breakpoint.")
                if self.descending_breakpoint_func:
                    self.descending_breakpoint_func()
                return value
        elif el_current_value <= self.breakpoint:
            if value > self.breakpoint:
                if self.log:
                    log_info(f"Element {self.name} for db object {self.container.dbref}, method breakpoint_check encountered ascending breakpoint.")
                if self.ascending_breakpoint_func:
                    self.ascending_breakpoint_func()
                return value
        return value

    def verify_num_arg(self, value=None, caller='unknown'):
        """
        Verifies that an object passed to it is a number. float or int
        returns False if the value argument can not convert to a number.
            Logs a warning level log event if it can not.
        arg 1 is value to test
        arg 2 is the name of the method calling
        both are optional. Leaving arg 1 empty will result in a test failure.
        """
        try:
            # if value is not an int or float try to convert it
            if isinstance(value, int) or isinstance(value, float):
                value = float(value)
                return value
        except TypeError:
            if self.log:
                log_info("Element verify_num_arg, TypeError")
            log_warn(f"Element {self.name} for db object {self.container.dbref} caller {caller}, method verify_num_arg received no argument.")
            return False
        except ValueError:
            if self.log:
                log_info("Element verify_num_arg, ValueError")
            log_warn(f"Element {self.name} for db object {self.container.dbref} caller {caller}, method verify_num_arg argument cannot convert to int or float.")
            return False
        return value  # value is good, simly return it

    def verify(self):
        """
        Verifies the instance of this Element is useable.
        Verify the container reference passed at Element's init contains a reference to this Element instance.
        Find the name of this instance if none was provided.
        Creates a dictionary and list of database attributes to use as reference
        Creates local attributes.
        Pulls saved attribute values from database if any. These are used over default and creation settings.
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
                    log_info(f"Element {self.name}, in container {self.container} verified")
        # if element instance was not found in container reference.
        try:
            if self.verified:
                pass
        except AttributeError:
            raise RuntimeError("Element object declaration received a container reference that does not contain the element instance created.")
        # create a lists to easily manage db attributes
        self.db_fields_list = list()
        self.db_fields_dict = dict()
        for el_key, el_def_value in ELEMENT_DB_FIELDS:
            value = self.settings.get(el_key)  # get setting provided on Element creation
            el_db_key = self.name+'_'+el_key
            self.db_fields_list += [(el_key, (el_db_key, value))]
            self.db_fields_dict.update({el_key: (el_db_key, value)})
            # Create unique database entries if there are any
            # Where the database value overrides the Element's default values
            if self.db.has(el_db_key):
                value = self.db.get(el_db_key)
            if value != el_def_value:  # do not a global default Element value
                setattr(self, el_key, value)
        # create local attributes, if they were not set at init
        for attr_key, attr_value in ELEMENT_LOCAL_ATTRIBUTES:
            if not hasattr(self, attr_key):
                setattr(self, attr_key, attr_value)

    def percent(self):
        "returns the percent the element is from 0 to its max number."
        self.verify()  # verify this object instance if it has not been already
        value = self.get()
        return 100 * value / self.max

    def percentage(self):
        "returns the percent the element is from 0 to its max number."
        return self.percent()

    def breakpoint_percent(self):
        "returns the percent the element is from its breakpoint to its max number."
        self.verify()  # verify this object instance if it has not been already
        value = self.get()
        value = ((value - self.breakpoint) * 100) / (self.max - self.breakpoint)
        return round(value, 2)

    def clear(self):
        "delete the instance of the Element, including values in database."
        # intentionally delete database entries
        for el_key, el_def_value in ELEMENT_DB_FIELDS:
            delattr(self, el_key)

    def delete(self):
        "delete the instance of the Element, including values in database."
        self.clear()

    def breakpoint_percentage(self):
        "returns the percent the element is from its breakpoint to its max number."
        return self.breakpoint_percent()

# Start non-property descriptors section

    def __str__(self):
        "return a string version of the Element"
        self.verify()  # verify this object instance if it has not been already
        value = self.get()
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, float):
            if (value).is_integer():
                value = int(value)
            else:
                value = round(value, 2)
            return str(value)
        else:
            log_warn(f"Element {self.name} for db object {self.container.dbref}, self.__str__ received a non numerical type")
            return str(value)

    def __delete__(self, instance):
        """Element's __delete__ descriptor"""
        self.clear()

    #def __del__(self):
    #    """
    #        Elements __del__ descriptor
    #       Called after instance is deleted
    #    """
    #    super().__del__()

    def add(self, other, descriptor='add'):
        "Elements addition method"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, {descriptor} called other is {other} value is {value}.")
        value += other
        return value

    def __add__(self, other):
        "Element's __add__ descriptor"
        return self.add(other, '__add__')

    def __radd__(self, other):
        "Element's __radd__ descriptor"
        return self.add(other, '__radd__')

    def __iadd__(self, other):
        "Element's __iadd__ descriptor"
        return self.add(other, '__iadd__')

    def sub(self, other, descriptor='sub'):
        "Elements substraction method"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, {descriptor} called other is {other} value is {value}.")
        value -= other
        return value

    def __sub__(self, other):
        "Element's __sub__ descriptor"
        return self.sub(other, '__sub__')

    def __rsub__(self, other):
        "Element's __rsub__ descriptor"
        #return self.sub(other, '__rsub__')
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __rsub__ called other is {other} value is {value}.")
        value = other - value
        return value

    def __isub__(self, other):
        "Element's __isub__ descriptor"
        return self.sub(other, '__isub__')

    def mul(self, other, descriptor='mul'):
        "Elements multiplication method"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, {descriptor} called other is {other} value is {value}.")
        value *= other
        return value

    def __mul__(self, other):
        "Element's __mul__ descriptor"
        return self.mul(other, '__mul__')

    def __rmul__(self, other):
        "Element's __rmul__ descriptor"
        return self.mul(other, '__rmul__')

    def __imul__(self, other):
        "Element's __imul__ descriptor"
        return self.mul(other, '__imul__')

    def truediv(self, other, descriptor='truediv'):
        "Elements true division method"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, {descriptor} called other is {other} value is {value}.")
        value /= other
        return value

    def __truediv__(self, other):
        "Element's __truediv__ descriptor"
        return self.truediv(other, '__truediv__')

    def __rtruediv__(self, other):
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __rtruediv__ called other is {other} value is {value}.")
        value = other / value
        return value

    def __itruediv__(self, other):
        "Element's __itruediv__ descriptor"
        return self.truediv(other, '__itruediv__')

    def floordiv(self, other, descriptor='floordiv'):
        "Elements floor division method"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, {descriptor} called other is {other} value is {value}.")
        value //= other
        return value

    def __floordiv__(self, other):
        "Element's __floordiv__ descriptor"
        return self.floordiv(other, '__floordiv__')

    def __rfloordiv__(self, other):
        "Element's __rfloordiv__ descriptor"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __rfloordiv__ called other is {other} value is {value}.")
        value = other // value
        return value

    def __ifloordiv__(self, other):
        "Element's __ifloordiv__ descriptor"
        return self.floordiv(other, '__ifloordiv__')

    def mod(self, other, descriptor='mod'):
        "Elements mod division method"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, {descriptor} called other is {other} value is {value}.")
        value %= other
        return value

    def __mod__(self, other):
        "Element's __mod__ descriptor"
        return self.mod(other, '__mod__')

    def __rmod__(self, other):
        "Element's __rmod__ descriptor"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __rmod called other is {other} value is {value}.")
        value = other % value
        return value

    def __imod__(self, other):
        "Element's __imod__ descriptor"
        return self.mod(other, '__imod__')

    def pow(self, other, descriptor='pow'):
        "Elements power or pow method"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, {descriptor} called other is {other} value is {value}.")
        value **= other
        return value

    def __pow__(self, other):
        "Element's __pow__ descriptor"
        return self.pow(other, '__pow__')

    def __rpow__(self, other):
        "Element's __rpow__ descriptor"
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __rpow__ called other is {other} value is {value}.")
        value = other ** value
        return value

    def __ipow__(self, other):
        "Element's __ipow__ descriptor"
        return self.pow(other, '__ipow__')

    def __lt__(self, other):
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __lt__ called other is {other} value is {value}.")
        return value < other

    def __le__(self, other):
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __le__ called other is {other} value is {value}.")
        return value <= other

    def __gt__(self, other):
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __gt__ called other is {other} value is {value}.")
        return value > other

    def __ge__(self, other):
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if self.log:
            log_info(f"Element {self.name} for db object {self.container.dbref}, __ge__ called other is {other} value is {value}.")
        return value >= other

    def __eq__(self, other):
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if other:  # if other is a number
            if self.log:
                log_info(f"Element {self.name} for db object {self.container.dbref}, __eq__ called other is {other} value is {value}.")
            return value == other
        else:  # if other is not a number
            # avoid recursive checks
            return self.__repr__ == other.__repr__

    def __ne__(self, other):
        self.verify()  # verify this object instance if it has not been already
        other = self.verify_num_arg(other)
        value = self.get()
        if other:  # if other is a number
            if self.log:
                log_info(f"Element {self.name} for db object {self.container.dbref}, __ne__ called other is {other} value is {value}.")
            return value != other
        else:  # if other is not a number
            # avoid recursive checks
            return self.__repr__ != other.__repr__

# Attribute descriptors

    def __setattr__(self, name, value):
        """
        Element's __setattr__ descriptor
        If an Element's attribute should be saved to the database it will be saved there if it is not a defaul setting
        """
        name = name.lower()
        super().__setattr__(name, value)
        try:  # if verified does not exist ignore it.
            if self.verified:  # only do if Element is verified to avoid errors
                if name in self.db_fields_dict:
                    db_key, db_key_def_val = self.db_fields_dict.get(name)
                    # if the db field exists record the change.
                    # if the db field does not exist only record to the db if the value is not the default
                    if self.db.has(db_key):
                        if self.log:
                            log_info(f"Element {self.name} for db object {self.container.dbref} __setattr__ attribute {name} and database key {db_key} getting set to non default value {value}")
                        self.db.add(db_key, value)
                    else:
                        if value != db_key_def_val:  # do not record default values
                            if self.log:
                                log_info(f"Element {self.name} for db object {self.container.dbref} __setattr__ attribute {name} and database key {db_key} getting set to non default value {value}")
                            self.db.add(db_key, value)
        except AttributeError:
            pass

    def __getattribute__(self, name):
        """
        Used to access any attribute in the Element.
        Including min, min_func, max, max_func, breakpoint, descending_breakpoint_func and ascending_breakpoint_func
        """
        # if the attribute is a database attribute retreive it from the database
        if super(Element, self).__getattribute__('verified'):
            if name in ELEMENT_DB_KEYS:
                db_key, db_key_def_val = self.db_fields_dict.get(name)
                value = self.db.get(db_key, default=db_key_def_val)
                if self.log:
                    log_info(f"Element {self.name} for db object {self.container.dbref} __getattribute__ attribute {name} and database key {db_key} got value {value}")
                return value
        # Calling the super class to avoid recursion
        return object.__getattribute__(self, name)

    def __delattr__(self, name):
        """
        __delattr__ descriptor
        Called when an Element's attribute is deleted.
        If the attribute is a database attribute;
            its entry will be remmoved from the database,
            the attribute is managed
                it can not be deleted
                it is now its default value
        If it is not a database attribute it will be deleted
        """
        # if this is a database attribute there is no reference in the Element instance
        # only in the database if it exists there.
        # if it does not exist in the database Element.get returns the global default.
        # This results in the Element always seeing database attributes as existing when they never actually do
        if name in ELEMENT_DB_KEYS:
            el_db_key = self.name+'_' + name
            el_db_key, _ = self.db_fields_dict.get(name, el_db_key)
            # if the attribute exists in the database, remove it
            if self.db.has(el_db_key):
                self.db.remove(el_db_key)
        else:
            # delete the nondatabase attribute, calling the origional version of __delattr__ to avoid recursion
            object.__delattr__(self, name)
