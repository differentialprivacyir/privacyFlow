"""
Implements Data Recycle (DR) Algorithm
"""
import math
import numpy as np


class DR:
    """
    DR Class
    """

    def __init__(self, levels):
        self.levels = levels

    def compute_q(self, level):
        """Computes q value which is a specific value in DR Algorithm.

        Args:
            level (int): The desired level to compute q value for it.

        Returns:
            float: Computed q value
        """
        numerator = math.exp(level/2) - 1
        denominator = math.exp(level/2) + 1
        return numerator / denominator

    def compute_fg(self, q_s, q_target, q_i, version):
        """Computes f1, g1 if version is set to 1 and compute f2, g2 if
           version is set to 2

        Args:
            q_s (float): Computed q_s value
            q_target (float): Computed q_target value
            q_i (float): Computed q_i value.
            version (int): Specify required version of f and g

        Raises:
            ValueError: Version is neither 1 not 2.

        Returns:
            float, float: Specified version of f and g respectively.
        """
        if version == 1:
            f_1 = q_target/q_s
            g_1 = ((q_s - q_target) / q_s) * \
                (1 - (1-q_i / q_target) / (q_i / q_s + 1))
            return f_1, g_1
        if version == 2:
            f_2 = (q_target - q_i) / (q_s - q_i)
            g_2 = (q_i * (q_s - q_target)) / (q_target * (q_s - q_i))
            return f_2, g_2
        raise ValueError(f'Type should be 1 or 2: {version}')

    def derive(self, private_version_set, target_level):
        """Gets a private version set of current user and try to produce
            another version at target leve.

        Args:
            private_version_set (dict): The set of all derived versions for
            this user which are key-value in shape of level(int)-data(obj).
            target_level (int): The target level to produce new version at it.

        Raises:
            ValueError: If there is an undefined level in given private
                        version set.
        """
        infimum = {
            'level': None,
            'value': {
                'v': [],
                'h': []
            }
        }
        supremum = {
            'level': None,
            'value': {
                'v': [],
                'h': []
            }
        }
        for level in private_version_set:
            if level not in self.levels:
                raise ValueError(
                    f'Not defined level in private version set: {level}')
            if level >= target_level and (infimum['level'] is None or level <= infimum['level']):
                infimum['level'] = level
                infimum['value'] = private_version_set[level]
            if level <= target_level and (supremum['level'] is None or level >= supremum['level']):
                supremum['level'] = level
                supremum['value'] = private_version_set[level]
        if infimum['level'] == supremum['level']:
            return private_version_set[target_level]
        z_sup = infimum['value']['v']
        z_inf = supremum['value']['v']

        derived_version = []
        q_target = self.compute_q(target_level)
        q_s = self.compute_q(infimum['level'])
        if supremum['level'] is None:
            threshold = (q_s + q_target) / (2 * q_s)
            for i in range(len(infimum['value']['v'])):
                p = np.random.random()
                if p <= threshold:
                    derived_version.append(z_sup[i])
                else:
                    derived_version.append(z_sup[i] * -1)
        else:
            q_i = self.compute_q(supremum['level'])
            f_1, g_1 = self.compute_fg(q_s, q_target, q_i, 1)
            threshold1 = (1 + f_1 + g_1) / 2
            f_2, g_2 = self.compute_fg(q_s, q_target, q_i, 2)
            threshold2 = (1 + f_2 - g_2) / 2
            for j in range(len(supremum['value']['v'])):
                if z_sup[j] == z_inf[j]:
                    p = np.random.random()
                    if p <= threshold1:
                        derived_version.append(z_sup[j])
                    else:
                        derived_version.append(z_sup[j] * -1)
                else:
                    p = np.random.random()
                    if p <= threshold2:
                        derived_version.append(z_sup[j])
                    else:
                        derived_version.append(z_inf[j])
        return {
            'h': infimum['value']['h'],
            'v': derived_version
        }
