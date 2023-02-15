import hashlib

def get_hash(key: str) -> bytes:
    return hashlib.md5(str.encode('utf-8')).hexdigest()

class CacheController:
    """ CacheController class provide an object that manage all 
        memcache nodes as a whole. Provides method to communicate 
        with certain memcache node or broadcast configuration
        modification. 
        
        Fixed 16 partitions (16 nodes)
    """

    memcache_nodes = []
    pool_size = 0
    partition_dict = {} # used to map partition with memcache nodes

    def __init__(self, memcache_servers: list[str]):
        """ Create a new Cache Controller instance with a list of memcache node
            servers.

        Args:
            memcache_servers (list[str]): list of addresses of the memcache node
        """
        assert(len(memcache_servers) > 0)
        self.memcache_nodes = memcache_servers
        self.pool_size = 1
        # 16 partitions all map to the same node
        for i in range(16):
            self.partition_dict[hex(i)[2:]] = memcache_servers[0]

    def activated_nodes(self) -> list[str]:
        """ Get a list of all activated nodes

        Returns:
            list[str]: activated nodes
        """
        return self.memcache_nodes[0:self.activated_nodes]

    def get_node(self, key: str) -> str:
        """ Get corresponding node address by key.

        Args:
            key (str): key

        Returns:
            str: the address of the corresponding node
        """
        h = get_hash(key)
        node = self.partition_dict[h[0]]
        return node
    
    def modify_pool_size(self, size: int):
        """ Modify the number of activating node, and convey data stored in 
            old nodes into newer ones.

        Args:
            size (int): new size of the activated nodes

        Raises:
            ValueError: size not 
        """
        if size <= 0: raise ValueError("Size must greater than 0")
        if size > size: raise ValueError("Size must smaller or equal to pool size (%d)" % (self.pool_size))
        self.pool_size = size
        new_partition_dict = {}
        # generate new partition dict
        for i in range(16):
            new_partition_dict[hex(i)[2:]] = self.memcache_nodes[i % size]
    
        for i in range(16):
            if new_partition_dict[hex(i)[2:]] != self.partition_dict[hex(i)[2:]]:
                # Notify node to convey data to new place
                pass
        
        # Update the partition dict
        self.partition_dict = new_partition_dict