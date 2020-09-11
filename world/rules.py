"""
Created following:
https://github.com/evennia/evennia/wiki/Implementing-a-game-rule-system
"""

from random import randint
import time
from threading import Timer


def roll_hit():
    "Roll 1d100"
    return randint(1, 100)


def roll_dmg():
    "Roll 1d6"
    return randint(1, 6)


def check_defeat(character):
    "Checks if a character is 'defeated'."
    if character.db.HP <= 0:
        character.msg("You fall down, defeated!")
        character.db.HP = 100   # reset


def add_XP(character, amount):
    "Add XP to character, tracking level increases."
    if "training_dummy" in character.tags.all():  # don't allow the training dummy to level
        character.location.msg_contents("Training Dummies can not gain XP.")
        return
    else:
        character.db.XP += amount
        if character.db.XP >= (character.db.level + 1) ** 2:
            character.db.level += 1
            character.db.STR += 1
            character.db.combat += 2
            character.msg("|gYou are now level %i!" % character.db.level)


def skill_combat(*args):
    """
    This determines outcome of combat. The one who
    rolls under their combat skill AND higher than
    their opponent's roll hits.
    """
    char1, char2 = args
    roll1, roll2 = roll_hit(), roll_hit()
    failtext = "|RYou are hit by %s for %i damage!"
    wintext = "|YYou hit %s for %i damage!"
    xp_gain = randint(1, 3)

    # display messages showing attack numbers
    attack_message = f"|510{char1.name} rolls {roll1} + combat {char1.db.combat} " \
    f"= {char1.db.combat+roll1} | {char2.name} rolls {roll2} + combat " \
    f"{char2.db.combat} = {char2.db.combat+roll2}"
    char1.location.msg_contents(attack_message)
    attack_summary = f"|510{char1.name} {char1.db.combat+roll1} " \
    f"vs {char2.name} {char2.db.combat+roll2}"
    char1.location.msg_contents(attack_summary)

    if char1.db.combat+roll1 > char2.db.combat+roll2:
        # char 1 hits
        dmg = roll_dmg() + char1.db.STR
        char1.msg(wintext % (char2, dmg))
        add_XP(char1, xp_gain)
        char2.msg(failtext % (char1, dmg))
        char2.db.HP -= dmg
        check_defeat(char2)
    elif char2.db.combat+roll2 > char1.db.combat+roll1:
        # char 2 hits
        dmg = roll_dmg() + char2.db.STR
        char1.msg(failtext % (char2, dmg))
        char1.db.HP -= dmg
        check_defeat(char1)
        char2.msg(wintext % (char1, dmg))
        add_XP(char2, xp_gain)
    else:
        # a draw
        drawtext = "Neither of you can find an opening."
        char1.msg(drawtext)
        char2.msg(drawtext)


SKILLS = {"combat": skill_combat}


def roll_challenge(character1, character2, skillname):
    """
    Determine the outcome of a skill challenge between
    two characters based on the skillname given.
    """
    if skillname in SKILLS:
        SKILLS[skillname](character1, character2)
    else:
        raise RunTimeError("Skillname %s not found." % skillname)


def set_cool_down(caller, cool_down):
    """
    Locks commands that requiring a cooldown time
    self is the character who is having the cooldown time set
    cool_down is the time in seconds for the cooldown.
    """
    # https://docs.python.org/3/library/threading.html#timer-objects
    caller.cool_down = time.time() + cool_down
    caller.msg(f"You will be busy for {cool_down} seconds.")
    caller.ready_timer = Timer(cool_down, caller.ready_msg)
    caller.ready_timer.start()


def get_cool_down(caller):
    """
    Returns 0 if there is no cooldown or the time for cooldown has passed
    """
    # https://docs.python.org/3/library/threading.html#timer-objects
    if hasattr(caller, "cool_down"):
        current_time = time.time()
        if current_time > caller.cool_down:
            delattr(caller, "cool_down")
            return 0
        else:
            return caller.cool_down - current_time
    else:
        return 0


def set_stunned(caller, stun_time):
    """
    Locks commands that requiring a cooldown time
    self is the character who is having the cooldown time set
    cool_down is the time in seconds for the cooldown.
    """
    # https://docs.python.org/3/library/threading.html#timer-objects
    caller.stunned = time.time() + stun_time
    caller.msg(f"|[rYou will be stunned for {stun_time} seconds.")
    caller.stunned_timer = Timer(stun_time, caller.stun_stop_msg)
    caller.stunned_timer.start()


def get_stun(caller):
    """
    Returns 0 if there is no cooldown or the time for cooldown has passed
    """
    # https://docs.python.org/3/library/threading.html#timer-objects
    if hasattr(caller, "stunned"):
        current_time = time.time()
        if current_time > caller.stunned:
            delattr(caller, "stunned")
            return 0
        else:
            return caller.stunned - current_time
    else:
        return 0
