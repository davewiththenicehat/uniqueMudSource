from evennia.utils.search import search_channel
from commands.command import Command


class CmdConnect(Command):
    """
    Connect to a channel.
    """

    key = "+"
    help_category = "Comms"
    locks = "cmd:not pperm(channel_banned)"
    auto_help = False

    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.args
        if not args:
            self.msg("Which channel do you want to connect to?")
            return

        channelname = self.args
        # https://evennia.readthedocs.io/en/latest/Coding-Utils.html#searching
        search_list = search_channel(channelname)
        # If we found no channel of that name stop.
        if not search_list:
            self.msg(f"Did not find a channel nammed: {self.args}")
            return

        # search_channel will return a list of objects found, even if 0 or 1 object is found
        # get the first channel found from our search above.
        channel = search_list[0]

        # Check permissions
        if not channel.access(caller, 'listen'):
            self.msg(f"{channel.key}: You are not allowed to listen to this channel.")
            return

        # If not connected to the channel, try to connect
        if not channel.has_connection(caller):
            if not channel.connect(caller):
                self.msg(f"{channel.key}: You are not allowed to join this channel.")
                return
            else:
                self.msg(f"You now are connected to the {channel.key.lower()} channel.")
        else:
            self.msg(f"You already are connected to the {channel.key.lower()} channel.")


class CmdDisconnect(Command):
    """
    Disconnect from a channel.
    """

    key = "-"
    help_category = "Comms"
    locks = "cmd:not pperm(channel_banned)"
    auto_help = False

    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.args
        if not args:
            self.msg("Which channel do you want to disconnect from?")
            return

        channelname = self.args
        # https://evennia.readthedocs.io/en/latest/Coding-Utils.html#searching
        search_list = search_channel(channelname)
        # If we found no channel of that name stop.
        if not search_list:
            self.msg(f"Did not find a channel nammed: {self.args}")
            return

        # search_channel will return a list of objects found, even if 0 or 1 object is found
        # get the first channel found from our search above.
        channel = search_list[0]

        # If connected to the channel, try to disconnect
        if channel.has_connection(caller):
            if not channel.disconnect(caller):
                self.msg(f"{channel.key}: You are not allowed to disconnect from this channel.")
                return
            else:
                self.msg(f"You stop listening to the {channel.key.lower()} channel.")
        else:
            self.msg(f"You are not connected to the {channel.key.lower()} channel.")
