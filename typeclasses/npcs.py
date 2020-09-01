from typeclasses.characters import Character


class NPC(Character):
    """
    A NPC typeclass which extends the character class.

    Made following tutorial:
    https://github.com/evennia/evennia/wiki/Tutorial-Aggressive-NPCs
    """

    def at_char_entered(self, character):
        """
         A simple is_aggressive check.
         Can be expanded upon later.
        """
        if self.db.is_aggressive:
            self.execute_cmd(f"say Graaah, die {character}!")
        else:
            self.execute_cmd(f"say Greetings, {character}!")


# from characters import Character
class ReapterNPC(Character):
    """
    A NPC typeclass which extends the character class.

    Made following:
    https://github.com/evennia/evennia/wiki/Tutorial-NPCs-listening
    """

    def at_heard_say(self, message, from_obj):
        """
        A simple listener and response. This makes it easy to change for
        subclasses of NPCs reacting differently to says.

        """
        # message will be on the form `<Person> says, "say_text"`
        # we want to get only say_text without the quotes and any spaces
        message = message.split('says, ')[1].strip(' "')

        # we'll make use of this in .msg() below
        return f"SQUAK {message}"

    def msg(self, text=None, from_obj=None, **kwargs):
        "Custom msg() method reacting to say."

        if from_obj != self:
            # make sure to not repeat what we ourselves said or we'll create a loop
            try:
                # if text comes from a say, `text` is `('say_text', {'type': 'say'})`
                say_text, is_say = text[0], text[1]['type'] == 'say'
            except Exception:
                is_say = False
            if is_say:
                # First get the response (if any)
                response = self.at_heard_say(say_text, from_obj)
                # If there is a response
                if response is not None:
                    # speak ourselves, using the return
                    self.execute_cmd("say %s" % response)

        # this is needed if anyone ever puppets this NPC - without it you would never
        # get any feedback from the server (not even the results of look)
        super().msg(text=text, from_obj=from_obj, **kwargs)
