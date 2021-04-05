"""
This module contains misc small functions
"""
import re

from evennia.utils.logger import log_err
from evennia.utils import utils
from evennia.contrib import rpsystem


def string_to_data(value=None):
    """
    Converts a string to a variable data type.
    White spaces on end of strings are always stripped.
    strings:
        'None' become None
        'False' becomes False
        'True' becomes True
        int becomes an intigers

    Arguments:
        value, a string to convert

    Returns:
        value, a data version of the string passed.
        If the string could not be converted to a data type the string is returned.

    Raises:
        ValueError, if the argument was not passed or is None.
            Not the string 'None' but the data variable None
    """
    if value is None:
        raise ValueError("utils.um_utils.string_to_data, argument 1 must be passed and can " \
                         "not equal None. Not the string 'None' but the data variable None.")
    try:
        # if the string can become an inteiger make it one
        value = int(value)
    except ValueError:
        # convert the string to a data type
        value = value.strip()
        if value == 'None':
            value = None
        elif value == 'False':
            value = False
        elif value == 'True':
            value = True
    return value


def highlighter(message, highlight_color=None, **kwargs):
    """
    Assists with complex text highlighting.

    Arguments:
        positional
        message=str, the string to be highlighted.
            Required
        highlight_color=None, the background color for the text

        kwargs, key word arguments:
        color=None, the color the text should be.
            Colors are in Evennia color tags format.
            r for red, R for dark red so on.
        click=False, if the string is clickable.
            if no other settings are provided, run the message as a command.
        click_cmd=None, a string command to run when message is clicked.
            If this argument is used, click is ignored.
        up=False, if the first letter should be capitalized

    Usage:
        Examples taken from this functions unit test.
        # test color change
        test_message = um_utils.highlighter('test', 'r')
        test_message == "|[rtest|n"
        # test a text color change
        test_message = um_utils.highlighter('test', color='r')
        test_message == "|rtest|n"
        # test click kwarg
        test_message = um_utils.highlighter('test', click=True)
        test_message == "|lctest|lttest|le|n"
        # test a custom click command
        test_message = um_utils.highlighter('test', click_cmd="click me")
        test_message == "|lcclick me|lttest|le|n"
        # test the up kwarg
        test_message = um_utils.highlighter('test', up=True)
        test_message == "Test|n"
    """
    if highlight_color:
        message = f"|[{highlight_color}{message}"
    if 'color' in kwargs:
        color = kwargs.get('color')
        message = f"|{color}{message}"
    if 'up' in kwargs:
        message = message.capitalize()
    # apply a click method if one was passed
    if 'click_cmd' in kwargs:
        click_cmd = kwargs.get('click_cmd')
        message = f"|lc{click_cmd}|lt{message}|le"
    elif 'click' in kwargs:
        message = f"|lc{message}|lt{message}|le"
    return message + "|n"


def error_report(error_message, char=None):
    """
    Handle messaging errors to system.

    Arguments:
        error_message, string, message to present to the log, and user.
        char=None, the Character instance. Only used for messaging the player

    Returns:
        The message showed to the user, or the message recieved if the Character has no account attached.
        These returns are intended for easy unit testing. Not for actual usage.
    """

    if char:
        perm_str = ""  # default permision string, incase the account is missions the permissions class
        if hasattr(char, 'account'):  # if there is an account attached to the Character
            if hasattr(char.account, 'permissions'):
                perm_str = str(char.account.permissions)  # get premissions in string form
            if 'developer' in perm_str:  # if the user is a developer
                dev_msg = f"|RError message:|n {error_message}|/This has |RNOT|n been logged. System detects you are a developer."
                char.msg(dev_msg)
                return_msg = dev_msg
            else:
                log_err(error_message)
                char_msg = "An error was found and has been logged. It is recommended you report this error. To do so please press "
                click_cmd = f"report error = {error_message}"
                report_cmd = highlighter("Report Error", highlight_color='R', click_cmd=click_cmd)
                char_msg = f"{char_msg}{report_cmd}."
                char.msg(char_msg)
                return_msg = char_msg
        else:  # Character has no account attached, just log message
            log_err(error_message)
            return_msg = error_message
    else:  # if no Character instance provided
        log_err(error_message)
        return_msg = error_message
    return return_msg


def objs_sdesc_str(objects, you_object=None):
    """
    Turn a list of objects into a description string with commas.

    Arguments:
        Objects list(), a list of objects you would like their.
        you_object=None, an object that "you" will be returned instead of the objects description.

    Returns:
        A string containing the usdesc of the objects.
        Example:
            "object 1, object 2 and object 3"

    Usage:
        If within a command.
            target_names = objs_sdesc_str(self.targets)
                returns a string of short descriptions of the commands targets
                Example: "target 1, target 2 and target 3"
            target_names = objs_sdesc_str(self.targets, receiver)
                returns a string of short descriptions of the commands targets
                Where the receivers description is ommited than " and you", is added to the end.
                Example: "target 1, target 2 and you"
    """
    if hasattr(objects, '__iter__'):
        if you_object:
            names_list = list()
            for object in objects:
                if object != you_object:
                    names_list.append(object.usdesc)
            object_names = ', '.join(names_list)
            object_names += " and you"
            return object_names
        else:
            names_list = list()
            for object in objects[:-1]:
                names_list.append(object.usdesc)
            objects_names = ', '.join(names_list)
            objects_names += f" and {objects[-1].usdesc}"
            return objects_names
    else:
        return ""


