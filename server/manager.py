"""This is main entrypoint to run server side of Privacy Flow algorithm which combines both
    Estimator and Replicator and Combiner Algorithms.
"""
from typing import List
import numpy as np
from server.replicator.drpp import DRPP
from server.combiner.ac import AC
from server.estimator.estimator import WrappedServer


class PrivacyFlow:
    """This class is responsible for managing different modules of server.
    """

    def __init__(self, data, levels, M):
        """Initialize underlying modules

        Args:
            data ({eps: [{userID: id, value: {v: int[], h: int[]}}, ...]}): Contains a dictionary of
                privacy budget where each privacy budget is a list of users and values which
                are selected that leve.
            levels (float[]): The array of privacy budgets which denotes available levels.
        """
        if data:
            raise ValueError('Error! `data` is not supported in constructor \
                anymore, please use `new_data_set` function')
        self.data = data
        if levels != sorted(levels):
            raise ValueError('Error! Level array should be sorted in order\
                 to consider a mapping between each level and its position.')
        self.levels: List[float] = levels
        # Prepare main servers which works with data of original users at that level.
        self.servers:List[WrappedServer] = [WrappedServer(M, lvl) for lvl in self.levels]
        # Prepare replicatd servers which works with both replicated data and original data all thw way along.
        self.replicatorServers: List[WrappedServer] = [WrappedServer(M, lvl) for lvl in self.levels]
        # self.replicatorServers = self.replicatorServers[1:]
        # self.replication = DRPP(self.data, self.levels)
        self.replication = None

    def new_data_set(self, data):
        """Get the data of new round and report it to underlying servers.

        Args:
            data ({eps: [{userID: id, value: {v: int[], h: int[]}}, ...]}): Contains a dictionary of
                privacy budget where each privacy budget is a list of users and values which
                are selected that leve. val is an array of 1 or -1 values
        """
        self.data = data
        for lvl in self.data:
            for user in self.data[lvl]:
                for index,_ in enumerate(user['value']['v']):
                    self.servers[self.levels.index(lvl)].new_value(\
                                user['value']['v'][index], user['value']['h'][index], index, False)
        # Prepare replication module:
        self.replication = DRPP(self.data, self.levels)
        # We works with replicatedServers without activating replica but introducing the replicated
        #   data as original data becuase we are going to always use the replication data.
        for lvl in self.data:
            expanded_group_data, _ = self.replication.recycle(lvl)
            for user in expanded_group_data:
                for index,_ in enumerate(user['value']['v']):
                    self.replicatorServers[self.levels.index(lvl)].new_value(\
                                user['value']['v'][index], user['value']['h'][index], index, False)

    def estimate(self, l):
        """Computes the result at given level.

        Args:
            l (float): The budget of level
        """
        level = self.levels.index(l)
        estimation_at_level = self.replicatorServers[level].predicate(False)
        estimations = []
        for lvl in self.data:
            if lvl < l:
                estimations.append(self.servers[self.levels.index(lvl)].predicate(False))
        estimations.append(estimation_at_level)
        # Fix estimations length:
        for _ in range(len(self.levels) - len(estimations)):
            estimations.append(np.array([0 for i in estimation_at_level]))
        population = [len(self.data[lvl]) for lvl in self.data]
        # print(estimations)
        ac = AC(estimations, self.levels, population)
        level_index = level
        if level_index is None:
            raise ValueError('Error! Unable to find index of level')
        # print(level, level_index, self.levels)
        answer = ac.weighted_estimate(level_index)
        return answer
    def next_round(self):
        """Annotate next round to underlying servers.
        """
        for server in self.servers:
            server.predicate(True)
        for server in self.replicatorServers:
            server.predicate(True)
    def finish(self):
        """Get all recorded frequencies from server and return them to client.

        Returns:
            {eps: float[][]}: Returns etimated frequencies 
                                for each bit at each level and in each round.
        """
        raise ValueError('Under Construction! Replicating and combination is not done for estimations of different level.')
        result = {}
        for index in enumerate(self.levels):
            result[self.levels[index]] = self.servers[index].finish()
        return result
        