"""
This module contains misc small functions
"""

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
    """
    if highlight_color:
        message = f"|{highlight_color}{message}"
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
