from evennia.utils.utils import make_iter

from world.rules.damage import TYPES as DAMAGE_TYPES
from utils.element import Element, ListElement
from utils.emote import um_emote
from world.rules.body import PART_STATUS
from world.rules import body


class CharExAndObjMixin:
    """
    Creates basic attributes that exist on all typeclasses.objects.Objects and
    typeclasses.characters.Character objects.
    This is a mixin class. Should be a secondary inherit.
        class Object(CharExAndObjMixin, ContribRPObject):

    Attributes:
        hp = Element, the objects hit points or health
        dr=ListElement, a series of damage types. Used to represent a
            characters flat damage reduction. This is used in addition to
            dr received from worn equiptment.
        dr.types, a list (tuple) of damage types this object supports.
        body=object, body is a blank object. It contains ListElement objects
            that represent the individual body parts.
            Body parts are accessable as attributes.
            IE: py self.msg(body.head), will display the status of your
            Character's head. "broke: 0 | bleeding: 0 | missing: 0 |"
            These status can be manipulated directly.
            self.body.left_arm.bleeding = True
                Will start the bleeding status on the arm.
                This will be recorded to the database also.
                As "head_bleeding = True" or self.db.head_bleeding
                Do not manipulate Elements' database entries. Work with them
                via the Element.
        BODY_PARTS, a list of body parts to reprenst a body on this object.
            For example humans would be ('head', 'shoulders') so on.
            Note, this could be used for obects ('left_turret', 'right_turret')
        body.parts, is a tuple of parts that make up the instances body
            This will be an exact duplicate of BODY_PARTS.
            This is intended to make it very easy to iterate through a body.
        body.part_name, where part_name is a part from the objects body.parts list
           Using body.head as a reference of a possible body part.
           body.head.dr, an object containing dr values in a simular format to Object.dr
               THESE ARE CACHED VARIABLES. part dr ratings are provided by armor.
               Changing this will result in a temp change until the character wears anything,
               the server restarts, or the Character is initialized for any reason.
           body.head.dr.el_list, a list of dr values this body part is covered with.
           body.head.dr.DAMAGE_TYPE (int), dr value of a type from the DAMAGE_TYPES list
               for example body.head.dr.PRC for peirce
           body.head.PART_STATUS (boolean), a status from the PART_STATUS list.
               for example body.head.bleeding, for bleeding

    Methods:
        get_body_part(part_name), Return a randon or specified instance of a part on the object's body.
        cache_body_dr(), caches dr for all this Object's body parts
        ascending_breakpoint(), is automatically called when an object's hp rises above it's
            breakpoint (likely 0), when it was previous below it's breakpoint.
            Is intended to be overridden
        descending_breakpoint(), is automatically called when an object's hp falls below it's
            breakpoint (likely 0), when it was previous above it's breakpoint.
            Is intended to be overridden
        destroy, This is automatically called when an object's hp reaches self.hp.min
            Intended to be overriden with a typeclass

    """

    # define objects's HP
    @property
    def hp(self):
        try:
            if self._hp:
                pass
        except AttributeError:
            self._hp = Element(self)
            self._hp.verify()
            setattr(self._hp, 'modifier_stat', 'CON')
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp.set(value)

    @hp.deleter
    def hp(self):
        self._hp.delete()
        del self._hp

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

    # define untyped Object bodies
    BODY_PARTS = ()

    @property
    def body(self):
        try:
            if self._body:
                pass
        except AttributeError:
            # create an empty object
            self._body = type('_body', (object,), {})()
            self._body  # initialize the empty object
            self._body.parts = self.BODY_PARTS  # make copy of the parts list
            # ListElements will want to know what its db method is
            self._body.attributes = self.attributes
            for body_part in self.BODY_PARTS:
                # create attributes to represent body parts
                setattr(self._body, body_part, ListElement(self._body, PART_STATUS))
                # verify the newly created Element
                part_inst = getattr(self._body, body_part)
                setattr(part_inst, 'dr', type('dr', (object,), {})())
                part_inst.verify()
        return self._body

    def cache_body_dr(self):
        """
        caches dr for a body part.
        Currently dr for a body part is received only from worn armor.

        example:
        body.head.dr.DAMAGE_TYPE=int, dr value of a type from the DAMAGE_TYPES list
            for example body.head.dr.PRC for peirce

        This is automatically called in:
        typeclasses.equipment.clothing.UMClothing.wear
        typeclasses.equipment.clothing.UMClothing.Clothing.remove
        typeclasses.objects.at_init
        typeclasses.characters.at_init
        typeclasses.exits.at_init

        Unit Test:
            commands.test.TestCommands.test_wear_remove
        """
        # clear the previous cache
        for part in self.body.parts:
            part_inst = getattr(self.body, part, False)
            if part_inst:
                for dmg_type in DAMAGE_TYPES:
                    if hasattr(part_inst.dr, dmg_type):
                        delattr(part_inst.dr, dmg_type)
            setattr(part_inst.dr, 'el_list', [])
        # cache worn dr
        for item in self.contents:
            if item.db.worn:
                # if this item covers a body part
                if item.db.clothing_type in self.body.parts:
                    # get the body part this item covers
                    body_part = getattr(self.body, item.db.clothing_type)
                    # give the body part a list of dr types the armor supports, to mimic an Objects.dr
                    setattr(body_part.dr, 'el_list', item.dr.el_list)
                    # for damage types in the dr element list
                    for dmg_type in item.dr.el_list:
                        dmg_type_dr_rating = getattr(item.dr, dmg_type, 0)
                        setattr(body_part.dr, dmg_type, dmg_type_dr_rating)

    def get_body_part(self, part_name=False, log=False):
        """Return a randon or specified instance of a part on the object's body.

        Body part instances are ListElements. List Elements function very simular
            to python's dict object.
            ref: utils.element.ListElement
            Created using keys: world.rules.body.PART_STATUS:
                ('broke', 'bleeding', 'missing', 'occupied', 'wielding',)
        Body parts retain python's standard attribute format.
        The name attribute is the name of the body part.
        As it is an instance of an object spaces are replaced with _.
        Get a parts name with:
            part = body.body_part()
            part_name = part.name.replace('_', ' ')  # replace _ with spaces

        Unit Tests:
            commands.test.TestCommands.test_get_body_part
            world.tests.test_rules
            commands.test.TestCommands.test_wear_remove

        Args:
            part_name (bool, optional), String name of a body part. Defaults to None.
                Example: 'left_leg'
            log (bool, optional), Should variables be logged. Defaults to False.

        Returns:
            body_part (ListElement): Functions very simular to python dict.
                ref: utils.element.ListElement
                Created using keys: world.rules.body.PART_STATUS:
                    ('broke', 'bleeding', 'missing', 'occupied', 'wielding',)

        Todo:
            option to target low middle or high
        """
        return body.get_part(self, part_name, log)

    def ascending_breakpoint(self):
        """
        This is automatically called when an object's hp rises above it's breakpoint (likely 0), when it was previous below it's breakpoint.
        Here to be overridden.
        """
        self.set_unconscious(False)

    def descending_breakpoint(self):
        """
        This is automatically called when an object's hp falls below it's breakpoint (likely 0), when it was previous above it's breakpoint.
        Here to be overridden.
        """
        self.set_unconscious(True)

    def destroy(self):
        """
        Here to be overridden.
        This is automatically called an an object's hp reaches self.hp.min
            normally -100
            Characters with a hp_max_mod, will reflect on the minimum also.
        """

    def at_init(self):
        """
        This is always called whenever this object is initiated --
        that is, whenever it its typeclass is cached from memory. This
        happens on-demand first time the object is used or activated
        in some way after being created but also after each server
        restart or reload.

        UniqueMud:
            Used to cache dr values for objects body parts.
        """
        self.cache_body_dr()  # cache dr worn on body
        self.hp.descending_breakpoint_func = self.descending_breakpoint
        self.hp.ascending_breakpoint_func = self.ascending_breakpoint
        self.hp.min_func = self.destroy
        return super().at_init()  # Here only to support future change to evennia's Character.at_init

    def at_object_creation(self):
        """Runs when Object is created."""
        self.at_init()  # initialize self.
        return super().at_object_creation()


