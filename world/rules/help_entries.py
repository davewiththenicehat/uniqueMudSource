"""This module conties entries for the static help system.

To use create a dictionary whose keys are the entry name and values are the help entries.

Once completed add you dictionary to the ENTRIES dictionary.
    Each key in this dictionary is a help catergory.
"""

from utils.um_utils import highlighter


BASIC_ENTRY = {
    'basic': f"""Basic help menu
    """
}

DMG_TYPES_ENTRIES = {
    'ACD': """Acid
    Special:
        acid damage
    """,
    #'BLG': 'bludgeoning',
    #'CLD': 'cold',
    #'FIR': 'fire',
    #'ELC': 'electric',
    #'MNT': 'mental',
    #'PRC': 'piercing',
    #'POI': 'poison',
    #'RAD': 'radiation',
    #'SLS': 'slashing'
}


def merge_dict(*args):
    mergere_dictionary = {}
    for dict_instance in args:
        mergere_dictionary.update(dict_instance)
    return mergere_dictionary


ENTRIES = {
    'rules': merge_dict(BASIC_ENTRY, DMG_TYPES_ENTRIES)
}
