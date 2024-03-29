import types, re
from unittest.mock import patch, Mock, MagicMock

from twisted.internet import task
from evennia.utils.test_resources import EvenniaTest
from evennia.commands.default.tests import CommandTest
from evennia import create_object
from evennia.utils import ansi, utils
from evennia.server.sessionhandler import SESSIONS
from evennia.commands.command import InterruptCommand

from typeclasses.accounts import Account
from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from typeclasses.scripts import Script
from typeclasses.equipment.wieldable import OneHandedWeapon
from typeclasses.equipment import clothing
from commands import developer_cmds

# set up signal here since we are not starting the server
_RE = re.compile(r"^\+|-+\+|\+-+|--+|\|(?:\s|$)", re.MULTILINE)

_TASK_HANDLER = None

class UniqueMudTest(EvenniaTest):
    """
    Base test for UniqueMud, sets up a basic environment.

    Attributes:
        task_handler (TASK_HANDLER): A local reference to the global task handler.
            The clock attribute is replaced with an instance of twisted.task.clock.
            Primarily to use task_handler.adavnace
        char1 (Character): Default choice for call's caller kwarg
        char2 (Character):
        exit (exit):
        room1 (Room):
        test_hat (UMClothing):
        test_shirt (UMClothing):
        test_helmet (HumanoidArmor):

    """

    account_typeclass = Account
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    script_typeclass = Script

    def setUp(self):
        """
        Sets up testing environment
        """
        # call inherited setUp
        super().setUp()
        # make character names something easy to tell apart,
        self.char1.usdesc = 'Char'
        self.char2.usdesc = 'Char2'
        # make objects targetable for testing
        self.obj1.targetable = True
        self.obj2.targetable = True
        self.sword = create_object(OneHandedWeapon, key="a sword")
        self.sword.targetable = True
        self.sword.location = self.char1.location
        self.test_hat = create_object(clothing.UMClothing, key="test hat")
        self.test_hat.db.clothing_type = "hat"
        self.test_hat.location = self.room1
        # Make a test shirt
        self.test_shirt = create_object(clothing.UMClothing, key="test shirt")
        self.test_shirt.db.clothing_type = "top"
        self.test_shirt.location = self.room1
        # Make a test helmet
        self.test_helmet = create_object(clothing.HumanoidArmor, key="test helmet")
        self.test_helmet.db.clothing_type = "head"
        self.test_helmet.location = self.room1


