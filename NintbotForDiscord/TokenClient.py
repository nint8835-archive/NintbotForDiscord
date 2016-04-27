import asyncio
import traceback

import discord


# Temporary patch by LeoV
class TokenClient(discord.Client):
    """A subclass of the discord.py client that implements support for bot accounts. Made by LeoV"""

    # noinspection PyMethodOverriding
    def run(self, token):
        """
        Log into and start the bot using a token
        :param token: The token to log in with
        """
        self.token = token
        self.headers['authorization'] = token
        self._is_logged_in.set()
        try:
            self.loop.run_until_complete(self.connect())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.logout())
            pending = asyncio.Task.all_tasks()
            gathered = asyncio.gather(*pending)
            # noinspection PyBroadException
            try:
                gathered.cancel()
                self.loop.run_forever()
                gathered.exception()
            except:
                traceback.print_exc(5)
        finally:
            self.loop.close()
