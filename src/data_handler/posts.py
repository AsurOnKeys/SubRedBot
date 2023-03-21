from __future__ import annotations


class PostsManager:
    """
    A class that implements a wacky method to store the Post IDs of
    already sent submissions, it uses a list (as a queue) and stores sets
    inside of it (faster searching)
    After a set reaches its `size_cap`, it is removed, this causes the oldest
    posts to be removed, easily retaining the newer posts without having to
    use OrderedSets
    """

    def __init__(self: PostsManager, **configs: str | int) -> None:
        """
        The class constructor

        :param configs: All configs can be passed for ease of use,
        and so I can add many more later without changing much of the code
        """

        self.size_cap: int = configs["SET_SIZE_CAP"]
        self.queue: list[set[str | None]] = [
            set() for _ in range(configs["QUEUE_SIZE_CAP"])
        ]

    @property
    def fetch_free_set(self: PostsManager) -> set[str | None]:
        """Returns the first set that has not reached the `size_cap` yet"""

        post_id_set: set[str | None]
        for post_id_set in self.queue:
            if len(post_id_set) < self.size_cap:
                return post_id_set

        # Since the queue is shifted, the last set is empty and ready to use
        self.shift_queue()
        return self.queue[-1]

    def shift_queue(self: PostsManager) -> None:
        """Simply dequeues the oldest set, and enqueues a new one"""
        self.queue.pop(0)
        self.queue.append(set())

    def add_post_id(self: PostsManager, post_id: str) -> None:
        self.fetch_free_set.add(post_id)

    def is_new_post(self: PostsManager, post_id: str) -> bool:
        """Returns true if no set contains the post ID"""
        return all(post_id not in post_id_set for post_id_set in self.queue)
