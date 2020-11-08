from world.rules.damage import DamageElement
from utils.element import Element, ListElement


class CharExAndObjMixin:
    """
    Creates basic attributes that exist on all typeclasses.objects.Objects and
    typeclasses.characters.Character objects.
    This is a mixin class. Should be a secondary inherit.
        class Object(CharExAndObjMixin, ContribRPObject):

    Attributes:
        hp = Element, the objects hit points or health
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
            self._dr = DamageElement(self)
            self._dr.verify()
        return self._dr

    @dr.setter
    def dr(self, value):
        self._dr.set(value)

    @dr.deleter
    def dr(self):
        self._dr.delete()

    @property
    def le(self):
        try:
            if self._le:
                pass
        except AttributeError:
            #element.LIST = ('tst1', 'tst2')
            self._le = ListElement(self)
            self._le.verify()
        return self._le

    @le.setter
    def le(self, value):
        self._le.set(value)

    @le.deleter
    def le(self):
        self._le.delete()


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
        Universal Short Description

        A usdesc exists on each evennia object type Object, Character, Room and Exit

        usdesc refers to self.key on Exits, Objects and rooms
        usdesc refers to self.sdesc on Characters

        Usage:
           caller.msg(f'You attack {target.usdesc}.)  # to get
           target.usdesc = 'a happy tree'  # to set
        """
        return self.key

    @usdesc.setter
    def usdesc(self, value):
        """Setter property for usdesc"""
        self.key = value