class UniqueMudCmdTest(UniqueMudTest):

    def setUp(self):
        super().setUp()
        # create a local reference
        global _TASK_HANDLER
        if _TASK_HANDLER is None:
            from evennia.scripts.taskhandler import TASK_HANDLER as _TASK_HANDLER
        self.task_handler = _TASK_HANDLER
        # replace the reactor clock with twisted's task clock.
        _TASK_HANDLER.clock = task.Clock()

    def call(
        self,
        cmdobj,
        args,
        msg=None,
        cmdset=None,
        noansi=True,
        caller=None,
        receiver=None,
        cmdstring=None,
        obj=None,
        inputs=None,
        raw_string=None,
    ):
        """
        Test a command by assigning all the needed
        properties to cmdobj and  running
            cmdobj.at_pre_cmd()
            cmdobj.parse()
            cmdobj.func()
            cmdobj.at_post_cmd()
        The msgreturn value is compared to eventual
        output sent to caller.msg in the game

        Returns:
            msg (str): The received message that was sent to the caller.

        """
        caller = caller if caller else self.char1
        receiver = receiver if receiver else caller
        cmdobj.caller = caller
        cmdobj.cmdname = cmdstring if cmdstring else cmdobj.key
        cmdobj.raw_cmdname = cmdobj.cmdname
        cmdobj.cmdstring = cmdobj.cmdname  # deprecated
        cmdobj.args = args
        cmdobj.cmdset = cmdset
        cmdobj.session = SESSIONS.session_from_sessid(1)
        cmdobj.account = self.account
        cmdobj.raw_string = raw_string if raw_string is not None else cmdobj.key + " " + args
        cmdobj.obj = obj or (caller if caller else self.char1)
        # test
        old_msg = receiver.msg
        inputs = inputs or []

        try:
            receiver.msg = Mock()
            if cmdobj.at_pre_cmd():
                return
            cmdobj.parse()
            ret = cmdobj.func()

            # handle func's with yield in them (generators)
            if isinstance(ret, types.GeneratorType):
                while True:
                    try:
                        inp = inputs.pop() if inputs else None
                        if inp:
                            try:
                                ret.send(inp)
                            except TypeError:
                                next(ret)
                                ret = ret.send(inp)
                        else:
                            next(ret)
                    except StopIteration:
                        break

            cmdobj.at_post_cmd()
        except StopIteration:
            pass
        except InterruptCommand:
            pass

        # clean out evtable sugar. We only operate on text-type
        stored_msg = [
            args[0] if args and args[0] else kwargs.get("text", utils.to_str(kwargs))
            for name, args, kwargs in receiver.msg.mock_calls
        ]
        # Get the first element of a tuple if msg received a tuple instead of a string
        stored_msg = [str(smsg[0]) if isinstance(smsg, tuple) else str(smsg) for smsg in stored_msg]
        if msg is not None:
            msg = str(msg)  # to be safe, e.g. `py` command may return ints
            # set our separator for returned messages based on parsing ansi or not
            msg_sep = "|" if noansi else "||"
            # Have to strip ansi for each returned message for the regex to handle it correctly
            returned_msg = msg_sep.join(
                _RE.sub("", ansi.parse_ansi(mess, strip_ansi=noansi)) for mess in stored_msg
            ).strip()
            msg = msg.strip()
            if msg == "" and returned_msg or not returned_msg.startswith(msg):
                sep1 = "\n" + "=" * 30 + "Wanted message" + "=" * 34 + "\n"
                sep2 = "\n" + "=" * 30 + "Returned message" + "=" * 32 + "\n"
                sep3 = "\n" + "=" * 78
                retval = sep1 + msg + sep2 + returned_msg + sep3
                raise AssertionError(retval)
        else:
            returned_msg = "\n".join(str(msg) for msg in stored_msg)
            returned_msg = ansi.parse_ansi(returned_msg, strip_ansi=noansi).strip()
        receiver.msg = old_msg
        return returned_msg

    def call_multi_receivers(
        self, cmdobj, args,
        receivers=dict(),
        cmdset=None, noansi=True,
        caller=None, cmdstring=None,
        obj=None, inputs=None,
        raw_string=None,
    ):
        """
        Runs a command.
        Tests text passed to this method against messages Objects should
        receive from this command.
        Allows support for multiple receives

        Arguments:
            cmdobj, an instance of a Command object
            args, a string of arguments that command should receive
            receivers=dict(), a dictionary of receives and the messages they
                should receive.
                Example:
                    receivers = {
                        self.char1: 'The sky is cloudy.',
                        self.char2: 'Char looks at the sky.'
                    }
            cmdset=None,
            noansi=True, Should ANSI sugar will be removed from message to test.
            caller=self.char1, Object that called the command
            cmdstring=None, deprecated
            obj=caller, Command.obj instance
            inputs=None, Inputs that may be required during command run.
                For example evemenu or yield
            raw_string=cmdobj.key + " " + args, Command.raw_string attribute

        Examples:

            # runs a basic command
            receivers = {
                self.char1: 'The sky is cloudy.',
                self.char2: 'Char looks at the sky.'
            }
            self.call_multi_receivers(CmdLook, 'sky', receivers)

            # runs a basic command, where char2 should see no message.
            receivers = {
                self.char1: 'The sky is cloudy.',
                self.char2: ''
            }
            self.call_multi_receivers(CmdLook, 'sky', receivers)

            # skip the call_multi_receivers test to run your own.
            receivers = {
                self.char1: None,
                self.char2: None'
            }
            cmd_result = self.call_multi_receivers(CmdLook, 'sky', receivers)
            # run your custom tests on cmd_result

            #run call_multi_receivers test and your own.
            receivers = {
                self.char1: 'The sky is cloudy.',
                self.char2: 'Char looks at the sky.'
            }
            cmd_result = self.call_multi_receivers(CmdLook, 'sky', receivers)
            # run your custom tests on cmd_result

        Returns:
            msg (str): Collection of messages sent to each receiver

        Raises:
            AssertionError, if the passed string in the receivers argument does
            not match what was sent to the Character that is the key of that
            dictionary entry. This raise will display both passed and message
            the command sent for comparison.

        """
        caller = caller if caller else self.char1
        # if not supplied make receivers the first Character found in the
        # same room as receiver or object if no other
        cmdobj.caller = caller
        cmdobj.cmdname = cmdstring if cmdstring else cmdobj.key
        cmdobj.raw_cmdname = cmdobj.cmdname
        cmdobj.cmdstring = cmdobj.cmdname  # deprecated
        cmdobj.args = args
        cmdobj.cmdset = cmdset
        cmdobj.session = SESSIONS.session_from_sessid(1)
        cmdobj.account = self.account
        cmdobj.raw_string = raw_string if raw_string is not None else cmdobj.key + " " + args
        cmdobj.obj = obj or (caller if caller else self.char1)
        inputs = inputs or []
        # look through receivers backup than mock their msg method
        receivers_msg_methods = list()
        for char in receivers.keys():
            receivers_msg_methods.append((char, char.msg))  # record the msg method inst
            char.msg = Mock()  # turn msg into a mock

        # Run the command
        try:
            if cmdobj.at_pre_cmd():
                return
            cmdobj.parse()
            ret = cmdobj.func()
            # handle func's with yield in them (generators)
            if isinstance(ret, types.GeneratorType):
                while True:
                    try:
                        inp = inputs.pop() if inputs else None
                        if inp:
                            try:
                                ret.send(inp)
                            except TypeError:
                                next(ret)
                                ret = ret.send(inp)
                        else:
                            next(ret)
                    except StopIteration:
                        break
            cmdobj.at_post_cmd()
        except StopIteration:
            pass
        except InterruptCommand:
            pass

        # check the wanted message against the one received.
        returned_msg = ''
        for receiver, msg in receivers.items():
            # clean out evtable sugar. We only to operate on text-type
            stored_msg = [
                args[0] if args and args[0] else kwargs.get("text", utils.to_str(kwargs))
                for name, args, kwargs in receiver.msg.mock_calls
            ]
            # Get the first element of a tuple if msg received a tuple instead of a string
            stored_msg = [str(smsg[0]) if isinstance(smsg, tuple) else str(smsg) for smsg in stored_msg]
            if msg is not None:
                msg = str(msg)  # to be safe, e.g. `py` command may return ints
                # set our separator for returned messages based on parsing ansi or not
                msg_sep = "|" if noansi else "||"
                # Have to strip ansi for each returned message for the regex to handle it correctly
                verif_msg = msg_sep.join(
                    _RE.sub("", ansi.parse_ansi(mess, strip_ansi=noansi)) for mess in stored_msg
                ).strip()
                msg = msg.strip()
                if msg == "" and verif_msg or not verif_msg.startswith(msg):
                    sep1 = "\n" + "=" * 30 + "Wanted message" + "=" * 34 + "\n"
                    sep2 = "\n" + "=" * 30 + "Returned message" + "=" * 32 + "\n"
                    sep3 = "\n" + "=" * 78
                    retval = sep1 + msg + sep2 + verif_msg + sep3
                    raise AssertionError(retval)
                returned_msg += verif_msg
            else:
                # removed ansi characters from message.
                cleaned_msg = "\n".join(str(msg) for msg in stored_msg)
                cleaned_msg = ansi.parse_ansi(cleaned_msg, strip_ansi=noansi).strip()
                returned_msg += cleaned_msg

        # return the receivers msg method
        for char, char_msg in receivers_msg_methods:
            char.msg = char_msg
        return returned_msg

    def loop_tests(self, cmds=None):
        """
            Loop through a premade dictionary running unit test on data within.

            Arguments:
                cmds=dict(), a dictionary of data to test.
                    Keys:
                        'arg': command arguments to pass to call_multi_receivers
                        'receivers': receivers dictionary to pass to call_multi_receivers
                        'post_reg_tests': a tuple of strings to run regex tests on.
                            These are ran on the returned string from call_multi_receivers

            Example:
                Take from commands.test.TestCommands.test_unarmed
                punch_rc = {self.char1: "You will be busy for 3 seconds.|Facing Char2 Char pulls theirs hand back preparing an attack.",
                           self.char2: "Facing Char2 Char pulls theirs hand back preparing an attack.",
                           self.obj1: "Facing Char2 Char pulls theirs hand back preparing an attack.|Char punches at Char2 with their fist and connects. Hitting Char2's "}
                punch_post = ("punch \d+ VS evade \d+: You punch at Char2 with your fist and connect\. Hitting Char2's ",
                             "Dealing \d+ damage\.|You are no longer busy\.",
                             # defenders messages
                             "evade \d+ VS punch \d+: Char punches at you with their fist and connects. Hitting your ",
                             "You take \d+ damage\.",
                             # location messages
                             "Hitting Char2's \w+\s*\w*\.")
                punch_cmd = {
                            'arg': f"= punch Char2 unit_test_succ, complete_cmd_early",
                            'receivers': punch_rc,
                            'post_reg_tests': punch_post
                           }
                # test a punch that misses
                punch_miss_rc = {self.char1: "You will be busy for 3 seconds.|Facing Char2 Char pulls theirs hand back preparing an attack.",
                           self.char2: "Facing Char2 Char pulls theirs hand back preparing an attack.",
                           self.obj1: "Facing Char2 Char pulls theirs hand back preparing an attack.|Char punches at Char2 with their fist and misses."}
                punch_miss_post = ("punch \d+ VS evade \d+: You punch at Char2 with your fist but miss.",
                             "Dealing \d+ damage\.|You are no longer busy\.",
                             # defenders messages
                             "evade \d+ VS punch \d+: Char punches at you with their fist but you successfully evade the punch\.")
                punch_missed_cmd = {
                            'arg': f"= punch Char2 unit_test_fail, complete_cmd_early",
                            'receivers': punch_miss_rc,
                            'post_reg_tests': punch_miss_post
                           }
               # run the test
               self.loop_tests((punch_cmd, punch_missed_cmd))

           Raises:
               AssertionError, if a unit test failed.
        """
        command = developer_cmds.CmdMultiCmd
        for cmd in cmds:
            caller = cmd.get('caller', self.char1)
            cmd_result = self.call_multi_receivers(command(), cmd['arg'], cmd['receivers'], caller=caller)
            post_tests = cmd.get('post_reg_tests', tuple())
            for post_test in post_tests:
                try:
                    self.assertRegex(cmd_result, post_test)
                # clean up the asserion message
                except AssertionError:
                    msg = f"\nNo regex match for pattern:\n{post_test}\nIn " \
                          f"string: \n{cmd_result}"
                    raise AssertionError(msg)
