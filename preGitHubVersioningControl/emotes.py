#!/usr/bin/python
# -*- coding: utf-8 -*-
from evennia import Command as BaseCommand


class Command(BaseCommand):

    """
    Inherit from this if you want to create your own command styles
    from scratch.  Note that Evennia's default commands inherits from
    MuxCommand instead.

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_command(): If this returns True, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_command(): Extra actions, often things done after
            every command, like prompts.

    """

    def show_prompt(self, target):
        """
        This hook is called after the command has finished executing
        (after self.func()).
        """

        if float(target.db.health) / float(target.db.max_health) > 0.80:
            prompt_hp_color = '|g'
        elif float(target.db.health) / float(target.db.max_health) \
            > 0.36:
            prompt_hp_color = '|y'
        else:
            prompt_hp_color = '|r'

        if target.db.stamina > 6:
            prompt_stamina_color = '|g'
        elif target.db.stamina > 3:
            prompt_stamina_color = '|y'
        else:
            prompt_stamina_color = '|r'

        prompt = \
            '%sHealth|n: %s%s|n - |gMagic|n: |nAsleep|n - %sStamina|n: %s%s.' \
            % (
            prompt_hp_color,
            prompt_hp_color,
            target.db.health,
            prompt_stamina_color,
            prompt_stamina_color,
            target.db.stamina,
            )
        target.msg(prompt)

        # Not needed from the command's perspective.
        # if target.db.health != None:
        #    target.msg(prompt)

    pass


########################################################################
# WHN: Emotes start here.
########################################################################

