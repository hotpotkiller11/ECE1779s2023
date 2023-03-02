class Stater:
    def __init__(self):
        self.miss = 0  # total request number to be added during run time
        self.hit = 0
        self.reqs = 0
        self.total_reqs = 0
        self.total_miss = 0
        self.total_hit = 0
        self.stat_list = []  # list of tuple in the format (miss or hit str, timestamp)

    
