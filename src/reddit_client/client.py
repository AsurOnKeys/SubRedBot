from __future__ import annotations

import re
import asyncpraw
import asyncpraw.models

from src.data_handler.posts import PostsManager


class RedditClient:
    __slots__: tuple[str, str] = (
        "reddit_client", "fetch_limit", "posts_handler", "media_match_regex"
    )

    def __init__(
            self: RedditClient,
            reddit_client: asyncpraw.reddit.Reddit,
            posts_handler: PostsManager,
            **configs: str | int
    ) -> None:
        """
        The class constructor (not much to say about it)

        :param reddit_client: The reddit client to be used
        :param posts_handler: The posts manager to be used
        :param configs: All configs can be passed for ease of use,
        and so I can add many more later without changing much of the code
        """

        self.reddit_client: asyncpraw.Reddit = reddit_client
        self.posts_handler: PostsManager = posts_handler

        self.fetch_limit: int = configs["FETCH_LIMIT"]
        self.media_match_regex: str = configs["MEDIA_MATCH_REGEX"]

    def is_media_url(self: RedditClient, post_url: str) -> bool:
        """Returns true in the case the url is pointing to a media file"""
        return bool(re.match(self.media_match_regex, post_url))

    def is_valid(
            self: RedditClient,
            submission: asyncpraw.models.Submission,
            nsfw: bool
    ) -> bool:
        """
        Returns True, only when all the conditions are met: \n
        - `nsfw` needs to be true if submission is NSFW
        - has not already been sent in a server; is a `new` submission
        - contains a URL that points to a media file
        - is not a pinned post in the subreddit

        :param submission: The submission object to be tested
        :param nsfw: If the post/URL can be NSFW or not

        :return: True if all conditions are met, otherwise False
        """

        nsfw_validated: bool = (not submission.over_18) or nsfw
        is_new: bool = self.posts_handler.is_new_post(submission.id)

        return (
                is_new and
                nsfw_validated and
                self.is_media_url(submission.url) and
                not submission.stickied
        )

    async def fetch_matching_urls(
            self: RedditClient,
            subreddit_name: str,
            nsfw: bool,
            count: int
    ) -> list[str] | None:
        """
        Fetches a list of matching URLs,
        and also adds the post ID to the handler

        :param subreddit_name: The name of the subreddit
        :param nsfw: If the post/URL can be NSFW or not
        :param count: The number of matching URLs to be fetched

        :return: Either a list of URLs meeting the requirements,
        or None if nothing was fetched

        :raises asyncprawcore.exceptions.Redirect: If the subreddit is
        non-existent or wasn't fetched properly
        """

        matched_urls: list[str | None] = []
        subreddit: asyncpraw.models.Subreddit = await (
            self.reddit_client.subreddit(subreddit_name)
        )

        submission: asyncpraw.models.Submission
        async for submission in subreddit.hot(limit=self.fetch_limit):
            if self.is_valid(submission, nsfw):
                self.posts_handler.add_post_id(submission.id)
                matched_urls.append(submission.url)

                if len(matched_urls) >= count:
                    return matched_urls

        return matched_urls or None
