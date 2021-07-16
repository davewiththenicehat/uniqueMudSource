"""
Adds a dictionary f'status_type', to a Character, as an nattribute.

Only one instance of a status_type can exist at a time on a Character.

status_type = {
                'task': task  # utils.delay returned task
                'cmd': cmd  # a weakref of a command.
                'comp_time': time  # time.time() + delay_time
}

The 'stunned' status is a persistent task. Making certain stuns end after a server restart.
All other status types do not survive a restart.

status_user_request_stop adds attribute Character.nbd.cmd_stop_request
    A serialized instance of status_user_request_stop. It is passed to utils.evmenu.get_input when
    asking a player if they would like to stop their current command.

Unit testing for these functions is done in the commands unit test.
"""

import time
import weakref
from evennia import utils


STATUS_TYPES = ('stunned', 'busy')


def status_delay_set(char, cmd=None, delay_time=3, status_type='busy'):
    """Create a status that will automatically complete, possibly with an action.

    Arguments:
        char (Character): The Character to attach this status to.
        cmd (Command): A Command to call at the completion of this status.
        delay_time (int): Number of seconds to wait before completing this status.
        status_type (str): The type of status to create.

    Returns:
        success (bool): if the status was successfully created.

    """

    # create a status dictionary.
    status = {}

    # Record the completion time for this status
    status['comp_time'] = status_type, time.time() + delay_time

    # record the command (if any) for this status
    status['cmd'] = cmd

    # create the task for this status
    if status_type == 'stunned':  # stunned status are persistent tasks
        task = utils.delay(delay_time, complete, char, status_type, False)
    else:
        task = utils.delay(delay_time, complete, char, status_type, True)

    # record the task
    status['task'] = task

    # save the status as a Character attribute
    char.nattributes.set(f'{status_type}', status)

    # message the the char of the status creation
    plural_sec = 's' if delay_time > 1.99 else ''
    char.msg(f'You will be {status_type} for {round(delay_time)} second{plural_sec}.')

    return True  # tell char the command was deferred succesfully


def get_status(char, status_type='busy'):
    """Get an instance of a status.

    Attributes:
        char (Character): The Character to attach this status to.
        status_type (str): The type of status to get.

    returns:
        status (dict): An instance of the Character's status dictionary or an empty dictionary if
            no status of the type passed exists on this Character.
    """
    status = char.nattributes.get(status_type, False)
    if status:
        return status
    else:
        return {}


def status_delay_get(char, status_type='busy'):
    """Get the delay remaining on a status, or 0 if there is no status of the type passed.

    Attributes:
        char (Character): The Character to attach this status to.
        status_type (str): The type of status to get.

    returns:
        time_remaining (float): The time remaining before status completion. 0 is returned if there
            is no status, or if there is no time remaining on the status.
    """
    status = char.nattributes.get(status_type, False)
    if status:
        current_time = time.time()
        status_comp_time = status['comp_time']
        if current_time > status_comp_time:
            char.nattributes.remove(status_type)
            return 0
        else:
            return status_comp_time - current_time
    else:
        return 0


def complete(char, status_type='busy', complete_cmd=True):
    """Complete the deferred status.

    Arguments:
        char (Character): The Character to attach this status to.
        status_type (str): The type of status to get. Default is 'busy'.
        complete_cmd (bool): Should the command the status refers to be called?

    Returns:
        success (bool): The completion was successful

    """

    # get the status
    status = char.nattributes.get(f'{status_type}')

    # stop the function if there is no status of this type on the Character
    if not status:
        return False

    # get the status' task
    task = status['task']

    if task:

        # remove tmp attributes order of removal matters
        if char.nattributes.has('cmd_stop_request'):
            char.nattributes.remove('cmd_stop_request')

        # If the task was not called by the twisted deferred instance cancel it
        if not task.called:
            task.cancel()

        # remove commands waiting for user imput
        # utils.evmenu.get_input adds cmdset InputCmdSet which adds InputCmdSet
        char.cmdset.remove(utils.evmenu.InputCmdSet)
        char.cmdset.remove(utils.evmenu.CmdGetInput)

        # collect an instance of the command
        cmd = status['cmd']

        # run the deferred command if specified
        if complete_cmd and cmd:
            # check all command requirements
            if cmd.requirements(basic=True, custom=True, target=True):
                cmd_successful = cmd.deferred_action()  # run the action
                # Run command completion tasks. Evasion cmds do this in actions.evade_roll
                if cmd.cmd_type != 'evasion' and cmd_successful:
                    cmd.def_act_comp()

        # remove the deferred task
        task.remove()

        # reset the command instance
        if cmd:
            cmd.set_instance_attributes()

        # remove the status
        char.nattributes.remove(status_type)

        # message the Character.
        char.msg(f"You are no longer {status_type}.")

        return True


def status_user_request_stop(char, prompt, result, *args, **kwargs):
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
            complete(char, 'busy', False)
            # any arguments received should be stop commands, run them now
            for cmd in args:
                if isinstance(cmd, str):
                    char.execute_cmd(cmd)
    else:
        # remove commands waiting for user imput
        char.cmdset.remove(utils.evmenu.InputCmdSet)
        char.cmdset.remove(utils.evmenu.CmdGetInput)
        # run the none get_input command
        char.execute_cmd(result)
        # listen for the get_input command again
        char.cmdset.add(utils.evmenu.InputCmdSet)
        # Ask again after completing the none get_input cmd for a command
        char.msg(f"|/{prompt}")
        # returning True will make sure the prompt state is not exited
        return True


def status_force_stop(char, stop_message=None, stop_cmd=None, status_type='busy', stopper=None):
    """
    INTERNAL COMMAND, not intended for general developers.

    Forcibily stop a status
    Returns True if the status was stopped, false if it was not.

    Supports (Optional):
        sending a message to the char
        running a command after stopping the status
    """
    # stop the status and any commands waiting to run
    stop_success = complete(char, status_type, False)
    # only do rest if there was a command to stop.
    if stop_success:
        if stop_message:
            char.emote(stop_message, char, stopper)
        if stop_cmd:
            if isinstance(stop_cmd, str):
                char.execute_cmd(stop_cmd)
    return stop_success