class CmdAnger(Command):

    """
    An anger emote.

    Usage: 
      anger

    """

    key = 'anger'
    aliases = ['mad']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s looks mad. Really mad. You mad?' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You are looking really mad right now!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s looks really angry right now!' % caller.name
            target.msg(string)
            string = 'You catch yourself looking angrily at %s.' \
                % target.name
            caller.msg(string)
            string = '%s looks upset and angry with %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSmirk(Command):

    """
    A smirk emote.

    Usage: 
      smirk

    """

    key = 'smirk'
    aliases = ['wry']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s smirks wryly.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You smirk wryly.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s smirks wryly at you.' % caller.name
            target.msg(string)
            string = 'You smirk wryly at %s.' % target.name
            caller.msg(string)
            string = '%s smirks wryly at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdNod(Command):

    """
    A nod emote.

    Usage: 
      nod

    """

    key = 'nod'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s nods.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You nod your head.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gives you a nod of %s head.' % (caller.name,
                    caller.db.genderp)
            target.msg(string)
            string = 'You nod your head towards %s.' % target.name
            caller.msg(string)
            string = '%s gives a nod of %s head to %s.' % (caller.name,
                    caller.db.genderp, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdShake(Command):

    """
    A shake emote.

    Usage: 
      shake

    """

    key = 'shake'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s shakes %s head.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You shake your head.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s shakes %s head at you.' % (caller.name,
                    caller.db.genderp)
            target.msg(string)
            string = 'You shake your head at %s.' % target.name
            caller.msg(string)
            string = '%s shakes %s head at %s.' % (caller.name,
                    caller.db.genderp, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdHairTwirl(Command):

    """
    A hair twirling emote.

    Usage: 
      twirl

    """

    key = 'twirl'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s twirls their hair around a finger idly.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You twirl your hair idly around your finger.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s twirls their hair.' % caller.name
            target.msg(string)
            string = 'You twirl your hair at idly at %s.' % target.name
            caller.msg(string)
            string = '%s twirls %s hair idly at %s.' % (caller.name,
                    caller.db.genderp, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSalute(Command):

    """
    A salute emote.

    Usage: 
      salute

    """

    key = 'salute'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s stands at attention and gives a crisp salute.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You stand at attention and give a crisp salute.'
                       )
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = \
                '%s stands at attention and gives you a crisp salute.' \
                % caller.name
            target.msg(string)
            string = \
                'You stand at attention and give %s a crisp salute.' \
                % target.name
            caller.msg(string)
            string = \
                '%s stands at attention and gives %s a crisp salute.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWink(Command):

    """
    A wink emote.

    Usage: 
      wink

    """

    key = 'wink'
    aliases = ['winky']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s winks charmingly.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You wink a charming wink of winklyness.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s winks charmingly at you.' % caller.name
            target.msg(string)
            string = 'You wink charmingy at %s.' % target.name
            caller.msg(string)
            string = '%s winks charmingly at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdDance(Command):

    """
    A dance emote.

    Usage: 
      dance

    """

    key = 'dance'
    aliases = ['tango']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = \
                "%s dances the tango. Apparently it doesn't take two after all." \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You dance the tango -- alone. Skills!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s dances dramatically with you.' % caller.name
            target.msg(string)
            string = \
                'You dance the dance of love and suffering with %s.' \
                % target.name
            caller.msg(string)
            string = \
                '%s dances the dance of love and suffering with %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPat(Command):

    """
    A pat emote.

    Usage: 
      pat

    """

    key = 'pat'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s pats themselves on the back.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You pat yourself on the back. Good job!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s pats you on the back.' % caller.name
            target.msg(string)
            string = 'You pat %s on the back.' % target.name
            caller.msg(string)
            string = '%s pats %s on the back.' % (caller.name,
                    target.name)

            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWince(Command):

    """
    A wince emote.

    Usage: 
      wince

    """

    key = 'wince'

    # aliases = ["wince at"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s winces awkwardly.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You wince awkwardly.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s winces awkwardly at you.' % caller.name
            target.msg(string)
            string = 'You wince awkwardly at %s.' % target.name
            caller.msg(string)
            string = '%s winces awkwardly at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdApologize(Command):

    """
    An apologize emote.

    Usage: 
      apologize

    """

    key = 'apologize'

    # aliases = ["apologize to"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s formally apologizes.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You formally apologize.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s formally apologizes to you.' % caller.name
            target.msg(string)
            string = 'You formally apologize to %s.' % target.name
            caller.msg(string)
            string = '%s formally apologizes to %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdThank(Command):

    """
    A thank emote.

    Usage: 
      thank

    """

    key = 'thank'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s humbly thanks everyone.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You humbly thank everyone.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s humbly thanks you.' % caller.name
            target.msg(string)
            string = 'You humbly thank %s.' % target.name
            caller.msg(string)
            string = '%s humbly thanks %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdLaugh(Command):

    """
    A laugh emote.

    Usage: 
      laugh

    """

    key = 'laugh'
    aliases = ['lol']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s laughs out loud!' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You laugh out loud!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s laughs out loud at you!' % caller.name
            target.msg(string)
            string = 'You laugh out loud at %s.' % target.name
            caller.msg(string)
            string = '%s laughs out loud at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWave(Command):

    """
    A wave emote.

    Usage: 
      wave

    """

    key = 'wave'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s waves.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You wave.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s waves at you.' % caller.name
            target.msg(string)
            string = 'You wave at %s.' % target.name
            caller.msg(string)
            string = '%s waves at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCurtsey(Command):

    """
    A curtsey emote.

    Usage: 
      curtsey

    """

    key = 'curtsey'
    aliases = ['curtsy']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s curtseys gracefully.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You curtsey gracefully.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s curtseys gracefully before for you.' \
                % caller.name
            target.msg(string)
            string = 'You curtsey gracefully before %s.' % target.name
            caller.msg(string)
            string = '%s curtseys gracefully before %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdHug(Command):

    """
    A hug emote.

    Usage: 
      hug

    """

    key = 'hug'
    aliases = ['embrace']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s awaits a hug with open arms.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You await your hug with open arms.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gives you a hug!' % caller.name
            target.msg(string)
            string = 'You give %s a hug!' % target.name
            caller.msg(string)
            string = '%s hugs %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdKiss(Command):

    """
    A kiss emote.

    Usage: 
      kiss

    """

    key = 'kiss'
    aliases = ['smooch', 'snog']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s purses those lips for a smooch.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You purse those kissers for a smooch.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gives you a smooch!' % caller.name
            target.msg(string)
            string = 'You give %s a smooch!' % target.name
            caller.msg(string)
            string = '%s gives %s a smooch!' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdFrown(Command):

    """
    A frown emote.

    Usage: 
      frown

    """

    key = 'frown'

    # aliases = ["frown at"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s frowns darkly.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You frown darkly.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s frowns darkly at you.' % caller.name
            target.msg(string)
            string = 'You frown darkly at %s.' % target.name
            caller.msg(string)
            string = '%s frowns darkly at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdMutter(Command):

    """
    A mutter emote.

    Usage: 
      mutter

    """

    key = 'mutter'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s mutters angrily, unmindful of who hears.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You mutter angrily, not mindful of who might hear you.'
                       )
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s mutters angrily in your general direction.' \
                % caller.name
            target.msg(string)
            string = \
                'You mutter angrily in the general direction of %s.' \
                % target.name
            caller.msg(string)
            string = \
                '%s mutters angrily in the general direction of %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGreet(Command):

    """
    Raise a hand in greeting towards someone.

    Usage:
      greet

    """

    key = 'greet'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s raises a hand in greeting.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You raise a hand in greeting.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s raises a hand towards you in greeting.' \
                % caller.name
            target.msg(string)
            string = 'You raise a hand towards %s in greeting.' \
                % target.name
            caller.msg(string)
            string = '%s raises a hand towards %s in greeting.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPet(Command):

    """
    Gently pet something (or someone).

    Usage:
      pet <something or someone>

    """

    key = 'pet'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s makes a petting motion with %s hand.' \
                % (caller.name, caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You make a petting motion with your hand.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gently pets you.' % caller.name
            target.msg(string)
            string = 'You gently pet %s.' % target.name
            caller.msg(string)
            string = '%s gently pets %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdScream(Command):

    """
    A scream emote.

    Usage: 
      scream

    """

    key = 'scream'

    # aliases = ["scream at"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s screams loudly! Aaaaaaah! Not awkward.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You scream at the top of your lungs!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s loudly at you! So weird!' % caller.name
            target.msg(string)
            string = \
                'You scream loudly at %s, not being weird or anything.' \
                % target.name
            caller.msg(string)
            string = '%s screams loudly at %s. These two have issues.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWhine(Command):

    """
    A whine emote.

    Usage: 
      whine [<target>]

    """

    key = 'whine'

    # aliases = ["whine to", "whine at"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s whines annoyingly.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You whine, trying not to be too annoying.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s whines at you annoyingly.' % caller.name
            target.msg(string)
            string = 'You whine at %s, trying not to be too annoying.' \
                % target.name
            caller.msg(string)
            string = '%s whiens annoyingly towards %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPoke(Command):

    """
    A poke emote.

    Usage: 
      poke

    """

    key = 'poke'
    aliases = ['prod']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s lifts a finger, threatening to poke.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg("You lift your poking finger, ready to poke. You'll do it!"
                       )
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s pokes you in the ribs.' % caller.name
            target.msg(string)
            string = \
                'You poke %s in the ribs, probably not for the first time.' \
                % target.name
            caller.msg(string)
            string = '%s pokes %s in the ribs.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdTear(Command):

    """
    A tear emote.

    Usage: 
      tear

    """

    key = 'tear'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = 'A single tear slips down the face of %s.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('A single tear slips down your face.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = \
                '%s looks at you and a single tear slips down that face.' \
                % caller.name
            target.msg(string)
            string = \
                'You look at %s as a single tear slips down your face.' \
                % target.name
            caller.msg(string)
            string = \
                'A single tear slips down the face %s, who is looking at %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCry(Command):

    """
    A cry emote.

    Usage: 
      cry

    """

    key = 'cry'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s cries hysterically.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You cry hysterically.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s cries hysterically in front of you.' \
                % caller.name
            target.msg(string)
            string = 'You cry hysterically in front of %s.' \
                % target.name
            caller.msg(string)
            string = '%s cries hysterically in front of %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPoint(Command):

    """
    A point emote.

    Usage: 
      point <person, direction, up, down>

    """

    key = 'point'
    aliases = ['point']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s points off into the distance.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You point off into the distance.')
        else:
            if self.target == 'north':
                string = '%s points to the north.' % caller.name
                caller.location.msg_contents(string, exclude=[caller])
                caller.msg('You point to the north.')
            elif self.target == 'east':
                string = '%s points to the east.' % caller.name
                caller.location.msg_contents(string, exclude=[caller])
                caller.msg('You point to the east.')
            elif self.target == 'south':
                string = '%s points to the south.' % caller.name
                caller.location.msg_contents(string, exclude=[caller])
                caller.msg('You point to the south.')
            elif self.target == 'west':
                string = '%s points to the west.' % caller.name
                caller.location.msg_contents(string, exclude=[caller])
                caller.msg('You point to the west.')
            elif self.target == 'up':
                string = '%s points straight up.' % caller.name
                caller.location.msg_contents(string, exclude=[caller])
                caller.msg('You point straight up.')
            elif self.target == 'down':
                string = '%s points down towards the ground.' \
                    % caller.name
                caller.location.msg_contents(string, exclude=[caller])
                caller.msg('You point down towards the ground.')
            else:
                target = caller.search(self.target)
                if not target:

                    # caller.search handles error messages

                    return
                string = '%s points directly at you.' % caller.name
                target.msg(string)
                string = 'You point directly at %s.' % target.name
                caller.msg(string)
                string = '%s points directly at %s.' % (caller.name,
                        target.name)
                caller.location.msg_contents(string, exclude=[caller,
                        target])


