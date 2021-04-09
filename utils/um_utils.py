"""
This module contains misc small functions
"""
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


def replace_cap(msg, switch, rep_txt, upper=False, lower=False, allow_upper=False):
    """
    Replace a sequence of characters in a string with another.
    Automatically capitalizing the first letter of the replacement
    string if it is the first word in a sentence.

    Arguments:
        msg: string, a message to capitalize at the start of the string
            and the start of each sentence.
        switch: string, the switch to replace
            example: "/target", "/Target", "/me", "/Me"
        rep_txt: string, replacement text, to replace the switch with.
        upper=False: bool, all replacements start with a upper case
        lower=False: bool, all replacements start with a lower case
        allow_upper: bool, allows replacement in middle of sentence to be upper
            This only occurs if the rep_txt starts with an upper case character

    Returns:
        string, with proper capitalization for sentences.

    Unit Tests:
        commands.tests.TestCommands.test_um_emote
    """
    msg = msg.strip()
    if switch not in msg:
        return msg
    if upper:
        return msg.replace(switch, rep_txt[0].upper() + rep_txt[1:])
    if lower:
        return msg.replace(switch, rep_txt[0].lower() + rep_txt[1:])
    if switch[1].isupper():
        return msg.replace(switch, rep_txt[0].upper() + rep_txt[1:])
    else:
        if allow_upper:
            return msg.replace(switch, rep_txt[0] + rep_txt[1:])
        else:
            return msg.replace(switch, rep_txt[0].lower() + rep_txt[1:])
    return msg

def support_upper(name, obj):
    """intended to be used with um_emote"""
    allow_upper = False
    if hasattr(obj, 'sdesc'):
        sdesc = obj.sdesc.get()
    else:
        sdesc = obj.key
    if name.startswith(sdesc):
        name = name.lower()
    else:
        allow_upper = True
    return name, allow_upper

