"""This module implements Data Recycle by Sampling (DRS)
"""
import numpy as np
import math


class DRS:
    """This class implements DRS algorithm.
    """

    def __init__(self, data, levels):
        """Initialize the DRS module

        Args:
            data ({eps: [{userID: id, value: {v: val, h: heights}}, ...]}): Contains a dictionary of
                privacy budget where each privacy budget is a list of users and values which
                are selected that level. 

            levels (float[]): The array of privacy budgets which denotes available levels.
        """
        self.data = data
        self.sampledData = {}
        for eps in self.data:
            sampledData[eps] = np.array([])

    def recycle(self, target_level):
        """derives level-dp version from data of users with looser privacy
             requirements

        Args:
            level (float): The target level to expand it.
        """

        expanded_group = self.data[target_level].copy()
        if self.sampledData[target_level].size != 0:
            # We already runned this algorithm for this target_level:
            return expanded_group + self.sampledData[target_level].tolist(), self.sampledData[target_level].tolist()

        sampledGroup = np.array([])
        for level in self.data:
            if level > target_level:
                levelData = np.array(self.data[level])
                sampleSize = math.floor(target_level/level * len(self.data[level]))
                sampledDataAtThisLevel = np.random.choice(levelData, sampleSize, replace=False)
                sampledGroup = np.concatenate(sampledGroup, sampledDataAtThisLevel)
        self.sampledData[target_level]
        return expanded_group + self.sampledData[target_level].tolist(), self.sampledData[target_level].tolist()

