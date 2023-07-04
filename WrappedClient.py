import numpy as np
from client import Client

class WrappeedClient:
    """This class is just a wrapper around client.py to make it suitable for multi-value
        data.
    """
    def __init__(self, M, privacy_levels, selected_level,report_limit):
        """Initialize the wrapper client.

        Args:
            M (int): Number of bits of data which is also number of required clients.
            privacy_levels (float[]): An array of all levels of privacy.
            selected_level (int): An index of privacy_levels array which is indicating 
                selected level of privacy for this client.
        """
        self.M = M
        self.privacy_levels = privacy_levels
        self.selected_level = selected_level
        self.epsilon = privacy_levels[selected_level]
        self.global_eps = report_limit * self.epsilon
        self.clients = [Client(self.privacy_levels,self.selected_level, report_limit)\
                         for i in range(M)]
        self.changes = 0
        self.prev_value = -1
        self.budget_usage = 0

    def report(self, value):
        """Get the multivalued 'value' and break it down to give each bit to corresponding
            client and manage clients to report each bit.
            At end, it also combine the values from clients and return a single perturbed data.

        Args:
            value (int): The value which is considered an integer here.

        Returns:
            [int[], int[]]: Returns 2 arrays where first one is representing each bit of 
                reported data by client and second array contains the height of each reported bit.
        """
        if value != self.prev_value:
            self.changes+=1
        self.prev_value = value
        binary_representation = f'{value:0{self.M}b}'
        characterized = [c for c in binary_representation]
        all_v = []
        all_h = []
        is_budget_used = False
        for i in range(self.M):
            to_report = int(characterized[i])
            [v, h] = self.clients[i].report(to_report)
            all_v.append(v)
            all_h.append(h)
            is_budget_used = is_budget_used or self.clients[i].is_budget_used()
        if is_budget_used:
            self.budget_usage += self.epsilon
            if self.budget_usage >= self.global_eps:
                for client in self.clients:
                    client.budget_exhausted()
        return [all_v, all_h]
    def how_many_changes(self):
        """Returns number of changes in values.

        Returns:
            int: Number of changes till now.
        """
        return self.changes