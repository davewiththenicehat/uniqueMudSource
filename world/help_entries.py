"""
File-based help entries. These complements command-based help and help entries
added in the database using the `sethelp` command in-game.

Control where Evennia reads these entries with `settings.FILE_HELP_ENTRY_MODULES`,
which is a list of python-paths to modules to read.

A module like this should hold a global `HELP_ENTRY_DICTS` list, containing
dicts that each represent a help entry. If no `HELP_ENTRY_DICTS` variable is
given, all top-level variables that are dicts in the module are read as help
entries.

Each dict is on the form
::

    {'key': <str>,
     'category': <str>,   # optional, otherwise settings.DEFAULT_HELP_CATEGORY
     'aliases': <list>,   # optional
     'text': <str>}``     # the actual help text. Can contain # subtopic sections

"""

from utils.um_utils import highlighter

HELP_ENTRY_DICTS = [
    {
        "key": "Unique Mud",
        "category": "General",
        "text": f"""
        Thank you for playing.

        For game world and rules use: {highlighter("help rules", click_cmd="help rules")}
        To view all your character's commands: {highlighter("help commands", click_cmd="help commands")}
        For all commands and help topics: {highlighter("help all", click_cmd="help all")}

        """
    },
]