def replace_cap(msg, switch, rep_txt, upper=False, lower=False):
    """
    Replace a sequence of characters in a string with another.
    Automatically capitalizing the first letter of the replacement
    string if it is the first word in a sentence.

    Arguments:
        msg: string, a message to capitalize at the start of the string
            and the start of each sentence.
        switch: string, the switch to replace
            example: "/target"
        rep_txt: string, replacement text, to replace the switch with.
        upper=False: bool, all replacements start with a upper case
        lower=False: bool, all replacements start with a lower case

    Returns:
        string, with proper capitalization for sentences.

    Unit tests:
        commands.test.TestCommands.test_emote
    """
    msg = msg.strip()
    if upper:
        return msg.replace(switch, rep_txt[0].upper() + rep_txt[1:])
    if lower:
        return msg.replace(switch, rep_txt[0].lower() + rep_txt[1:])
    # Replace the swtiches with standard sentence capitalization.
    for pattern in ("(?:^|(?:[.!?]\s))\|*\S*", "(?:[.!?]\|+\S+\s)\|*\S*"):
        pat_match = re.search(pattern + switch, msg)
        if pat_match:
            pat_matches = pat_match.groups()
            if not pat_matches:
                pat_matches = pat_match.group(0)
                pat_matches = (pat_matches,)
            for match in pat_matches:
                rep_match = match.replace(switch, rep_txt[0].upper() + rep_txt[1:])
                msg = msg.replace(match, rep_match)
    # replace all other switches
    if switch in msg:
        msg = msg.replace(switch, rep_txt)
    return msg


def um_emote(emote, sender, receivers=None, target=None, anonymous_add=None):
    """
    Distribute an emote.

    Arguments:
        sender (Object): The one sending the emote.
        receivers (iterable): Receivers of the emote. These
            will also form the basis for which sdescs are
            'valid' to use in the emote.
        emote (str): The raw emote string as input by emoter.
        anonymous_add (str or None, optional): If `sender` is not
            self-referencing in the emote, this will auto-add
            `sender`'s data to the emote. Possible values are
            - None: No auto-add at anonymous emote
            - 'last': Add sender to the end of emote as [sender]
            - 'first': Prepend sender to start of emote.

    # change color codes in object.process_sdesc
    """
    if not receivers:
        receivers = sender.location.contents
    sender_emote = False
    target_emote = False
    if '/me' in emote:  # replace me for sender
        if sender in receivers:
            receivers.remove(sender)
            sender_emote = replace_cap(emote, '/me', 'you')
            if '/target' in emote:
                if target:
                    if utils.is_iter(target):  # target is multiple targets
                        target_names = list()
                        for targ in target:  # get recieivers recog of the target
                            target_names.append(targ.get_display_name(sender).lower())
                        target_names = utils.iter_to_string(target_names, endsep="and")
                        sender_emote = replace_cap(sender_emote, '/target', target_names)
                else:
                    targ_name = target.get_display_name(sender).lower()
                    # replace /target with target's name from sender's view
                    sender_emote = replace_cap(sender_emote, '/target', targ_name)
            # send the emote
            rpsystem.send_emote(sender, (sender,), sender_emote, anonymous_add)
    if '/target' in emote:
        if target:
            if utils.is_iter(target):  # target is multiple targets
                # send a message to each target
                for targ in target:
                    if targ in receivers:  # process message only if needed
                        # remove target receiving emote from name replacement
                        targets = list(target)
                        targets.remove(targ)
                        # replace /target with all other command targets recog
                        target_names = list()
                        for other_targ in targets:
                            target_names.append(other_targ.get_display_name(targ).lower())
                        target_names = utils.iter_to_string(target_names, endsep="")
                        target_names += " and you"
                        target_emote = replace_cap(emote, '/target', target_names)
                        receivers.remove(targ)  # targ receives emote here
                        rpsystem.send_emote(sender, (targ,), target_emote, anonymous_add)
            else:  # if the command has a single target
                if target in receivers: # process message only if needed
                    # make target's emote replacing /target with 'you'
                    target_emote = replace_cap(emote, '/target', 'you')
                    receivers.remove(target)  # target will receive it's own emote
                    rpsystem.send_emote(sender, (target,), target_emote, anonymous_add)
    for receiver in receivers:  # process receivers separately
        rec_emote = emote
        # replace /target with target's name from receiver's recog fields
        if '/target' in emote:
            if target:
                if utils.is_iter(target):  # target is multiple targets
                    target_names = list()
                    for targ in target:  # get recieivers recog of the target
                        target_names.append(targ.get_display_name(receiver).lower())
                    target_names = utils.iter_to_string(target_names, endsep="and")
                    rec_emote = replace_cap(emote, '/target', target_names)
                else:  # only a single target
                    targ_name = target.get_display_name(receiver).lower()
                    rec_emote = replace_cap(emote, '/target', targ_name)
            else:
                rec_emote = rec_emote.replace("/target", "|rnothing|n")
        rpsystem.send_emote(sender, (receiver,), rec_emote, anonymous_add)