class CmdFacepalm(Command):

    """
    Face, meet palm.

    Usage: 
      facepalm

    """

    key = 'facepalm'
    aliases = ['f2p']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = \
                "%s facepalms. Why? I mean, at least it's not a double facepalm." \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You facepalm because why?')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = \
                '%s facepalms before you but it coud be worse, right?' \
                % caller.name
            target.msg(string)
            string = 'You facepalm right in front of %s because why?' \
                % target.name
            caller.msg(string)
            string = '%s looks at %s and then facepalms.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPray(Command):

    """
    A pray emote.

    Usage: 
      pray

    """

    key = 'pray'
    aliases = ['hope']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = \
                '%s prays humbly to the Gods and their Encarnations.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You pray humbly before the Gods and their Encarnations.'
                       )
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = \
                '%s prays for you, to the Gods and their Enarnations.' \
                % caller.name
            target.msg(string)
            string = \
                'You pray to the Gods and their Encarnations for mercy for %s.' \
                % target.name
            caller.msg(string)
            string = \
                '%s prays humbly to the Gods and their Encarnations to show mercy upon %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSmile(Command):

    """
    A smile emote.

    Usage: 
      smile [<someone>]

    Smiles to someone in your vicinity or to the room
    in general.

    """

    key = 'smile'

    # aliases = ["smile at"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s smiles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You smile.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s smiles at you.' % caller.name
            target.msg(string)
            string = 'You smile at %s.' % target.name
            caller.msg(string)
            string = '%s smiles at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGrin(Command):

    """
    A grin emote.

    Usage: 
      grin [<someone>]

    Grin to someone in your vicinity or to the room
    in general.

    """

    key = 'grin'

    # aliases = ["grin at"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s grins mischievously.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You grin mischievously.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s grins mischievously at you.' % caller.name
            target.msg(string)
            string = 'You grin mischievously at %s.' % target.name
            caller.msg(string)
            string = '%s grins mischievously at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdBow(Command):

    """
    A bow emote.

    Usage: 
      bow [<someone>]

    """

    key = 'bow'

    # aliases = ["bow"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s bows deeply.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You bow deeply.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s bows deeply before you.' % caller.name
            target.msg(string)
            string = 'You bow deeply before %s.' % target.name
            caller.msg(string)
            string = '%s bows deeply before %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdKneel(Command):

    """
    A kneel emote.

    Usage:
      kneel [<someone>]

    """

    key = 'kneel'

    # aliases = ["kneel before"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s kneels humbly on the ground.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You kneel humbly on the ground.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s kneels humbly on the ground before you.' \
                % caller.name
            target.msg(string)
            string = 'You kneel humbly on the ground before %s.' \
                % target.name
            caller.msg(string)
            string = '%s kneels humbly on the ground before %s.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdBeg(Command):

    """
    A beg emote.

    Usage: 
      beg [<someone>]

    """

    key = 'beg'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s begs pitifully to anyone who will listen.' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You beg pitifully to anyone who will listen.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s begs you pitifully for mercy.' % caller.name
            target.msg(string)
            string = 'You beg %s pitifully for mercy.' % target.name
            caller.msg(string)
            string = '%s begs %s pitifully for mercy.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdParagon(Command):

    """
    Looking good!

    Usage:
      paragon

    """

    key = 'paragon'
    aliases = ['cool']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s stands tall before you, a virtual paragon!' \
                % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You are looking pretty cool right now!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s stands tall before you, a virtual paragon!' \
                % caller.name
            target.msg(string)
            string = 'You try to look cool in front of %s.' \
                % target.name
            caller.msg(string)
            string = '%s stands tall before %s, trying to look cool.' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSmooth(Command):

    """
    Smooth back that hair!

    Usage:
      smooth

    """

    key = 'smooth'
    aliases = ['slick']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s slicks back %s hair.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You slick back that hair!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s looks at you while smoothing back %s hair.' \
                % (caller.name, caller.db.genderp)
            target.msg(string)
            string = 'You look at %s and smooth back your hair.' \
                % target.name
            caller.msg(string)
            string = 'Eyes on %s, %s smooths back %s hair.' \
                % (target.name, caller.name, caller.db.genderp)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdFistBump(Command):

    """
    Bro (or sister) fister!

    Usage:
      fistbump

    """

    key = 'fistbump'
    aliases = ['brofist', 'sisfist']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s fist bumps with... no one. Sad!' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You fist bump with your imaginary bro.  Not awkward.'
                       )
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = \
                'Against your better judgment, you fist bump with %s.' \
                % caller.name
            target.msg(string)
            string = 'You and %s bump fists.' % target.name
            caller.msg(string)
            string = \
                '%s and %s bump fists.  Can you feel the bromance?' \
                % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdHi(Command):

    """
    Raise your hand in a greeting to someone.

    Usage:
      hi <someone>

    """

    key = 'hi'
    aliases = ['hello', 'nihao']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '"Hi!" %s blurts out.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('"Hi!" you blurt out.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '"Hi!" %s says to you.' % caller.name
            target.msg(string)
            string = '"Hi!" you say to %s.' % target.name
            caller.msg(string)
            string = '"Hi!" %s says to %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdHeh(Command):

    """
    Almost a laugh but not quite...

    Usage:
      heh

    """

    key = 'heh'
    aliases = ['hah']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller

        string = '"Heh," %s grunts.' % caller.name
        caller.location.msg_contents(string, exclude=caller)
        caller.msg('"Heh," you grunt.')


