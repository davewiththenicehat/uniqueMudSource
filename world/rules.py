"""
Created following:
https://github.com/evennia/evennia/wiki/Implementing-a-game-rule-system
"""

from random import randint
import time, re
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
        if character.db.is_monster:
            character.location.msg_contents(f"The {character.name} dies.")
            character.delete()


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
