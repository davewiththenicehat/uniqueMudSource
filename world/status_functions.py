import time
import weakref
from evennia import utils


STATUS_TYPES = ('stunned', 'busy')

"""
Only one instance of a status_type can exist at a time on a Character.
Only ONE command can be deffered at a time.
    Even if you attempt to defer a second command under a different status type

Attributes:
Character.db.f'{status_type}', a float or int of the time the status will end.
Character.ndb.deffered_command, weakref.proxy instance of a Command to defer.
Character.f'{status_type}_status', instance of a utils.delay
    stores the stop function and time it will run. Automatically calls it.
    Supports canceling.
Character.nbd.cmd_stop_request, an serialized instance of status_user_request_stop
    passed to utils.evmenu.get_input when asking a player if they would like to
    stop their current command.

Unit testing for these functions is done in the commands unit test.
"""


def status_delay_set(target, cmd, delay_time, status_type):
    """
    INTERNAL COMMAND, not intended for general developers.

    defers or delays the action portion of a command
    Returns True if a command was successfully deffered.

    References:
    https://github.com/evennia/evennia/wiki/Coding-Utils#utilsdelay
        Much of utilsdelay is poorly documented.
        utilsdelay is an instance of evennia.scripts.TaskHandler
        TaskHandler returns a twisted Deffered object
        https://twistedmatrix.com/documents/13.0.0/api/twisted.internet.defer.Deferred.html
    """
    # create an Character.int attribute with the completion time
    target.attributes.add(status_type, time.time() + delay_time)
    if cmd:
        # only create a command if one is currently not deffered
        if not target.nattributes.has('deffered_command'):
            # created a reference of the command that is being deffered
            target.nattributes.add('deffered_command', weakref.proxy(cmd))
    # Return correct plural on seconds
    plural_sec = 's' if delay_time > 1.99 else ''
    target.msg(f'You will be {status_type} for {round(delay_time)} second{plural_sec}.')
    if status_type != 'stunned':
        target.nattributes.add(f'{status_type}_status', utils.delay(delay_time, status_delay_stop, target, status_type, True, persistent=True))
    else:
        target.nattributes.add(f'{status_type}_status', utils.delay(delay_time, status_delay_stop, target, status_type, False, persistent=True))
    return True  # tell target the command was deffered succesfully


def status_delay_get(target, status_type='busy'):
    """
    INTERNAL COMMAND, not intended for general developers.

    Checks if a deferal or delay type is on a character.

    Returns 0 if there is no delay, returns a float of the difference if there is.
    """
    if target.attributes.has(status_type):
        current_time = time.time()
        if current_time > target.attributes.get(status_type):
            target.attributes.remove(status_type)
            return 0
        else:
            return target.attributes.get(status_type) - current_time
    else:
        return 0


def status_delay_stop(target, status_type, complete_cmd):
    """
    INTERNAL COMMAND, not intended for general developers.

    stop utils.delay called from status_delay_set
    Returns True when the status was stopped successfully

    Reference:
    https://twistedmatrix.com/documents/13.0.0/api/twisted.internet.defer.Deferred.html#cancel
    https://github.com/evennia/evennia/wiki/Coding-Utils#utilsdelay
    Much of utilsdelay is poorly documented.
    utilsdelay is an instance of evennia.scripts.TaskHandler
        note the use of delay_status_inst.remove()
        it is used to remove the instance of utilsdelay
        This is a TaskHandler method
    """
    # stop the function if there is no status of this type on the Character
    if not target.nattributes.has(f'{status_type}_status'):
        return False
    delay_status_inst = target.nattributes.get(f'{status_type}_status')
    if delay_status_inst:
        # remove tmp attributes order of removal matters
        try:
            target.nattributes.remove('cmd_stop_request')
        except AttributeError:
            pass
        try:
            # If the deffered command was not called by the twisted deferred instance cancel it
            if not delay_status_inst.called:
                delay_status_inst.pause()  # tricks cancel into not shooting an error
                delay_status_inst.cancel()
                delay_status_inst.remove()
        except AttributeError:
            pass
        # remove commands waiting for user imput
        # utils.evmenu.get_input adds cmdset InputCmdSet which adds InputCmdSet
        target.cmdset.remove(utils.evmenu.InputCmdSet)
        target.cmdset.remove(utils.evmenu.CmdGetInput)
        # run the deffered command if it is not being cancelled
        if complete_cmd:
            target.ndb.deffered_command.deferred_action()
        # remove tmp attributes order of removal matters
        try:
            target.attributes.remove(status_type)  # remove time tracking attr
        except AttributeError:
            pass
        try:
            target.nattributes.remove('deffered_command')
        except AttributeError:
            pass
        try:
            target.nattributes.remove(f'{status_type}_status')
        except AttributeError:
            pass
        target.msg(f"You are no longer {status_type}.")
        return True


def status_user_request_stop(target, prompt, result, *args, **kwargs):
    """
    Request a player if they would like to cancel a command.
    Allows for a custom prompt to be sent to do this.
    Allows for a command to be automatically executed when done.

    Reason:
        To allow commands to be canceled and automatically followed up with a new one.

    Reference:
        utils.evmenu.get_input adds cmdset InputCmdSet which adds InputCmdSet
        These are removed in this function to return proper command input.
    """
    #
    if result.lower() in ("y", "yes", "i", "ignore"):
        if result.lower() in ("y", "yes"):
            # stop the command waiting to be run
            status_delay_stop(target, 'busy', False)
            # any arguments received should be stop commands, run them now
            for cmd in args:
                if isinstance(cmd, str):
                    target.execute_cmd(cmd)
    else:
        # remove commands waiting for user imput
        target.cmdset.remove(utils.evmenu.InputCmdSet)
        target.cmdset.remove(utils.evmenu.CmdGetInput)
        # run the none get_input command
        target.execute_cmd(result)
        # listen for the get_input command again
        target.cmdset.add(utils.evmenu.InputCmdSet)
        # Ask again after completing the none get_input cmd for a command
        target.msg(f"|/{prompt}")
        # returning True will make sure the prompt state is not exited
        return True


def status_force_stop(target, stop_message=None, stop_cmd=None, status_type='busy', stopper=None):
    """
    INTERNAL COMMAND, not intended for general developers.

    Forcibily stop a status
    Returns True if the status was stopped, false if it was not.

    Supports (Optional):
        sending a message to the target
        running a command after stopping the status
    """
    # stop the status and any commands waiting to run
    stop_success = status_delay_stop(target, status_type, False)
    # only do rest if there was a command to stop.
    if stop_success:
        if stop_message:
            target.emote(stop_message, target, stopper)
        if stop_cmd:
            if isinstance(stop_cmd, str):
                target.execute_cmd(stop_cmd)
    return stop_success
