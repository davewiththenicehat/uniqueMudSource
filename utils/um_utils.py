"""
This module contains misc small functions
"""
import string

from evennia.utils.logger import log_info, log_warn, log_err

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
    if value == None:
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


def cap_msg(msg):
    """
    Capitalize the first word of a message, as well as the first word of each
    sentence within the message.

    Arguments:
        msg: string, a message to capitalize at the start of the string
            and the start of each sentence.

    Returns:
        string, with proper capitalization for sentences.
    """
    for punc in '.?!':
        punc += ' '
        if punc in msg:
            sentences = msg.split(punc)
            # Normally the last punctuation will not have a space after it.
            # use construction to detect first run. Otherwise the punc string
            # would get added to the end of the construction. Resulting in
            # double punctuation.
            construction = False
            # in reverse to easily sort last sentence
            for sentence in reversed(sentences):
                if construction:
                    construction = sentence.capitalize() + punc + construction
                else:
                    construction = sentence.capitalize()
            msg = construction
    return msg