class AllObjectsMixin:
    """
    Creates basic attributes and methods that are shared on all objects.
        Rooms, Objects, Characters and Exits

    Attributes:
        These attributes automatically manage self.attributes.attr_type in the database.

        targetable = False  # is the object targetable.
        container = False  # Can the object contain other objects
    """

    @property
    def targetable(self):
        """
        python property to make an object targetable with actions.

        Usage:
            object.targetable = True  # make an object targetable.
            if object.targetable:  # check if an object is targetable.
        """
        if self.attributes.has('targetable'):
            return self.db.targetable
        else:
            return False

    @targetable.setter
    def targetable(self, value):
        """
        Setter property for targetable

        Usage:
            if truthy True will be saved to the database.
                truth means is value is anything other than false, None or 0
        """
        if value:
            self.db.targetable = True
        else:
            self.attributes.remove('targetable')

    @targetable.deleter
    def targetable(self):
        """Delete method for targetable"""
        self.attributes.remove('targetable')

    @property
    def container(self):
        """
        Is used to allow objects to be stored in this object.
        Created for containers like backpacks. Can be used for things like hooks on a door.

        Usage:
            object.container = True  # make an object container.
            if object.container:  # check if an object is container.
        """
        if self.attributes.has('container'):
            return self.db.container
        else:
            return False

    @container.setter
    def container(self, value):
        """
        Setter property for container

        Usage:
            if truthy True will be saved to the database.
                truth means is value is anything other than false, None or 0
        """
        if value:
            self.db.container = True
        else:
            self.attributes.remove('container')

    @container.deleter
    def container(self):
        """Delete method for container"""
        self.attributes.remove('container')

    def emote_contents(self, text, sender, target=None, anonymous_add=None, exclude=None):
        """
        send emote to contents of an object.

        Arguments:
            text (str): The raw emote string as input by emoter.
            sender (Object): The one sending the emote.
            target (iterable): objects to replace /target switch with.
            anonymous_add (str or None, optional): If `sender` is not
                self-referencing in the emote, this will auto-add
                `sender`'s data to the emote. Possible values are
                - None: No auto-add at anonymous emote
                - 'last': Add sender to the end of emote as [sender]
                - 'first': Prepend sender to start of emote.

        Example:
            "/Me punches at /target "
            from a by stander: "A tall man punches at a short name "
            from the target of the attach: "A tall man punches at you "
            from the sender (or command caller) "You punches at a short man "
                Normally the command caller and target get custom messages.

        Notes:
            All standard evennia switches are supported.
            /me will be replaced with "you" for the sender.
            /target will be replaced with the display name of the target.
                From the receivers recog attribute for the target.
                For example if they recog a friend with a proper name.
            Capitalization of /Me or /Target results in the name being upper cased.
                This does NOT work as string.capitalize(), ONLY the first character
                is adjusted. Meaning following character's in the string can be
                upper cased.
                Example: /Target may be replaced with "A big fish flops"
                         where /target would show "a big fish flops"
            If a receiver has a recog for a /target or /me entry, it will have the
                potential of being upper case. This allows for players to recog
                with proper names.
            This method is a very light wrapper for utils.um_utils.um_emote.
            If a feature is supported there, it will be supported here.

        Unit Tests:
            commands.tests.TestCommands.test_um_emote, indirectly
            This will be directly tested in most commands scripts and other.
        """
        receivers = self.contents
        if exclude:
            exclude = make_iter(exclude)
            receivers = [obj for obj in receivers if obj not in exclude]
        um_emote(text, sender, receivers, target, anonymous_add)


    def emote(self, text, target=None, sender=None, receivers=None, anonymous_add=None):
        """
        send emote to contents of an object.

        Arguments:
            text (str): The raw emote string as input by emoter.
            target (iterable): objects to replace /target switch with.
            sender (Object)=self: The one sending the emote.
            receivers (iterable)=self: Receivers of the emote. These
                will also form the basis for which sdescs are
                'valid' to use in the emote.
            anonymous_add (str or None, optional): If `sender` is not
                self-referencing in the emote, this will auto-add
                `sender`'s data to the emote. Possible values are
                - None: No auto-add at anonymous emote
                - 'last': Add sender to the end of emote as [sender]
                - 'first': Prepend sender to start of emote.

        Example:
            "/Me punches at /target "
            from a by stander: "A tall man punches at a short name "
            from the target of the attach: "A tall man punches at you "
            from the sender (or command caller) "You punches at a short man "
                Normally the command caller and target get custom messages.

        Notes:
            All standard evennia switches are supported.
            /me will be replaced with "you" for the sender.
            /target will be replaced with the display name of the target.
                From the receivers recog attribute for the target.
                For example if they recog a friend with a proper name.
            Capitalization of /Me or /Target results in the name being upper cased.
                This does NOT work as string.capitalize(), ONLY the first character
                is adjusted. Meaning following character's in the string can be
                upper cased.
                Example: /Target may be replaced with "A big fish flops"
                         where /target would show "a big fish flops"
            If a receiver has a recog for a /target or /me entry, it will have the
                potential of being upper case. This allows for players to recog
                with proper names.
            This method is a very light wrapper for utils.um_utils.um_emote.
            If a feature is supported there, it will be supported here.

        Unit Tests:
            commands.tests.TestCommands.test_um_emote, indirectly
            This will be directly tested in most commands scripts and other.
        """
        if not sender:
            sender = self
        if not receivers:
            receivers = self
        um_emote(text, sender, receivers, target, anonymous_add)

    def emote_location(self, text, target=None, sender=None, skip_caller=True, anonymous_add=None, exclude=None):
        """
        Emote everyone in the caller's location with a message.

        Args:
            caller (Object or None): Sender of the message. If None, there
                is no sender.
            text (str): Message to parse and send to the room.
            skip_caller (bool): Send to everyone except caller.

        """
        receivers = self.location.contents
        sender = self if not sender else sender
        # remove caller from emote receivers.
        if skip_caller:
            if self in receivers:
                receivers.remove(self)
        # remove excluded objects from receivers
        if exclude:
            exclude = make_iter(exclude)
            receivers = [obj for obj in receivers if obj not in exclude]
        um_emote(text, sender, receivers, target, anonymous_add)

class ExObjAndRoomMixin:
    """
    Creates basic attributes for Exits Objects and Rooms.
    This is a mixin class. Should be a secondary inherit.
        class Object(ExObjAndRoomMixin, ContribRPObject):

    Attributes:
        usdesc = self.key, universal sdesc. Uses self.key.
        Exits also on Character to allow for cross object support.
    """

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
        return self.key

    @usdesc.setter
    def usdesc(self, value):
        """Setter property for usdesc"""
        self.key = value
