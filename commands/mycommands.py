from evennia import default_cmds
# our custom MuxCommand with at_post_cmd hook
from commands.command import MuxCommand

# overloading the look command
class CmdLook(default_cmds.CmdLook, MuxCommand):
    pass
