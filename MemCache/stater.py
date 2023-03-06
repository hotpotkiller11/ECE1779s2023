class Stater:
    def __init__(self):
        self.miss = 0  # total request number to be added during run time
        self.hit = 0
        self.reqs = 0 # within one minute

        self.total_reqs = 0     #   number of requests served per minute
        self.total_miss = 0
        self.total_hit = 0

        self.stat_list = []     #   list of tuple in the format (miss or hit str, timestamp)

        self.items_in_cache = 0
        self.size_in_cache = 0
        """miss rate,
            hit rate,
            number of items in cache,
            total size of items in cache,
            number of requests served per minute."""

