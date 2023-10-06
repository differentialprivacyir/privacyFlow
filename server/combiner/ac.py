"""
    Implements Advanced Combination (AC) Algorithms
"""
import math
import numpy as np


class AC:
    """
        This class
    """

    def __init__(self, estimations, privacy_levels, population):
        # Contains estimated histograms. It should be a 2D numpy array.
        # E.g. if we have 4 category and 5 leve then it is a 5 * 4 matrix
        self.estimations = np.array(estimations)
        # Contains array of levels. For example: [0.1, 0.3, 0.6, 0.9, 1]
        self.privacy_levels = privacy_levels
        # Contains the number of users in each level: [300, 400, 200, 100, 50]
        self.population = population

    def weighted_estimate(self, level_index):
        """
            Computes the estimation at given level using combining that level
                and all upper levels
        """
        weights = self.compute_weights(level_index)
        npweights = np.array(weights)
        # print("estimations are", self.estimations)
        result = np.sum(npweights[:, np.newaxis] * self.estimations, axis=0)
        # print("result is:", result)
        return result

    def compute_weights(self, level_index):
        """
            Computes an array of weight to use with weighted
                summation/estimation.
        """
        weights = [0] * len(self.privacy_levels)
        main_weight = [0] * len(self.privacy_levels)
        # Compute the size of population at replicated level:
        sum_of_users_at_last_allowed_level = 0
        for i in range(len(self.privacy_levels) - level_index):
            sum_of_users_at_last_allowed_level += self.population[len(self.privacy_levels) - i - 1]
        # Compute main weights which are weights without any normalization.
        for i in range(level_index + 1):
            eps = self.privacy_levels[i]
            n = self.population[i]
            k = len(self.estimations[i])
            if i == level_index:
                n = sum_of_users_at_last_allowed_level
            main_weight[i] = n / (1 - np.sum(self.estimations[i] ** 2 +
                                          k/(math.exp(eps/2) + math.exp(-eps/2) - 2)))
        # Apply normalization on each weight:
        denominator = np.sum(main_weight)
        for i in range(level_index + 1):
            weights[i] = main_weight[i] / denominator
            if weights[i] < 0:
                print(weights)
                raise ValueError('Error! Negative weight detected')
        return weights
