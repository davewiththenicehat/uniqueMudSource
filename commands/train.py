from evennia import Command, CmdSet

class CmdEnterTrain(Command):
    """
    entering the train

    Usage:
      enter train

    This will be available to players in the same location
    as the train and allows them to embark.
    """

    key = "enter train"
    locks = "cmd:not cmdinside()"

    def func(self):
        train = self.obj
        self.caller.msg("You board the train.")
        self.caller.move_to(train)


class CmdLeaveTrain(Command):
    """
    leaving the train

    Usage:
      leave train

    This will be available to everyone inside the
    train. It allows them to exit to the train's
    current location.
    """

    key = "leave train"
    locks = "cmd:cmdinside()"

    def func(self):
        train = self.obj
        parent = train.location
        self.caller.move_to(parent)


class CmdSetTrain(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdEnterTrain())
        self.add(CmdLeaveTrain())