def um_emote(emote, sender, receivers=None, target=None, anonymous_add=None):
    """
    Distribute an emote.

    Arguments:
        emote (str): The raw emote string as input by emoter.
        sender (Object): The one sending the emote.
        receivers (iterable): Receivers of the emote. These
            will also form the basis for which sdescs are
            'valid' to use in the emote.
        target (iterable): objects to replace /target switch with.
        anonymous_add (str or None, optional): If `sender` is not
            self-referencing in the emote, this will auto-add
            `sender`'s data to the emote. Possible values are
            - None: No auto-add at anonymous emote
            - 'last': Add sender to the end of emote as [sender]
            - 'first': Prepend sender to start of emote.

    Example:
        "/Me punches at /target "
        from a by stander: "A tall man punches at a short name "
        from the target of the attach: "A tall man punches at you "
        from the sender (or command caller) "You punches at a short man "
            Normally the command caller and target get custom messages.

    Notes:
        All standard evennia switches are supported.
        /me will be replaced with "you" for the sender.
        /target will be replaced with the display name of the target.
            From the receivers recog attribute for the target.
            For example if they recog a friend with a proper name.
        Capitalization of /Me or /Target results in the name being upper cased.
            This does NOT work as string.capitalize(), ONLY the first character
            is adjusted. Meaning following character's in the string can be
            upper cased.
            Example: /Target may be replaced with "A big fish flops"
                     where /target would show "a big fish flops"
        If a receiver has a recog for a /target or /me entry, it will have the
            potential of being upper case. This allows for players to recog
            with proper names.

    Unit Tests:
        commands.tests.TestCommands.test_um_emote

    # change color codes in object.process_sdesc
    """
    if not receivers:
        receivers = sender.location.contents
    else:
        receivers = utils.make_iter(receivers)
    sender_emote = False
    # If me is in msg, create custom message for sender
    if '/me' in emote.lower():
        if sender in receivers:
            sender_emote = emote
            if '/Me' in sender_emote:
                sender_emote = replace_cap(sender_emote, '/Me', 'you')
            if '/me' in sender_emote:
                sender_emote = replace_cap(sender_emote, '/me', 'you')
    if '/target' in emote.lower():
        if target:
            if utils.is_iter(target):  # target is multiple targets
                # send a message to each target
                for receiver in target:
                    if receiver in receivers:  # process message only if needed
                        if receiver == sender and sender_emote:
                            rec_emote = sender_emote
                            # sender's emote will send with target's emotes
                            sender_emote = False
                        else:
                            rec_emote = emote
                        # remove target receiving emote from name replacement
                        targets = list(target)
                        targets.remove(receiver)
                        # Capitalized recog support
                        allow_upper = False
                        # create a list of recog names
                        target_names = list()
                        for other_targ in targets:
                            ot_targ_name = other_targ.get_display_name(receiver)
                            # if the receiver has a custom recog for the receiver
                            # do not force it to be lower cased
                            ot_targ_name, allow_upper = support_upper(ot_targ_name, other_targ)
                            target_names.append(ot_targ_name)
                        # turn names list into a string
                        target_names = utils.iter_to_string(target_names, endsep="")
                        target_names += " and you"
                        # replace target switches with target names string
                        rec_emote = replace_cap(rec_emote, '/target', target_names, allow_upper=allow_upper)
                        rec_emote = replace_cap(rec_emote, '/Target', target_names)
                        # replace /me with senders display name
                        sender_name = sender.get_display_name(receiver)
                        sender_name, allow_upper = support_upper(sender_name, sender)
                        rec_emote = replace_cap(rec_emote, '/me', sender_name, allow_upper=allow_upper)
                        rec_emote = replace_cap(rec_emote, '/Me', sender_name)
                        # this target receives a custom emote, remove from standard
                        receivers.remove(receiver)
                        # send the emote to the target
                        rpsystem.send_emote(sender, (receiver,), rec_emote, anonymous_add)
            else:  # if the command has a single target
                if target in receivers: # process message only if needed
                    if target == sender and sender_emote:
                        target_emote = sender_emote
                        # sender's emote will send with target's emotes
                        sender_emote = False
                    else:
                        target_emote = emote
                    # make target's emote replacing /target's with 'your'
                    target_emote = replace_cap(target_emote, "/target's", 'your')
                    target_emote = replace_cap(target_emote, "/Target's", 'your')
                    # make target's emote replacing /target with 'you'
                    target_emote = replace_cap(target_emote, '/target', 'you')
                    target_emote = replace_cap(target_emote, '/Target', 'you')
                    # replace /me with senders display name
                    sender_name = sender.get_display_name(target)
                    sender_name, allow_upper = support_upper(sender_name, sender)
                    target_emote = replace_cap(target_emote, '/me', sender_name, allow_upper=allow_upper)
                    target_emote = replace_cap(target_emote, '/Me', sender_name)
                    # this target receives a custom emote, remove from standard
                    receivers.remove(target)
                    # send the emote to the target
                    rpsystem.send_emote(sender, (target,), target_emote, anonymous_add)
    # process message for receivers
    for receiver in receivers:
        if receiver == sender and sender_emote:
            rec_emote = sender_emote
            # sender's emote will send with target's emotes
            sender_emote = False
        else:
            rec_emote = emote
        if '/target' in rec_emote.lower():
            if target:
                if utils.is_iter(target):  # target is multiple targets
                    allow_upper = False  # Capitalized recog support
                    # create a list of recog names
                    target_names = list()
                    for targ in target:  # get recieivers recog of the target
                        targ_name = targ.get_display_name(receiver)
                        # if the receiver has a custom recog for the receiver
                        # do not force it to be lower cased
                        targ_name, upper = support_upper(targ_name, targ)
                        if upper:
                            allow_upper = True
                        target_names.append(targ_name)
                    # turn names list into a string
                    target_names = utils.iter_to_string(target_names, endsep="and")
                    # replace target switches with target names string
                    rec_emote = replace_cap(rec_emote, '/target', target_names, allow_upper=allow_upper)
                    rec_emote = replace_cap(rec_emote, '/Target', target_names)
                else:  # only a single target
                    targ_name = target.get_display_name(receiver)
                    targ_name, allow_upper = support_upper(targ_name, target)
                    # replace /target with the receivers recog for target
                    rec_emote = replace_cap(rec_emote, '/target', targ_name, allow_upper=allow_upper)
                    rec_emote = replace_cap(rec_emote, '/Target', targ_name)
            else:  # there is no target but is in the switch.
                rec_emote = rec_emote.replace("/target", "|rnothing|n")
                rec_emote = rec_emote.replace("/Target", "|rnothing|n")
            # replace /me with senders display name
            sender_name = sender.get_display_name(receiver)
            sender_name, allow_upper = support_upper(sender_name, sender)
            rec_emote = replace_cap(rec_emote, '/me', sender_name, allow_upper=allow_upper)
            rec_emote = replace_cap(rec_emote, '/Me', sender_name)
        # send the emote to the receiver
        rpsystem.send_emote(sender, (receiver,), rec_emote, anonymous_add)
