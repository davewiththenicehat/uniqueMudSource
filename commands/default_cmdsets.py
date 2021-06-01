"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from evennia.contrib.gendersub import SetGender
from commands.developer_cmds import DeveloperCmdSet
from commands.combat.unarmed import UnarmedCmdSet
from commands.combat.evasion import EvasionCmdSet
from commands.combat.one_handed import OneHandedCmdSet
from typeclasses.equipment.clothing import UMClothedCharacterCmdSet
from commands.standard_cmds import StandardCmdsCmdSet, UMRPSystemCmdSet
from typeclasses.equipment.wieldable import WieldableCmdSet


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.

    This class describes a unique cmdset that understands priorities.
    CmdSets can be merged and made to perform various set operations
    on each other.  CmdSets have priorities that affect which of their
    ingoing commands gets used.

    In the examples, cmdset A always have higher priority than cmdset B.

    key - the name of the cmdset. This can be used on its own for game
    operations

    mergetype (partly from Set theory):

        Union -    The two command sets are merged so that as many
                    commands as possible of each cmdset ends up in the
                    merged cmdset. Same-name commands are merged by
                    priority.  This is the most common default.
                    Ex: A1,A3 + B1,B2,B4,B5 = A1,B2,A3,B4,B5
        Intersect - Only commands found in *both* cmdsets
                    (i.e. which have same names) end up in the merged
                    cmdset, with the higher-priority cmdset replacing the
                    lower one.  Ex: A1,A3 + B1,B2,B4,B5 = A1
        Replace -   The commands of this cmdset completely replaces
                    the lower-priority cmdset's commands, regardless
                    of if same-name commands exist.
                    Ex: A1,A3 + B1,B2,B4,B5 = A1,A3
        Remove -    This removes the relevant commands from the
                    lower-priority cmdset completely.  They are not
                    replaced with anything, so this in effects uses the
                    high-priority cmdset as a filter to affect the
                    low-priority cmdset.
                    Ex: A1,A3 + B1,B2,B4,B5 = B2,B4,B5

                 Note: Commands longer than 2 characters and starting
                       with double underscrores, like '__noinput_command'
                       are considered 'system commands' and are
                       excempt from all merge operations - they are
                       ALWAYS included across mergers and only affected
                       if same-named system commands replace them.

    priority- All cmdsets are always merged in pairs of two so that
              the higher set's mergetype is applied to the
              lower-priority cmdset. Default commands have priority 0,
              high-priority ones like Exits and Channels have 10 and 9.
              Priorities can be negative as well to give default
              commands preference.

    duplicates - determines what happens when two sets of equal
                 priority merge. Default has the first of them in the
                 merger (i.e. A above) automatically taking
                 precedence. But if allow_duplicates is true, the
                 result will be a merger with more than one of each
                 name match.  This will usually lead to the account
                 receiving a multiple-match error higher up the road,
                 but can be good for things like cmdsets on non-account
                 objects in a room, to allow the system to warn that
                 more than one 'ball' in the room has the same 'kick'
                 command defined on it, so it may offer a chance to
                 select which ball to kick ...  Allowing duplicates
                 only makes sense for Union and Intersect, the setting
                 is ignored for the other mergetypes.

    key_mergetype (dict) - allows the cmdset to define a unique
             mergetype for particular cmdsets.  Format is
             {CmdSetkeystring:mergetype}. Priorities still apply.
             Example: {'Myevilcmdset','Replace'} which would make
             sure for this set to always use 'Replace' on
             Myevilcmdset no matter what overall mergetype this set
             has.

    no_objs  - don't include any commands from nearby objects
                  when searching for suitable commands
    no_exits  - ignore the names of exits when matching against
                        commands
    no_channels   - ignore the name of channels when matching against
                        commands (WARNING- this is dangerous since the
                        account can then not even ask staff for help if
                        something goes wrong)
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
        self.add(SetGender)
        self.add(DeveloperCmdSet)
        self.add(UnarmedCmdSet)
        self.add(EvasionCmdSet)
        self.add(OneHandedCmdSet)
        self.add(UMClothedCharacterCmdSet)
        self.add(UMRPSystemCmdSet)
        self.add(StandardCmdsCmdSet)  # has to be after rpsystem
        self.add(WieldableCmdSet)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
