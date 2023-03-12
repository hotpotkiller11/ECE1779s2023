import hashlib
import requests
import math

def get_hash(key: str) -> bytes:
    h = hashlib.md5(key.encode('utf-8')).hexdigest()
    return h


class CacheController:
    """ CacheController class provide an object that manage all 
        memcache nodes as a whole. Provides method to communicate 
        with certain memcache node or broadcast configuration
        modification. 
        
        Fixed 16 partitions (16 nodes)
    """

    memcache_nodes = [] # Nodes (activated + not activated)
    pool_size = 0 # Activated node count
    partition_dict = {} # used to map partition with memcache nodes

    def __init__(self, memcache_servers):
        """ Create a new Cache Controller instance with a list of memcache node
            servers.

        Args:
            memcache_servers (list[str]): list of addresses of the memcache node
        """
        assert(len(memcache_servers) > 0)
        self.memcache_nodes = memcache_servers# IPs
        self.pool_size = 1
        # 16 partitions all map to the same node
        for i in range(16):
            self.partition_dict[hex(i)[2:]] = memcache_servers[0]
        for node in memcache_servers:
            requests.post(node + "/clear") # Clear all servers at start

    def activated_nodes(self) -> list:
        """ Get a list of all activated nodes

        Returns:
            list[str]: activated nodes
        """
        return self.memcache_nodes[0:self.pool_size]
    
    def not_activated_nodes(self) -> list:
        """ Get a list of all not activated nodes

        Returns:
            list[str]: not activated nodes
        """
        return self.memcache_nodes[self.pool_size: len(self.memcache_nodes)]

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
        if size > len(self.memcache_nodes): raise ValueError("Size must smaller or equal to pool size (%d)" % (self.pool_size))
        if size == self.pool_size: return # No modification
        self.pool_size = size
        new_partition_dict = {}
        # generate new partition dict
        for i in range(16):
            new_partition_dict[hex(i)[2:]] = self.memcache_nodes[i % size]

        # Find nodes that has lost any partition (they need to convey some files to new place)
        shrunk_nodes = []
        for i in range(16):
            node = self.partition_dict[hex(i)[2:]]
            if node != new_partition_dict[hex(i)[2:]] and node not in shrunk_nodes:
                shrunk_nodes.append(self.partition_dict[hex(i)[2:]])
        
        # Update the partition dict
        self.partition_dict = new_partition_dict
        send_dict_list = [] # a list of send dict, each original node will have a dict to send
        
        for node in shrunk_nodes:
            res = requests.post(node + "/get/all")
            files = res.json() # list of all files (contains key, file and timestamp)
            drop_list = []
            send_dict = {} # dictionary that defines files and its new storing node destination
            # Find files and its new destination
            for file in files:
                file_node = self.get_node(file["key"])
                if file_node != node: 
                    drop_list.append(file["key"]) # file to drop
                    if file_node not in send_dict.keys():
                        send_dict[file_node] = [file] # a list of file
                    else:
                        send_dict[file_node].append(file)
            # prepare to send files to its new destination
            send_dict_list.append(send_dict)
            
            # Remove conveyed files from original node
            if node in self.not_activated_nodes():
                res = requests.post(node + "/clear")
                if res.status_code != 200: print("Node clear failed (%s)" % (node))
            else:
                res = requests.post(node + "/drop", json = {"keys": drop_list})
                
        for send_dict in send_dict_list:
            for new_node in send_dict.keys():
                    res = requests.post(new_node + "/put/list", json = send_dict[new_node])
                    if res.status_code != 200: print("File transition filed (%s)" % (new_node))
