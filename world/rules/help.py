from evennia import create_help_entry
from evennia import create_script
from evennia import GLOBAL_SCRIPTS
from evennia.help.models import HelpEntry

from typeclasses.scripts import Script
from world.rules.help_entries import ENTRIES


REFRESH_INTERVALS = 86400


def refresh_entries():
    """Refreshes old and create new entries in the help system."""
    for category, entries in ENTRIES.items():
        for entry_name, entry in entries.items():
            entry_inst = HelpEntry.objects.search_help(entry_name, help_category=category)
            entry_inst.delete()
            create_help_entry(entry_name, entry, category=category, locks="view:all()")


def remove_empty_entries():
    """Remove help entries if they are not in the hard coded list."""
    # create a list of coded static help entries
    entries_list = []
    for _, entries in ENTRIES.items():
        entries_list += entries.keys()
    # remove an entry if it is not in the static entries list.
    for entry in HelpEntry.objects.all():
        if entry.key not in entries_list:
            entry.delete()


def at_start_refresh_help():
    refresh_help_script = GLOBAL_SCRIPTS.get("refresh_help")
    # create the refresh help script if it does not already exist
    if "refresh_help" not in str(refresh_help_script):
        create_script("world.rules.help.RefreshHelp", key="refresh_help", persistent=True, obj=None)
    # always refresh help entries on server startup
    refresh_help_script = GLOBAL_SCRIPTS.get("refresh_help")
    refresh_help_script.at_repeat()


class RefreshHelp(Script):
    """Script to refreshing of the help entries system."""

    def at_script_creation(self):
        self.key = "refresh_help"
        self.interval = REFRESH_INTERVALS  # reapeat time
        self.persistent = True  # survies a reboot
        refresh_entries()

    def at_repeat(self):
        refresh_entries()
        remove_empty_entries()
