from typeclasses.objects import Object
from typeclasses.mixins.invisible import RespectInvisibilityMixin


class InvisibleObject(RespectInvisibilityMixin, Object):
    """
    Example on not to make an InvisibleObject
    """

    def at_object_creation(self):
        self.locks.add("visible:false()")
        self.locks.add("view:false()")
