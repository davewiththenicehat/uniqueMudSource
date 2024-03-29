"""
Clothing - Provides a typeclass and commands for wearable clothing,
which is appended to a character's description when worn.

Evennia contribution - Tim Ashley Jenkins 2017

Clothing items, when worn, are added to the character's description
in a list. For example, if wearing the following clothing items:

    a thin and delicate necklace
    a pair of regular ol' shoes
    one nice hat
    a very pretty dress

A character's description may look like this:

    Superuser(#1)
    This is User #1.

    Superuser is wearing one nice hat, a thin and delicate necklace,
    a very pretty dress and a pair of regular ol' shoes.

Characters can also specify the style of wear for their clothing - I.E.
to wear a scarf 'tied into a tight knot around the neck' or 'draped
loosely across the shoulders' - to add an easy avenue of customization.
For example, after entering:

    wear scarf draped loosely across the shoulders

The garment appears like so in the description:

    Superuser(#1)
    This is User #1.

    Superuser is wearing a fanciful-looking scarf draped loosely
    across the shoulders.

Items of clothing can be used to cover other items, and many options
are provided to define your own clothing types and their limits and
behaviors. For example, to have undergarments automatically covered
by outerwear, or to put a limit on the number of each type of item
that can be worn. The system as-is is fairly freeform - you
can cover any garment with almost any other, for example - but it
can easily be made more restrictive, and can even be tied into a
system for armor or other equipment.

To install, import this module and have your default character
inherit from UMClothedCharacter in your game's characters.py file:

    from typeclasses.equipment.clothing. import UMClothedCharacter

    class Character(UMClothedCharacter):

And then add UMClothedCharacterCmdSet in your character set in your
game's commands/default_cmdsets.py:

    from typeclasses.equipment.clothing. import UMClothedCharacterCmdSet

    class CharacterCmdSet(default_cmds.CharacterCmdSet):
         ...
         at_cmdset_creation(self):

             super().at_cmdset_creation()
             ...
             self.add(UMClothedCharacterCmdSet)    # <-- add this

From here, you can use the default builder commands to create clothes
with which to test the system:

    @create a pretty shirt : typeclasses.equipment.clothing.UMClothing
    @set shirt/clothing_type = 'top'
    wear shirt

"""

from evennia import DefaultObject
from evennia import DefaultCharacter
from evennia import default_cmds
from evennia.utils import list_to_string
from evennia.utils import evtable
from typeclasses.objects import Object
from commands.command import Command
from world.rules.body import HUMANOID_BODY
from world.rules.damage import TYPES as DAMAGE_TYPES
from utils.um_utils import highlighter

# Options start here.
# Maximum character length of 'wear style' strings, or None for unlimited.
WEARSTYLE_MAXLENGTH = 50

# The rest of these options have to do with clothing types. Clothing types are optional,
# but can be used to give better control over how different items of clothing behave. You
# can freely add, remove, or change clothing types to suit the needs of your game and use
# the options below to affect their behavior.

# The order in which clothing types appear on the description. Untyped clothing
# or clothing with a type not given in this list goes last.
# Also used in misc loops. Place covered clothing type below types that get
# covered.
CLOTHING_TYPE_ORDER = [
    "hat",
    "jewelry",
    "top",
    "undershirt",
    "gloves",
    "fullbody",
    "bottom",
    "underpants",
    "socks",
    "shoes",
    "accessory",
]
# The maximum number of each type of clothes that can be worn. Unlimited if untyped or not specified.
CLOTHING_TYPE_LIMIT = {
    "hat": 1,
    "jewelry": 1,
    "fullbody": 1,
    "top": 1,
    "undershirt": 1,
    "gloves": 1,
    "bottom": 1,
    "underpants": 1,
    "socks": 1,
    "shoes": 1,
    "accessory": 1
}

# The maximum number of clothing items that can be worn, or None for unlimited.
# Support for this removed. Limit is supported per item.
# CLOTHING_OVERALL_LIMIT = 20
# What types of clothes will automatically cover what other types of clothes when worn.
# Note that clothing only gets auto-covered if it's already worn when you put something
# on that auto-covers it - for example, it's perfectly possible to have your underpants
# showing if you put them on after your pants!
CLOTHING_TYPE_AUTOCOVER = {
    "top": ["undershirt"],
    "bottom": ["underpants"],
    "fullbody": ["undershirt", "underpants"],
    "shoes": ["socks"],
}
# Types of clothes that can't be used to cover other clothes.
CLOTHING_TYPE_CANT_COVER_WITH = ["jewelry"]
# used to refer to the clothing class, to make this easier to create instances of
CLOTHING_OBJECT_CLASS = "typeclasses.equipment.clothing.UMClothing"

