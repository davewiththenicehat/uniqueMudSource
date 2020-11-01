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
