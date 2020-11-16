from world.rules.damage import TYPES as DAMAGE_TYPES
from utils.element import Element, ListElement
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
            For example humans would be ('head', 'shoulders' so on.
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
           body.head.dr.DAMAGE_TYPE=int, dr value of a type from the DAMAGE_TYPES list
               for example body.head.dr.PRC for peirce
           body.head.PART_STATUS=boolean, a status from the PART_STATUS list.
               for example body.head.bleeding, for bleeding

    Methods:
        get_body_part(no_understore=False), Return the name of a body part that exists on this Object
        cache_body_dr(), caches dr for all this Object's body parts
    """

    # define objects's HP
    @property
    def hp(self):
        try:
            if self._hp:
                pass
        except AttributeError:
            self._hp = Element(self)
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
        typeclasses.equipment.clothing.Clothing.wear
        typeclasses.equipment.clothing.Clothing.Clothing.remove
        typeclasses.objects.at_init
        typeclasses.characters.at_init
        typeclasses.exits.at_init

        Unit test for this in commands.test
        """
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
                        dmg_type_dr_rating = getattr(item.dr, dmg_type)
                        setattr(body_part.dr, dmg_type, dmg_type_dr_rating)

    def get_body_part(self, no_understore=False, log=False):
        """
        Return the name of a body part that exists on this Object

        Arguments:
            no_understore=False, if True underscores '_' will be removed from the returned part name.
            log=False, if True log the variables used

        Returns:
            str, in the form of a body part description.
                Example: "head" or "waist"
            False, if this object has no body parts to hit.
            None, the function failed on the python level.
        """
        return body.get_part(self, no_understore, log)

    def break_func(self):
        """
        Here to be overridden.
        This is automatically called when an object's hp reaches 0.
        """

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
        self.hp.breakpoint_func = self.break_func
        self.hp.min_func = self.destroy
        return super().at_init()  # Here only to support future change to evennia's Character.at_init


class AllObjectsMixin:
    """
    Creates basic attributes and methods that are shared on all objects.
        Rooms, Objects, Characters and Exits

    Attributes:
        targetable = False  # if the target is targetable.
            Is a property that references self.db automatically
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
        """
        return self.key

    @usdesc.setter
    def usdesc(self, value):
        """Setter property for usdesc"""
        self.key = value