# HELPER FUNCTIONS START HERE


def order_clothes_list(clothes_list):
    """
    Orders a given clothes list by the order specified in CLOTHING_TYPE_ORDER.

    Args:
        clothes_list (list): List of clothing items to put in order

    Returns:
        ordered_clothes_list (list): The same list as passed, but re-ordered
                                     according to the hierarchy of clothing types
                                     specified in CLOTHING_TYPE_ORDER.
    """
    ordered_clothes_list = clothes_list
    # For each type of clothing that exists...
    for current_type in reversed(CLOTHING_TYPE_ORDER):
        # Check each item in the given clothes list.
        for clothes in clothes_list:
            # If the item has a clothing type...
            if clothes.db.clothing_type:
                item_type = clothes.db.clothing_type
                # And the clothing type matches the current type...
                if item_type == current_type:
                    # Move it to the front of the list!
                    ordered_clothes_list.remove(clothes)
                    ordered_clothes_list.insert(0, clothes)
    return ordered_clothes_list


def get_worn_clothes(character, exclude_covered=False):
    """
    Get a list of clothes worn by a given character.

    Args:
        character (obj): The character to get a list of worn clothes from.

    Kwargs:
        exclude_covered (bool): If True, excludes clothes covered by other
                                clothing from the returned list.

    Returns:
        ordered_clothes_list (list): A list of clothing items worn by the
                                     given character, ordered according to
                                     the CLOTHING_TYPE_ORDER option specified
                                     in this module.
    """
    clothes_list = []
    for thing in character.contents:
        # If uncovered or not excluding covered items
        if not thing.db.covered_by or exclude_covered is False:
            # If 'worn' is True, add to the list
            if thing.db.worn:
                clothes_list.append(thing)
    # Might as well put them in order here too.
    ordered_clothes_list = order_clothes_list(clothes_list)
    return ordered_clothes_list


def clothing_type_count(clothes_list):
    """
    Returns a dictionary of the number of each clothing type
    in a given list of clothing objects.

    Args:
        clothes_list (list): A list of clothing items from which
                             to count the number of clothing types
                             represented among them.

    Returns:
        types_count (dict): A dictionary of clothing types represented
                            in the given list and the number of each
                            clothing type represented.
    """
    types_count = {}
    for garment in clothes_list:
        if garment.db.clothing_type:
            type = garment.db.clothing_type
            if type not in list(types_count.keys()):
                types_count[type] = 1
            else:
                types_count[type] += 1
    return types_count


def single_type_count(clothes_list, type):
    """
    Returns an integer value of the number of a given type of clothing in a list.

    Args:
        clothes_list (list): List of clothing objects to count from
        type (str): Clothing type to count

    Returns:
        type_count (int): Number of garments of the specified type in the given
                          list of clothing objects
    """
    type_count = 0
    for garment in clothes_list:
        if garment.db.clothing_type:
            if garment.db.clothing_type == type:
                type_count += 1
    return type_count