class CmdOK(Command):

    """
    Express your consent, approval or just maybe, indifference.

    Usage:
      ok <target>

    """

    key = 'ok'
    aliases = ['ok!', 'kk']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '"Ok!" %s blurts out.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('"Ok!" you blurt out.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '"Ok!" %s says to you.' % caller.name
            target.msg(string)
            string = 'You look at %s and say, "Ok!"' % target.name
            caller.msg(string)
            string = '"Ok!", %s says to %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdYo(Command):

    """
    A "Yo!" emote.

    Usage:
      yo

    """

    key = 'yo'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '"Yo!" %s says.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('"Yo!" you say.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '"Yo!" %s says to you.' % caller.name
            target.msg(string)
            string = '"Yo!" you say to %s.' % target.name
            caller.msg(string)
            string = '"Yo!" %s says to %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPonder(Command):

    """
    A ponder emote.

    Usage:
      ponder

    """

    key = 'ponder'
    aliases = ['think']
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s ponders... things.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You ponder... things.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s looks at you and rubs %s chin thoughtfully.' \
                % (caller.name, caller.db.genderp)
            target.msg(string)
            string = 'You look at %s and rub your chin thoughtfully.' \
                % target.name
            caller.msg(string)
            string = '%s looks at %s and rubs %s chin thoughtfully.' \
                % (caller.name, target.name, caller.db.genderp)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdShrug(Command):

    """
    A shrug emote.

    Usage:
      shrug <target>

    """

    key = 'shrug'

    # aliases = ["mad"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s shrugs %s shoulders.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You shrug your shoulders.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s looks at you and shrugs.' % caller.name
            target.msg(string)
            string = 'You look at %s and shrug.' % target.name
            caller.msg(string)
            string = '%s looks at %s and shrugs.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdJump(Command):

    """
    A jump emote.

    Usage: 
      jump 

    

    """

    key = 'jump'

    # aliases = ["ju"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s jumps up and down!' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You jump up and down!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s jumps toward you!' % caller.name
            target.msg(string)
            string = 'You jumps toward %s!' % target.name
            caller.msg(string)
            string = '%s jumps towards %s!' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWhistle(Command):

    """
    A whistle emote.

    Usage: 
      whistle



    """

    key = 'whistle'

    # aliases = ["whist"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s whistles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You whistle.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s whistles at you.' % caller.name
            target.msg(string)
            string = 'You whistles at %s.' % target.name
            caller.msg(string)
            string = '%s whistles at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWag(Command):

    """
    A finger wag emote.

    Usage: 
        wag


    """

    key = 'wag'

    # aliases = ["wag"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s wags %s finger back and forth.' \
                % (caller.name, caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You wag your finger back and forth.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s wags a finger at you.' % caller.name
            target.msg(string)
            string = 'You wags a finger at %s.' % target.name
            caller.msg(string)
            string = '%s wags a finger at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdStare(Command):

    """
    A stare emote.

    Usage: 
      stare


    """

    key = 'stare'

    # aliases = ["stare"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s stares.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You stare.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s stares at you.' % caller.name
            target.msg(string)
            string = 'You stare at %s.' % target.name
            caller.msg(string)
            string = '%s stares at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGlare(Command):

    """
    A glare emote.

    Usage: 
      glare


    """

    key = 'glare'

    # aliases = ["glare"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s glares.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You glare.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s glares at you.' % caller.name
            target.msg(string)
            string = 'You glare at %s.' % target.name
            caller.msg(string)
            string = '%s glare at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdFlutter(Command):

    """
    An eyelid flutter emote.

    Usage: 
      flutter



    """

    key = 'flutter'

    # aliases = ["flut"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s flutters %s eyelashes.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You flutter your eyelashes.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s flutters %s eyelashes at you.' % (caller.name,
                    caller.db.genderp)
            target.msg(string)
            string = 'You flutter your eyelashes at %s.' % target.name
            caller.msg(string)
            string = '%s flutters %s eyelashes at %s.' % (caller.name,
                    caller.db.genderp, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdEye(Command):

    """
    An eye emote.

    Usage: 
      eye [<object>]


    """

    key = 'eye'

    # aliases = ["eye"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s eyes the area appraisingly.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You grin mischievously.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s eyes you appraisingly.' % caller.name
            target.msg(string)
            string = 'You eye %s appraisingly.' % target.name
            caller.msg(string)
            string = '%s eyes %s appraisingly.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGrimace(Command):

    """
    A grimace emote.

    Usage: 
      grimace [<object>]


    """

    key = 'grimace'

    # aliases = ["grim"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s grimaces.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You grimaces.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s grimaces at you.' % caller.name
            target.msg(string)
            string = 'You grimaces at %s.' % target.name
            caller.msg(string)
            string = '%s grimaces at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdLeer(Command):

    """
    A leer emote.

    Usage: 
      leer [<object>]

    """

    key = 'leer'

    # aliases = ["leer"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s leers.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You leer.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s leers at you.' % caller.name
            target.msg(string)
            string = 'You leers at %s.' % target.name
            caller.msg(string)
            string = '%s leers at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdNarrow(Command):

    """
    An eye narrow emote.

    Usage: 
      narrow [<object>]


    """

    key = 'narrow'

    # aliases = ["narrow"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s narrows %s eyes.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You narrow your eyes.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s narrows %s eyes at you.' % (caller.name,
                    caller.db.genderp)
            target.msg(string)
            string = 'You narrow your eyes at %s.' % target.name
            caller.msg(string)
            string = '%s narrows %s eyes at %s.' % (caller.name,
                    caller.db.genderp, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdNudge(Command):

    """
    A nudge emote.

    Usage: 
      nudge [<object>]


    """

    key = 'nudge'

    # aliases = ["nudge"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s nudges something with %s foot absently.' \
                % (caller.name, caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You nudge something with your foot.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s nudges you.' % caller.name
            target.msg(string)
            string = 'You nudge %s.' % target.name
            caller.msg(string)
            string = '%s nudges %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdOgle(Command):

    """
    An ogle emote.

    Usage: 
      ogle [<object>]


    """

    key = 'ogle'

    # aliases = ["ogle"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s ogles the area with %s eyes.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You ogle the area with your eyes.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s ogles %s eyes at you.' % (caller.name,
                    caller.db.genderp)
            target.msg(string)
            string = 'You ogle your eyes at %s.' % target.name
            caller.msg(string)
            string = '%s ogles %s eyes at %s.' % (caller.name,
                    caller.db.genderp, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPeer(Command):

    """
    A peer emote.

    Usage: 
      peer [<object>]


    """

    key = 'peer'

    # aliases = ["peer"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s peers.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You peer.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s peers at you.' % caller.name
            target.msg(string)
            string = 'You peers at %s.' % target.name
            caller.msg(string)
            string = '%s peers at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdScowl(Command):

    """
    A scowl emote.

    Usage: 
      scowl [<object>]


    """

    key = 'scowl'

    # aliases = ["scowl"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s scowls.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You scowl.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s scowls at you.' % caller.name
            target.msg(string)
            string = 'You scowls at %s.' % target.name
            caller.msg(string)
            string = '%s scowls at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSnarl(Command):

    """
    A snarl emote.

    Usage: 
      snarl [<object>]


    """

    key = 'snarl'

    # aliases = ["snarl"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s snarls.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You snarl.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s snarls at you.' % caller.name
            target.msg(string)
            string = 'You snarls at %s.' % target.name
            caller.msg(string)
            string = '%s snarls at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdTickle(Command):

    """
    A tickle emote.

    Usage: 
      tickle [<object>]


    """

    key = 'tickle'

    # aliases = ["tickle"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s appears to be tickling %self.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You tickle yourself.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s tickles you.' % caller.name
            target.msg(string)
            string = 'You tickle %s.' % target.name
            caller.msg(string)
            string = '%s tickles %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWhimper(Command):

    """
    A whimper emote.

    Usage: 
      whimper [<object>]


    """

    key = 'whimper'

    # aliases = ["whimper"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s whimpers.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You whimper.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s whimpers at you.' % caller.name
            target.msg(string)
            string = 'You whimper at %s.' % target.name
            caller.msg(string)
            string = '%s whimpers at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdApplaud(Command):

    """
    An applaud emote.

    Usage: 
      applaud [<object>]


    """

    key = 'applaud'

    # aliases = ["applaud"]

    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s applauds!' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You applaud!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s applauds you!' % caller.name
            target.msg(string)
            string = 'You applauds %s!' % target.name
            caller.msg(string)
            string = '%s applauds %s!' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCuddle(Command):

    """
    A cuddle emote.

    Usage: 
      cuddle [<object>]


    """

    key = 'cuddle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s cuddles %s self.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You cuddle yourself.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s cuddles you.' % caller.name
            target.msg(string)
            string = 'You cuddle %s.' % target.name
            caller.msg(string)
            string = '%s cuddles %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdNibble(Command):

    """
    A nibble emote.

    Usage: 
      nibble [<object>]


    """

    key = 'nibble'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s nibbles on %s fingers.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You nibble on your fingers.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s nibbles on you.' % caller.name
            target.msg(string)
            string = 'You nibble on %s.' % target.name
            caller.msg(string)
            string = '%s nibbles on %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdNuzzle(Command):

    """
    A nuzzle emote.

    Usage: 
      nuzzle [<object>]


    """

    key = 'nuzzle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s nuzzles %sself.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You nuzzle yourself.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s nuzzles you.' % caller.name
            target.msg(string)
            string = 'You nuzzle %s.' % target.name
            caller.msg(string)
            string = '%s nuzzles %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSqueeze(Command):

    """
    A squeeze emote.

    Usage: 
      squeeze [<object>]


    """

    key = 'squeeze'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s squeezes %s hands together.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You squeeze your hands together.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s squeezes you.' % caller.name
            target.msg(string)
            string = 'You squeeze %s.' % target.name
            caller.msg(string)
            string = '%s squeezes %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGreet(Command):

    """
    A greet emote.

    Usage: 
      greet [<object>]


    """

    key = 'greet'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s raises %s hand in greeting.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You raise your hand in greeting.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s raises %s hand, greeting you.' % (caller.name,
                    caller.db.genderp)
            target.msg(string)
            string = 'You raise your hand, greeting %s.' % target.name
            caller.msg(string)
            string = '%s raises %s hand, greeting %s.' % (caller.name,
                    caller.db.genderp, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGrovel(Command):

    """
    A grovel emote.

    Usage: 
      grovel [<object>]


    """

    key = 'grovel'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s grovels.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You grovel.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s grovels to you.' % caller.name
            target.msg(string)
            string = 'You grovel to %s.' % target.name
            caller.msg(string)
            string = '%s grovels to %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdTap(Command):

    """
    A tap emote.

    Usage: 
      tap [<object>]


    """

    key = 'tap'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s taps %s fingers.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You tap your fingers.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s taps you.' % caller.name
            target.msg(string)
            string = 'You tap %s.' % target.name
            caller.msg(string)
            string = '%s taps %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdComfort(Command):

    """
    A comfort emote.

    Usage: 
      comfort [<object>]


    """

    key = 'comfort'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s comforts %sself.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You comfort yourself.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s comforts you.' % caller.name
            target.msg(string)
            string = 'You comfort %s.' % target.name
            caller.msg(string)
            string = '%s comforts %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdBlush(Command):

    """
    A blush emote.

    Usage: 
      blush [<object>]


    """

    key = 'blush'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s blushes.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You blush.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s blushes at you.' % caller.name
            target.msg(string)
            string = 'You blush at %s.' % target.name
            caller.msg(string)
            string = '%s blushes at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGasp(Command):

    """
    A gasp emote.

    Usage: 
      gasp [<object>]


    """

    key = 'gasp'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s gasps.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You gasp.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gasps at you.' % caller.name
            target.msg(string)
            string = 'You gasp at %s.' % target.name
            caller.msg(string)
            string = '%s gasps at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCringe(Command):

    """
    A cringe emote.

    Usage: 
      cringe [<object>]


    """

    key = 'cringe'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s cringes.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You cringe.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s cringes at you.' % caller.name
            target.msg(string)
            string = 'You cringe at %s.' % target.name
            caller.msg(string)
            string = '%s cringes at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCheer(Command):

    """
    A cheer emote.

    Usage: 
      cheer [<object>]


    """

    key = 'cheer'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s cheers!.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You cheer!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s cheers for you!' % caller.name
            target.msg(string)
            string = 'You cheer for %s!' % target.name
            caller.msg(string)
            string = '%s cheers for %s!' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdChortle(Command):

    """
    A chortle emote.

    Usage: 
      chortle [<object>]


    """

    key = 'chortle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s chortles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You chortle.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s chortles at you.' % caller.name
            target.msg(string)
            string = 'You chortle at %s.' % target.name
            caller.msg(string)
            string = '%s chortles at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSigh(Command):

    """
    A sigh emote.

    Usage: 
      sigh [<object>]


    """

    key = 'sigh'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sighs.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You sigh.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sighs at you.' % caller.name
            target.msg(string)
            string = 'You sigh at %s.' % target.name
            caller.msg(string)
            string = '%s sighs at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSnore(Command):

    """
    A snore emote.

    Usage: 
      snore [<object>]


    """

    key = 'snore'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s snores.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You snore.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s snores at you.' % caller.name
            target.msg(string)
            string = 'You snore at %s.' % target.name
            caller.msg(string)
            string = '%s snores at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGuffaw(Command):

    """
    A guffaw emote.

    Usage: 
      guffaw [<object>]


    """

    key = 'guffaw'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s guffaws.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You guffaw.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s guffaws at you.' % caller.name
            target.msg(string)
            string = 'You guffaw at %s.' % target.name
            caller.msg(string)
            string = '%s guffaws at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSob(Command):

    """
    A sob emote.

    Usage: 
      sob [<object>]


    """

    key = 'sob'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sobs.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You sob.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sobs at you.' % caller.name
            target.msg(string)
            string = 'You sob at %s.' % target.name
            caller.msg(string)
            string = '%s sobs at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSnigger(Command):

    """
    A snigger emote.

    Usage: 
      snigger [<object>]


    """

    key = 'snigger'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sniggers.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You snigger.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sniggers at you.' % caller.name
            target.msg(string)
            string = 'You snigger at %s.' % target.name
            caller.msg(string)
            string = '%s sniggers at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdChuckle(Command):

    """
    A chuckle emote.

    Usage: 
      chuckle [<object>]


    """

    key = 'chuckle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s chuckles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You chuckle.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s chuckles at you.' % caller.name
            target.msg(string)
            string = 'You chuckle at %s.' % target.name
            caller.msg(string)
            string = '%s chuckles at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdClap(Command):

    """
    A clap emote.

    Usage: 
      clap [<object>]


    """

    key = 'clap'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s claps.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You clap.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s claps for you.' % caller.name
            target.msg(string)
            string = 'You clap for %s.' % target.name
            caller.msg(string)
            string = '%s claps for %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdBlink(Command):

    """
    A blink emote.

    Usage: 
      blink [<object>]


    """

    key = 'blink'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s blinks.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You blink.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s blinks at you.' % caller.name
            target.msg(string)
            string = 'You blink at %s.' % target.name
            caller.msg(string)
            string = '%s blinks at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGiggle(Command):

    """
    A giggle emote.

    Usage: 
      giggle [<object>]


    """

    key = 'giggle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s giggles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You giggle.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s giggles at you.' % caller.name
            target.msg(string)
            string = 'You giggle at %s.' % target.name
            caller.msg(string)
            string = '%s giggles at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCackle(Command):

    """
    A cackle emote.

    Usage: 
      cackle [<object>]


    """

    key = 'cackle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s cackles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You cackle.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s cackles at you.' % caller.name
            target.msg(string)
            string = 'You cackle at %s.' % target.name
            caller.msg(string)
            string = '%s cackle at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSniff(Command):

    """
    A sniff emote.

    Usage: 
      sniff [<object>]


    """

    key = 'sniff'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sniffs.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You sniff.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sniffs you.' % caller.name
            target.msg(string)
            string = 'You sniff %s.' % target.name
            caller.msg(string)
            string = '%s sniffs %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdBurp(Command):

    """
    A burp emote.

    Usage: 
      burp [<object>]


    """

    key = 'burp'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s burps.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You burp.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s burps at you.' % caller.name
            target.msg(string)
            string = 'You burp at %s.' % target.name
            caller.msg(string)
            string = '%s burps at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdHowl(Command):

    """
    A howl emote.

    Usage: 
      howl [<object>]


    """

    key = 'howl'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s howls.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You howl.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s howls at you.' % caller.name
            target.msg(string)
            string = 'You howl at %s.' % target.name
            caller.msg(string)
            string = '%s howls at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGroan(Command):

    """
    A groan emote.

    Usage: 
      groan [<object>]


    """

    key = 'groan'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s groans.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You groan.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s groans at you.' % caller.name
            target.msg(string)
            string = 'You groan at %s.' % target.name
            caller.msg(string)
            string = '%s groans at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdMoan(Command):

    """
    A moan emote.

    Usage: 
      moan [<object>]


    """

    key = 'moan'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s moans.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You moan.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s moans at you.' % caller.name
            target.msg(string)
            string = 'You moan at %s.' % target.name
            caller.msg(string)
            string = '%s moans at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWail(Command):

    """
    A wail emote.

    Usage: 
      wail [<object>]


    """

    key = 'wail'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s wails!' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You wail!')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s wails at you!' % caller.name
            target.msg(string)
            string = 'You wail at %s!' % target.name
            caller.msg(string)
            string = '%s wails at %s!' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPout(Command):

    """
    A pout emote.

    Usage: 
      pout [<object>]


    """

    key = 'pout'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s pouts.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You pout.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s pouts at you.' % caller.name
            target.msg(string)
            string = 'You pout at %s.' % target.name
            caller.msg(string)
            string = '%s pouts at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdShudder(Command):

    """
    A shudder emote.

    Usage: 
      shudder [<object>]


    """

    key = 'shudder'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s shudders.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You shudder.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s shudders at you.' % caller.name
            target.msg(string)
            string = 'You shudder at %s.' % target.name
            caller.msg(string)
            string = '%s shudders at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdFidget(Command):

    """
    A fidget emote.

    Usage: 
      fidget [<object>]


    """

    key = 'fidget'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s fidgets.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You fidget.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s fidgets at you.' % caller.name
            target.msg(string)
            string = 'You fidget at %s.' % target.name
            caller.msg(string)
            string = '%s fidgets at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGulp(Command):

    """
    A gulp emote.

    Usage: 
      gulp [<object>]


    """

    key = 'gulp'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s gulps.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You gulp.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gulps at you.' % caller.name
            target.msg(string)
            string = 'You gulp at %s.' % target.name
            caller.msg(string)
            string = '%s gulps at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSkip(Command):

    """
    A skip emote.

    Usage: 
      skip [<object>]


    """

    key = 'skip'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s skips around.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You skip around.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s skips to you.' % caller.name
            target.msg(string)
            string = 'You skip to %s.' % target.name
            caller.msg(string)
            string = '%s skips to %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSnort(Command):

    """
    A snort emote.

    Usage: 
      snort [<object>]


    """

    key = 'snort'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s snorts.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You snort.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s snorts at you.' % caller.name
            target.msg(string)
            string = 'You snort at %s.' % target.name
            caller.msg(string)
            string = '%s snorts at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdWheeze(Command):

    """
    A wheeze emote.

    Usage: 
      wheeze [<object>]


    """

    key = 'wheeze'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s wheezes.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You wheeze.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s wheezes at you.' % caller.name
            target.msg(string)
            string = 'You wheeze at %s.' % target.name
            caller.msg(string)
            string = '%s wheezes at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdShiver(Command):

    """
    A shiver emote.

    Usage: 
      shiver [<object>]


    """

    key = 'shiver'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s shivers.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You shiver.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s shivers at you.' % caller.name
            target.msg(string)
            string = 'You shiver at %s.' % target.name
            caller.msg(string)
            string = '%s shivers at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdFume(Command):

    """
    A fume emote.

    Usage: 
      fume [<object>]


    """

    key = 'fume'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s fumes.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You fume.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s fumes at you.' % caller.name
            target.msg(string)
            string = 'You fume at %s.' % target.name
            caller.msg(string)
            string = '%s fumes at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdShake(Command):

    """
    A shake emote.

    Usage: 
      shake [<object>]


    """

    key = 'shake'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s shakes around.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You shake around.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s shakes you!' % caller.name
            target.msg(string)
            string = 'You shake %s!' % target.name
            caller.msg(string)
            string = '%s shakes %s!' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdPace(Command):

    """
    A pace emote.

    Usage: 
      pace [<object>]


    """

    key = 'pace'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s paces slowly.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You pace slowly.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s paces towards you.' % caller.name
            target.msg(string)
            string = 'You pace towards %s.' % target.name
            caller.msg(string)
            string = '%s paces towards %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSqueak(Command):

    """
    A squeak emote.

    Usage: 
      squeak [<object>]


    """

    key = 'squeak'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s squeaks.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You squeak.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s squeaks at you.' % caller.name
            target.msg(string)
            string = 'You squeak at %s.' % target.name
            caller.msg(string)
            string = '%s squeaks at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSlurp(Command):

    """
    A slurp emote.

    Usage: 
      slurp [<object>]


    """

    key = 'slurp'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s slurps.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You slurp.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s slurps you.' % caller.name
            target.msg(string)
            string = 'You slurp %s.' % target.name
            caller.msg(string)
            string = '%s slurps %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdHum(Command):

    """
    A hum emote.

    Usage: 
      hum [<object>]


    """

    key = 'hum'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s hums.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You hum.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s hums at you.' % caller.name
            target.msg(string)
            string = 'You hum at %s.' % target.name
            caller.msg(string)
            string = '%s hums at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSneeze(Command):

    """
    A sneeze emote.

    Usage: 
      sneeze [<object>]


    """

    key = 'sneeze'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sneezes.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You sneeze.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sneezes at you.' % caller.name
            target.msg(string)
            string = 'You sneeze at %s.' % target.name
            caller.msg(string)
            string = '%s sneezes at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSulk(Command):

    """
    A sulk emote.

    Usage: 
      sulk [<object>]


    """

    key = 'sulk'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sulks.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You sulk.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sulks at you.' % caller.name
            target.msg(string)
            string = 'You sulk at %s.' % target.name
            caller.msg(string)
            string = '%s sulks at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCough(Command):

    """
    A cough emote.

    Usage: 
      cough [<object>]


    """

    key = 'cough'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s coughs.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You cough.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s coughs at you.' % caller.name
            target.msg(string)
            string = 'You cough at %s.' % target.name
            caller.msg(string)
            string = '%s coughs at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSneer(Command):

    """
    A sneer emote.

    Usage: 
      sneer [<object>]


    """

    key = 'sneer'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sneers.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You sneer.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sneers at you.' % caller.name
            target.msg(string)
            string = 'You sneer at %s.' % target.name
            caller.msg(string)
            string = '%s sneers at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSpit(Command):

    """
    A spit emote.

    Usage: 
      spit [<object>]


    """

    key = 'spit'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s spits.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You spit.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s spits at you.' % caller.name
            target.msg(string)
            string = 'You spit at %s.' % target.name
            caller.msg(string)
            string = '%s spits at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdYawn(Command):

    """
    A yawn emote.

    Usage: 
      yawn [<object>]


    """

    key = 'yawn'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s yawns.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You yawn.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s yawns at you.' % caller.name
            target.msg(string)
            string = 'You yawn at %s.' % target.name
            caller.msg(string)
            string = '%s yawns at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdRaise(Command):

    """
    A toasting emote.

    Usage: 
      raise [<object>]


    """

    key = 'raise'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s raises a toast.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You raise a toast.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s raises a toast to you.' % caller.name
            target.msg(string)
            string = 'You raise a toast to %s.' % target.name
            caller.msg(string)
            string = '%s raises a toast to %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdTitter(Command):

    """
    A titter emote.

    Usage: 
      titter [<object>]


    """

    key = 'titters'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s titters.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You titter.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s titters at you.' % caller.name
            target.msg(string)
            string = 'You titter at %s.' % target.name
            caller.msg(string)
            string = '%s titters at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdStagger(Command):

    """
    A stagger emote.

    Usage: 
      stagger [<object>]


    """

    key = 'stagger'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s staggers around.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You stagger around.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s staggers towards you.' % caller.name
            target.msg(string)
            string = 'You stagger towards %s.' % target.name
            caller.msg(string)
            string = '%s staggers towards %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdSway(Command):

    """
    A sway emote.

    Usage: 
      sway [<object>]


    """

    key = 'sway'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s sways.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You sway.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s sways at you.' % caller.name
            target.msg(string)
            string = 'You sway at %s.' % target.name
            caller.msg(string)
            string = '%s sways at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdCaress(Command):

    """
    A caress emote.

    Usage: 
      caress [<object>]


    """

    key = 'caress'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s caresses %sself.' % (caller.name,
                    caller.db.genderp)
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You caress yourself.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s caresses you.' % caller.name
            target.msg(string)
            string = 'You caress %s.' % target.name
            caller.msg(string)
            string = '%s caresses %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGurgle(Command):

    """
    A gurgle emote.

    Usage: 
      gurgle [<object>]


    """

    key = 'gurgle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s gurgles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You gurgle.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gurgles at you.' % caller.name
            target.msg(string)
            string = 'You gurgle at %s.' % target.name
            caller.msg(string)
            string = '%s gurgles at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGargle(Command):

    """
    A gargle emote.

    Usage: 
      gargle [<object>]


    """

    key = 'gargle'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s gargles.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You gargle.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s gargles you.' % caller.name
            target.msg(string)
            string = 'You gargle %s.' % target.name
            caller.msg(string)
            string = '%s gargle %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdHiss(Command):

    """
    A hiss emote.

    Usage: 
      hiss [<object>]


    """

    key = 'hiss'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s hisses.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You hiss.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s hisses at you.' % caller.name
            target.msg(string)
            string = 'You hiss at %s.' % target.name
            caller.msg(string)
            string = '%s hisses at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdBeam(Command):

    """
    A happy! emote.

    Usage: 
      beam [<object>]


    """

    key = 'beam'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s beams happily.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You beam happily.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s beams happily at you.' % caller.name
            target.msg(string)
            string = 'You beam happily at %s.' % target.name
            caller.msg(string)
            string = '%s beams happily at %s.' % (caller.name,
                    target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])


class CmdGrunt(Command):

    """
    A grunt emote.

    Usage: 
      grunt [<object>]


    """

    key = 'grunt'
    locks = 'cmd:all()'
    help_category = 'Emotes'

    def parse(self):
        '''Very trivial parser'''

        self.target = self.args.strip()

    def func(self):
        '''This actually does things'''

        caller = self.caller
        if not self.target or self.target == 'here':
            string = '%s grunts.' % caller.name
            caller.location.msg_contents(string, exclude=caller)
            caller.msg('You grunt.')
        else:
            target = caller.search(self.target)
            if not target:

                # caller.search handles error messages

                return
            string = '%s grunts at you.' % caller.name
            target.msg(string)
            string = 'You grunt at %s.' % target.name
            caller.msg(string)
            string = '%s grunts at %s.' % (caller.name, target.name)
            caller.location.msg_contents(string, exclude=[caller,
                    target])
