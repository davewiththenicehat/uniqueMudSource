from utils.element import Element


class ObjectBaseMixin:

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
