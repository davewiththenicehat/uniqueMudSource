import weakref
from evennia.utils.logger import log_info, log_warn
from evennia.utils import inherits_from

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
    ('breakpoint_func', None)
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
                    will run Element.breakpoint_func when passed
                        will ONLY run when it is passed
                        if element is 10 below the break point and is subtracted further the breakpoint_func will not run.
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
            'breakpoint_func': None,  # When passed breakpoint_func runs
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
    Do not access the Elements value attribute directly.
    Element operators supported:
        +,  -,  *,  /,  //,  %,  **, pow()
        +=, -=, *=, /=, //=, %=, **=
        ==, !=, <, <=, >, >=
    All bitwise support is not available as well as @
    There are custom methods to use
        Element.percent()  # returns the % the current value is from 0 to Element.max
        Element.breakpoint_percent()  # returns the % the current value is from Element.breakpoint to Element.max
            # both return a float rounded to the 2 point

    Notes:
    Default values will NOT record to the database.
    self.value is the local reference to Element's value. Changing this changes the Element's attribute as well as database field.
    self.db is a reference of the attributes or nattributes method for the object containing the Element.
    self.db_fields_list is a list of two tuples containing a key and default value for database fields.
        example: self.dbfields = [(key),(value)]
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

        try:
            if kwargs['name']:
                name = kwargs.get('name')
                if name:
                    if isinstance(name, str):
                        self.name = name
                        if self.log:
                            log_info(f"Element __init__, name passed and used {self.name}")
                    else:
                        raise ValueError("Element object, argument 3 or kwarg name must be a string variable or ommited at declaration.")
        except KeyError:  # No log kwarg passed
            pass

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
        Runs self.breakpoint_func if breakpoint was reached.
        Call only after value was verified by verify_num_arg
        Call only after the the math has been completed on the value but before it has been written to the database.
        """
        el_current_value = self.get()
        if el_current_value > self.breakpoint:
            if value <= self.breakpoint:
                if self.log:
                    log_info(f"Element {self.name} for db object {self.container.dbref}, method breakpoint_check encountered breakpoint.")
                if self.breakpoint_func:
                    self.breakpoint_func()
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
        # create local attributes
        for attr_key, attr_value in ELEMENT_LOCAL_ATTRIBUTES:
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

    def delete(self):
        "delete the instance of the Element, including values in database."
        # intentionally delete database entries
        for el_key, el_def_value in ELEMENT_DB_FIELDS:
            delattr(self, el_key)

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
        return self.sub(other, '__rsub__')

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
        "Element's __rtruediv__ descriptor"
        return self.truediv(other, '__rtruediv__')

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
        return self.floordiv(other, '__rfloordiv__')

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
        return self.mod(other, '__rmod__')

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
        return self.pow(other, '__rpow__')

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
        Including min, min_func, max, max_func, breakpoint, breakpoint_func
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
        If it is a database attribute and a value is saved to the database that database field will be removed.
        """
        if hasattr(self, name):
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
