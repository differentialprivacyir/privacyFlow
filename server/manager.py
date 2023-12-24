"""This is main entrypoint to run server side of Privacy Flow algorithm which combines both
    Estimator and Replicator and Combiner Algorithms.
"""
from typing import List
import numpy as np
from server.replicator.drs import DRS
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
        self.servers:List[WrappedServer] = [WrappedServer(M, lvl) for lvl in self.levels]

        # self.replication = DRS(self.data, self.levels)
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

        self.replication = DRS(self.data, self.levels)

    def estimate(self, l):
        """Computes the result at given level.

        Args:
            l (float): The budget of level
        """
        level = self.levels.index(l)
        _, replicated_group_data = self.replication.recycle(l)
        for user in replicated_group_data:
            for index,_ in enumerate(user['value']['v']):
                self.servers[level].new_value(user['value']['v'][index],\
                                                user['value']['h'][index], index, True, user['eps'])
        self.servers[level].replica_activasion(True)
        estimation_at_level = self.servers[level].predicate(False)
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
        self.servers[level].replica_activasion(False)
        return answer
    def next_round(self):
        """Annotate next round to underlying servers.
        """
        for server in self.servers:
            server.predicate(True)
    def finish(self):
        """Get all recorded frequencies from server and return them to client.

        Returns:
            {eps: float[][]}: Returns etimated frequencies 
                                for each bit at each level and in each round.
        """
        result = {}
        for index in enumerate(self.levels):
            result[self.levels[index]] = self.servers[index].finish()
        return result
        