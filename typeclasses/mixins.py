from utils.element import Element


class ObjectBaseMixin:
    """
    Creates basic attributes that exist on all typeclasses.objects.Objects and
    typeclasses.characters.Character objects.
    This is a mixin class. Should be a secondary inherit.
        class Object(ObjectBaseMixin, ContribRPObject):

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


class ExitObjectAndRoomMixin:
    """
    A mixin for use with exits objects and rooms
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
