import discord
import asyncprawcore.exceptions

import src.reddit_client as reddit


class SlashCommandCog(discord.Cog):
    __slots__: tuple[str, str] = ("discord_bot", "reddit_client")

    def __init__(
            self,
            discord_bot: discord.Bot,
            reddit_client: reddit.RedditClient
    ) -> None:
        self.discord_bot: discord.Bot = discord_bot
        self.reddit_client: reddit.RedditClient = reddit_client

    async def fetch_urls(
            self,
            ctx: discord.ApplicationContext,
            subreddit: str,
            amount: int
    ) -> list[str] | None:
        """
        Fetches the list of URL, acts as a layer to catch major exceptions
        before sending the URLs

        :param ctx: The Application Context
        :param subreddit: Name of the subreddit
        :param amount: Amount of URLs to be scraped

        :return: A list of URLs or None if a response is already created
        """

        try:
            matching_urls: list[str] | None = (
                await self.reddit_client.fetch_matching_urls(
                    subreddit,
                    ctx.channel.nsfw,
                    amount
                )
            )
            if matching_urls is None:
                await ctx.respond("Couldn't find any juice")
                return

            return matching_urls
        except (
                asyncprawcore.exceptions.Redirect,
                asyncprawcore.exceptions.NotFound
        ):
            await ctx.respond("Invalid Subreddit")

    @discord.command(name="fetch")
    async def send_urls(
            self,
            ctx: discord.ApplicationContext,

            subreddit: discord.Option(
            discord.SlashCommandOptionType.string,
            required=True,
            description="Name of the subreddit"
            ),

            amount: discord.Option(
                discord.SlashCommandOptionType.integer,
                default=1,
                max_value=10,
                description="Amount of posts to fetch from (1-10)"
            )

    ) -> None:
        """
        The function that is converted to the Slash Command
        Fetched and sends the URLs, responses can vary depending on the
        status of the `fetch` itself

        :param ctx: The Application Context
        :param subreddit: Name of the subreddit
        :param amount: Amount of URLs to be scraped (Max 10)
        """

        # Defer is needed, since the process can take slightly longer
        # than the limit
        await ctx.defer(ephemeral=True)

        matching_urls: list[str] | None = await self.fetch_urls(
            ctx, subreddit, amount
        )

        if not matching_urls:
            return

        url: str
        for url in matching_urls:
            await ctx.send(url)

        if len(matching_urls) < amount:
            await ctx.respond(f"Sent: {len(matching_urls)}", ephemeral=True)

        await ctx.respond("Completed", ephemeral=True)
