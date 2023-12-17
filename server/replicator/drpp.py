"""This module implements Data Recycle with Personalized Privacy (DRPP)
"""
from server.replicator.dr import DR


class DRPP:
    """This class implements DRPP algorithm.
    """

    def __init__(self, data, levels):
        """Initialize the DRPP module

        Args:
            data ({eps: [{userID: id, value: {v: val, h: heights}}, ...]}): Contains a dictionary of
                privacy budget where each privacy budget is a list of users and values which
                are selected that level. 

            levels (float[]): The array of privacy budgets which denotes available levels.
        """
        self.data = data
        self.recycle_module = DR(levels)
        self.private_version_set = {}
        for eps in self.data:
            for element in self.data[eps]:
                self.private_version_set[element['userID']] = {
                    eps: element['value']
                }

    def recycle(self, target_level):
        """derives level-dp version from data of users with looser privacy
             requirements

        Args:
            level (float): The target level to expand it.
        """
        expanded_group = self.data[target_level].copy()
        replicated_group = []
        for level in self.data:
            if level > target_level:
                for user in self.data[level]:
                    derived_version = self.recycle_module.derive(
                        self.private_version_set[user['userID']], target_level)
                    self.private_version_set[user['userID']][target_level] = derived_version
                    expanded_group.append(
                        {'userID': user['userID'], 'value': derived_version})
                    replicated_group.append({'userID': user['userID'], 'value': derived_version})
        return expanded_group, replicated_group
