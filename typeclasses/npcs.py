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
