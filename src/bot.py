from __future__ import annotations

import os
import sys
import asyncio

import dotenv
import asyncpraw
import discord

import src.reddit_client as reddit
import src.data_handler as handler
import src.cogs as cogs


class DiscordBot:
    CONFIGS = {
        "SET_SIZE_CAP": 1_000,
        "QUEUE_SIZE_CAP": 5,
        "FETCH_LIMIT": 500,
        "MEDIA_MATCH_REGEX": r".+(jpg|png|jpeg|bmp|tiff|gif)$"
    }

    __slots__: tuple[str, ...] = (
        "discord_bot", "reddit_client_base", "reddit_client", "posts_handler"
    )

    def __init__(self: DiscordBot) -> None:
        """
        Instantiates all the required classes,
        Also handles loading in the required environment variables, and
        setting up the PATH
        """

        dotenv.load_dotenv()
        sys.path.append(os.path.abspath(os.path.pardir))

        self.discord_bot = discord.Bot(
            activity=(
                discord.Activity(
                    name="every sound",
                    type=discord.ActivityType.listening
                )
            ),
            intents=discord.Intents.all()
        )

        self.reddit_client_base = asyncpraw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"]
        )

        self.posts_handler = handler.PostsManager(**self.CONFIGS)

        self.reddit_client: reddit.RedditClient = reddit.RedditClient(
            self.reddit_client_base, self.posts_handler, **self.CONFIGS
        )

    def load_cogs(self: DiscordBot) -> None:
        self.discord_bot.add_cog(
            cogs.SlashCommandCog(
                self.discord_bot, self.reddit_client
            )
        )

    def run(self: DiscordBot) -> None:
        try:
            self.discord_bot.run(os.environ["DISCORD_TOKEN"])
        finally:
            event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            event_loop.run_until_complete(
                self.reddit_client.reddit_client.close()
            )


def main() -> None:
    discord_bot: DiscordBot = DiscordBot()
    discord_bot.load_cogs()
    discord_bot.run()


if __name__ == "__main__":
    main()