class UMClothing(Object):
    """
    Class of clothing objects.

    Attributes:
        type_limit=dict, The maximum number of each type of clothes that can be worn. Unlimited if untyped or not specified.
            example: {"clothing_type": 1}, where 1 is the number of cloths that can be worn on that location.
        type_autocover=dict, What types of clothes will automatically cover what other types of clothes when worn.
            Note that clothing only gets auto-covered if it's already worn when you put something
            on that auto-covers it - for example, it's perfectly possible to have your underpants
            showing if you put them on after your pants!
            example: {"clothing_type_covering": ["clothing_type_to_cover"]}

    Inherits:
        typeclasses.objects.Object
    """

    type_limit = CLOTHING_TYPE_LIMIT
    type_autocover = CLOTHING_TYPE_AUTOCOVER

    def at_object_creation(self):
        super().at_object_creation()
        self.targetable = True

    def wear(self, wearer, wearstyle, quiet=False):
        """
        Sets clothes to 'worn' and optionally echoes to the room.

        Args:
            wearer (obj): character object wearing this clothing object
            wearstyle (True or str): string describing the style of wear or True for none

        Kwargs:
            quiet (bool): If false, does not message the room

        Notes:
            Optionally sets db.worn with a 'wearstyle' that appends a short passage to
            the end of the name  of the clothing to describe how it's worn that shows
            up in the wearer's desc - I.E. 'around his neck' or 'tied loosely around
            her waist'. If db.worn is set to 'True' then just the name will be shown.
        """
        # Set clothing as worn
        self.db.worn = wearstyle
        # Auto-cover appropirate clothing types, as specified above
        to_cover = []
        if self.db.clothing_type and self.db.clothing_type in self.type_autocover:
            for garment in get_worn_clothes(wearer):
                if (
                    garment.db.clothing_type
                    and garment.db.clothing_type in self.type_autocover[self.db.clothing_type]
                ):
                    to_cover.append(garment)
                    garment.db.covered_by = self
        # Return if quiet
        if quiet:
            return True
        # Echo a message to the room
        room_msg = f"/Me wears /target"
        wearer_msg = f"You wear /target"
        if wearstyle is not True:
            room_msg = f"/Me wears /target {wearstyle}"
            wearer_msg = f"You wear /target {wearstyle}"
        if to_cover:
            room_msg += f", covering {list_to_string(to_cover)}"
            wearer_msg += f", covering {list_to_string(to_cover)}"
        wearer.emote_location(room_msg + ".", self)
        wearer.emote(wearer_msg + ".", self)

        # cache dr change for body parts, incase clothing is armor
        wearer.cache_body_dr()

        return True  # wear successful

    def remove(self, wearer, quiet=False):
        """
        Removes worn clothes and optionally echoes to the room.

        Args:
            wearer (obj): character object wearing this clothing object

        Kwargs:
            quiet (bool): If false, does not message the room

        Unit Tests:
            commands.tests.TestCommands.test_remove_wear
        """
        #remove the clothing
        self.db.worn = False
        # message wearer and room
        room_msg = f"/Me removes /target"
        wearer_msg = f"You remove /target"
        uncovered_list = []
        # Check to see if any other clothes are covered by this object.
        for thing in wearer.contents:
            # If anything is covered by
            if thing.db.covered_by == self:
                thing.db.covered_by = False
                uncovered_list.append(thing.name)
        if len(uncovered_list) > 0:
            uncov_msg = list_to_string(uncovered_list)
            room_msg += f", revealing {uncov_msg}"
            wearer_msg += f", revealing {uncov_msg}"
        # Echo a message to the room
        if not quiet:
            wearer.emote_location(room_msg + ".", self)
            wearer.emote(wearer_msg + ".", self)
        # cache dr change for body parts, incase clothing is armor
        wearer.cache_body_dr()
        # command run successful
        return True

    def at_get(self, getter):
        """
        Makes absolutely sure clothes aren't already set as 'worn'
        when they're picked up, in case they've somehow had their
        location changed without getting removed.
        """
        self.db.worn = False

class HumanoidArmor(UMClothing):
    """
    inherits typeclasses.equipment.UMClothing

    Armor tested in commands.tests
    """
    def at_init(self):
        """
        This is always called whenever this object is initiated --
        that is, whenever it its typeclass is cached from memory. This
        happens on-demand first time the object is used or activated
        in some way after being created but also after each server
        restart or reload.

        UniqueMud:
            Used to add the armor's body cover type to the self.type_limit attribute
            and to create an updated self.type_autocover
        """
        # add parts of the humanoid body to the humadoid armor type list.
        # allowing for additional clothing types.
        for part in HUMANOID_BODY:
            self.type_limit.update({part: 1})
        #add to the autocover list. So armor can cover cloths.
        self.type_autocover.update({
            "chest": ["undershirt", "top", "fullbody"],
            "right_foot": ["shoes", "socks"],
            "left_foot": ["shoes", "socks"],
            "head": ["hat"],
        })
        return super().at_init()  # Here only to support future change to evennia's Object.at_init

