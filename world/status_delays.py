"""
Created following
https://github.com/evennia/evennia/wiki/Command-Duration
utils.delay appears to be superior than threading.timer
utils.delay as the ability to persist after reboot.
utils.delay as a cancel method
"""


import time
from evennia import utils


def set_cool_down(caller, cool_down):
    """
    Locks commands that requiring a cooldown time
    caller is the character who is having the cooldown time set
    cool_down is the time in seconds for the cooldown.
    """
    caller.db.cool_down = time.time() + cool_down
    caller.msg(f"You will be busy for {cool_down} seconds.")
    # https://github.com/evennia/evennia/wiki/Coding-Utils#utilsdelay
    utils.delay(cool_down, ready_msg, caller, persistent=True)
    # https://docs.python.org/3/library/threading.html#timer-objects
    # from threading import Timer
    # caller.ready_timer = Timer(cool_down, caller.ready_msg)
    # caller.ready_timer.start()


def get_cool_down(caller):
    """
    Returns 0 if there is no cooldown or the time for cooldown has passed
    """
    # if hasattr(caller.db, "cool_down"):
    if caller.attributes.has("cool_down"):
        current_time = time.time()
        if current_time > caller.db.cool_down:
            caller.attributes.remove("cool_down")
            return 0
        else:
            return caller.db.cool_down - current_time
    else:
        return 0


def set_stunned(caller, stun_time):
    """
    Locks commands that requiring a cooldown time
    caller is the character who is having the cooldown time set
    cool_down is the time in seconds for the cooldown.
    """
    caller.db.stunned = time.time() + stun_time
    caller.msg(f"|[rYou will be stunned for {stun_time} seconds.")
    # https://github.com/evennia/evennia/wiki/Coding-Utils#utilsdelay
    caller.ndb.stun_deffered = utils.delay(stun_time, stun_stop_msg, caller, persistent=True)
    # https://docs.python.org/3/library/threading.html#timer-objects
    # from threading import Timer
    # caller.db.stunned_timer = Timer(stun_down, caller.stun_stop_msg)
    # caller.db.stunned_timer.start()


def get_stunned(caller):
    """
    Returns 0 if there is no cooldown or the time for cooldown has passed
    """
    if caller.attributes.has("stunned"):
        current_time = time.time()
        if current_time > caller.db.stunned:
            caller.attributes.remove("stunned")
            return 0
        else:
            return caller.db.stunned - current_time
    else:
        return 0


def ready_msg(caller):
    caller.attributes.remove("cool_down")
    caller.msg("|YYou are no longer busy.")


def stun_stop_msg(caller):
    # if caller.attributes.has("stunned"):
    caller.attributes.remove("stunned")
    # remove commands waiting for user to  press yes to stop stun.
    # review utils.evmenu for reference
    # simply put
    caller.cmdset.remove(utils.evmenu.InputCmdSet)
    caller.cmdset.remove(utils.evmenu.CmdGetInput)
    # stop utils.delay called from set_stunned
    # https://github.com/evennia/evennia/wiki/Coding-Utils#utilsdelay
    caller.ndb.stun_deffered.cancel()
    caller.msg("|YYou are no longer stunned.")