class UMClothedCharacter(DefaultCharacter):
    """
    Character that displays worn clothing when looked at. You can also
    just copy the return_appearance hook defined below to your own game's
    character typeclass.
    """

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.

        Notes:
            The name of every clothing item carried and worn by the character
            is appended to their description. If the clothing's db.worn value
            is set to True, only the name is appended, but if the value is a
            string, the string is appended to the end of the name, to allow
            characters to specify how clothing is worn.

        Unit Tests:
            commands.tests.TestCommands.test_wear_remove
        """
        if not looker:
            return ""
        # get description, build string
        string = ""
        worn_string_list = []
        clothes_list = get_worn_clothes(self, exclude_covered=True)
        # Append worn, uncovered clothing to the description
        for garment in clothes_list:
            # If 'worn' is True, just append the name
            if garment.db.worn is True:
                worn_string_list.append(garment.name)
            # Otherwise, append the name and the string value of 'worn'
            elif garment.db.worn:
                worn_string_list.append("%s %s" % (garment.name, garment.db.worn))
        if looker == self:
            string += "You are "
        else:
            string += f"{self.get_display_name(looker)} is "
        # Append worn clothes.
        if worn_string_list:
            string += f"wearing {list_to_string(worn_string_list)}."
        else:
            string += "not wearing anything."
        return string


# COMMANDS START HERE

class ClothingCommand(Command):
    """A command class for clothing commands"""
    help_category = "clothing"

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.can_not_target_self = True  # if True this command will end with a message if the Character targets themself
        self.cmd_type = "clothing"  # Should be a string of the command type. IE: 'evasion' for an evasion command
        self.target_inherits_from = (CLOTHING_OBJECT_CLASS, 'clothing and armor') # a tuple, position 0 string of a class type, position 1 is a string to show on mismatch
        self.search_caller_only = True  # if True the command will only search the caller for targets

class CmdWear(ClothingCommand):
    """
    Puts on an item of clothing or armor you are holding.

    Usage:
      wear name of attire

    Examples:
      wear shirt
      wear dented armor

    All the clothes you are wearing are appended to your description.
    """

    key = "wear"
    # self.target_in_hand = True  # has been manually written into
    # custom_requirements so support showing an item is already worn

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        clothing = self.target
        worn_clothes = get_worn_clothes(caller)

        # removed this, this is enforced per item type.
        # Enforce overall clothing limit.
        # if CLOTHING_OVERALL_LIMIT and len(worn_clothes) >= CLOTHING_OVERALL_LIMIT:
        #    caller.msg("You can't wear any more clothes.")
        #    return False
        # Apply individual clothing type limits.
        if clothing.db.clothing_type and not clothing.db.worn:
            type_count = single_type_count(worn_clothes, clothing.db.clothing_type)
            if clothing.db.clothing_type in list(clothing.type_limit.keys()):
                if type_count >= clothing.type_limit[clothing.db.clothing_type]:
                    for worn_article in worn_clothes:
                        if worn_article.db.clothing_type == clothing.db.clothing_type:
                            worn_art_name = worn_article.get_display_name(caller)
                    remove_cmd = f"remove {worn_article.get_display_name(caller)}"
                    remove_sugg = highlighter(remove_cmd, click_cmd=remove_cmd)
                    err_msg = f"You are wearing {worn_art_name} on your " \
                              f"{clothing.db.clothing_type}. You will need to " \
                              f"remove it first, try {remove_sugg}."
                    caller.msg(err_msg)
                    return False
        # check if the player is already wearing the item
        # if clothing.db.worn and len(self.arglist) == 1:
        if clothing.db.worn:
            caller.msg(f"You are already wearing {clothing.get_display_name(caller)}.")
            return False
        # if the Character is not holding the object to be wielded, stop the command
        if not caller.is_holding(clothing):
            stop_msg = f"You have to hold an object you want to " \
                       f"{self.cmdstring}.|/"
            get_cmd = f"get {clothing.get_display_name(caller)}"
            get_suggestion = highlighter(get_cmd, click_cmd=get_cmd)
            stop_msg += f"Try getting it with {get_suggestion}."
            caller.msg(stop_msg)
            return False
        # If armor, check if the Character has the body type required for the armor.
        if not (clothing.db.clothing_type in caller.body.parts or clothing.db.clothing_type in CLOTHING_TYPE_ORDER):
            caller.msg(f"You do not have a {clothing.db.clothing_type} to equip {clothing.get_display_name(caller)} to.")
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        room_message = f'/Me begins to put on /target.'
        caller_message = f'You begin to put on /target.'
        caller.emote_location(room_message, target)
        caller.emote(caller_message, target)

    def deferred_action(self):
        """The command completed, without receiving an attack."""
        caller = self.caller
        clothing = self.target

        wearstyle = True  # removed support for wearstyle
        wear_successful = clothing.wear(caller, wearstyle)
        # empty the hand that was holding the item worn
        if wear_successful:
            hand = caller.is_holding(clothing)
            if hand:
                # the worn item was also being wielded
                if hand.occupied == hand.wielding:
                    hand.wielding = 0  # unwield the item
                hand.occupied = 0  # unoccupy the hand


class CmdRemove(ClothingCommand):
    """
    Takes off an item of clothing.

    Usage:
       remove <obj>

    Removes an item of clothing you are wearing. You can't remove
    clothes that are covered up by something else - you must take
    off the covering item first.
    """

    key = "remove"

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        clothing = self.target
        # is the character wearing the clothing
        if not clothing.db.worn:
            caller.msg(f"You are not wearing {clothing.get_display_name(caller)}.")
            return False
        if clothing.db.covered_by:
            remove_cmd = f"remove {clothing.db.covered_by.get_display_name(caller)}"
            remove_sugg = highlighter(remove_cmd, click_cmd=remove_cmd)
            err_msg = f"You are wearing {clothing.db.covered_by.get_display_name(caller)} over " \
                      f"{clothing.get_display_name(caller)}. Try removing {clothing.db.covered_by.get_display_name(caller)} " \
                      f"first with {remove_sugg}."
            caller.msg(err_msg)
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        room_message = f'/Me begins to remove /target.'
        caller_message = f'You begin to remove /target.'
        caller.emote_location(room_message, target)
        caller.emote(caller_message, target)

    def deferred_action(self):
        """The command completed, without receiving an attack."""
        caller = self.caller
        clothing = self.target
        success = clothing.remove(caller)
        if success:
            # get open hands
            open_hands = caller.open_hands()
            # hands are full, stop the command
            # this repeat error checking is here itenetionally do not remove
            if not open_hands:
                caller.msg("Your hands are full.")
                clothing.db.worn = True
                return
            else:
                open_hand = open_hands[0]  # hand of the first open hand
            # occupy the hand used to get the object
            if open_hand:
                # occupy with dbref to make it very easy to search for items in hand
                open_hand.occupied = clothing.dbref


class CmdArmor(Command):
    """
    Display the armor status of your Character.

    Usage:
        armor: Show armor worn on entire body.
        armor [body part name]: show the armor worn on a single body part.

    Time:
        By default completion time is 1 second.
    """

    key = 'armor'
    aliases = ['dr', 'damage reduction']

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        room_message = f'/Me begins to check {caller.get_pronoun("|p")} armor.'
        caller.emote_location(room_message)
        caller.msg('You begin to check your armor.')

    def deferred_action(self):
        """This method is called after defer_time seconds when the Command.defer method is used.

        Notes:
            Intended to be overritten. Simply put the action portions of a command in this method.
        Returns:
            successful (bool): True if the command completed sucessfully.
                If this method returns True self.def_act_comp will be called after automatically.
        """
        caller = self.caller
        # collect only body parts with damage reduction, from armor only
        armored_body_parts = {}
        for part in caller.body.parts:
            body_part_inst = getattr(caller.body, part, False)
            for dr in body_part_inst.dr.el_list:  # body parts dr is not a list element, it is a cache
                if dr:
                    armored_body_parts.update({part:  None})
                    continue
        # get worn armor dr values
        for item in caller.contents:
            if item.attributes.has('worn'):
                # the item is worn and is armor
                if item.db.worn and item.db.clothing_type in armored_body_parts:
                    part_name = item.db.clothing_type
                    armored_body_parts.update({part_name: item})
        # get natural dr values
        for dr in caller.dr:
            if dr:
                armored_body_parts.update({'natural': caller})
                break
        part_names = []
        armor_names = []
        dr_values = []
        # create empty holder lists for each damage type to be used as headers in an evtable
        for dmg_type in DAMAGE_TYPES:
            dr_values.append([])
        # Collect body part and item names into lists for evtable
        for part_name, item in armored_body_parts.items():
            if part_name == 'natural':
                part_names.append(highlighter('-all-', click_cmd='echo Natural armor applies to all body parts.'))
                click_cmd="echo Natural armor applies damage redution to a Character's entire body."
                armor_names.append(highlighter('natural', click_cmd=click_cmd))
            else:
                part_names.append(part_name)
                armor_names.append(item.get_display_name(caller))
            # create lists for each damage type in the same order as body part names
            i = 0
            for dmg_type in DAMAGE_TYPES:
                dr_values[i].append(item.dr[dmg_type])
                i += 1
        dmg_types_header = []
        for dmg_type in DAMAGE_TYPES:
            dmg_types_header.append(highlighter(dmg_type, click_cmd=f'help {dmg_type}'))
        msg_header = ['Body Part', 'Armor Name'] + dmg_types_header
        msg_list = [part_names, armor_names] + dr_values
        msg_table = evtable.EvTable(*msg_header, table=msg_list, border=None, pad_left=4)
        caller.msg(msg_table, force=True)
        room_message = f'/Me completes the check of {caller.get_pronoun("|p")} armor.'
        caller.emote_location(room_message)

class UMClothedCharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for clothing, including new versions of 'drop'
    that take worn and covered clothing into account, as well as a new
    version of 'inventory' that differentiates between carried and worn
    items.

    Unit tests for these commands are in commands.tests.TestCommands
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdWear())
        self.add(CmdRemove())
        self.add(CmdArmor())
