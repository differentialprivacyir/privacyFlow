"""Client Implementation of Privacy Flow framework
"""
import math
import numpy as np

def leaf_nodes_per_tree(total_number_of_nodes):
    """Computes "a" values where a_i + 1 denotes the height of i'th tree and 
        2^(a_i) nodes are available in i'th tree.
    Also there is another relation:
        t = 2^(a_m_t) + ... + 2^(a_i) + 2^(a_1)
    where t is denoting time or number of reports gathered.


    Args:
        total_number_of_nodes (int): The total nodes available in all difference trees.

    Returns:
        int[]: a_i values
    """
    if total_number_of_nodes == 0:
        return []
    leaf_nodes_in_current_tree = math.floor(math.log2(total_number_of_nodes))
    remaning_nodes = total_number_of_nodes - math.pow(2, leaf_nodes_in_current_tree)
    return np.concatenate(([leaf_nodes_in_current_tree], leaf_nodes_per_tree(remaning_nodes)))


class Client:
    """Implements functionalities of Privacy Flow Client.
    """
    def __init__(self, privacy_levels, selected_level, report_limit):
        # A list for storing key nodes of difference trees:
        self.R = []
        # Keep the previous data of client to compute the difference.
        self.previous_value = 0
        # Keep track of time and number of reports.
        self.t = 0
        # Indicate the number of difference trees in the current time.
        self.m_t_1 = 0
        # List of all privacy levels
        self.privacy_levels = privacy_levels
        # Selected privacy level for this client.
        self.selected_level = selected_level
        # Selected epsiolon based on selected level.
        self.epsilon = self.privacy_levels[self.selected_level]
        # Stores number of changes in data for this client.
        self.changes = 0
        # The global epsilon which determines how many reports this client can participate in
        self.global_eps = report_limit * self.epsilon
        # The root level of last difference tree for this clien.t
        self.a_m_t = 0
        # Stores how many times we have consumed budget.
        self.count = 0
        # When there are other clients, we are in a parallel form and there is a parallel composition,
        #   This variable is true if budget is exhausted in parallel composition and so this client
        #   should never participate in reports anymore.
        self.budget_consumed = False
        # Determines if budget is used in last report or not.
        self.budget_used = False

    def calcualte_budget(self):
        """Returns the privacy budget for current calculation.
            You can replace it with a dynamic mechanism later.j


        Returns:
            Float: Current budget to be used.
        """
        if (self.count * self.epsilon) > self.global_eps or self.budget_consumed:
            return 0
        else:
            return self.epsilon


    def new_value(self, v):
        """Get the new value of the client and calculate new R array and a_mt.
        Also it updates previous values.

        Args:
            v (int): The value of new data
        """
        self.t = self.t + 1
        aArray = leaf_nodes_per_tree(self.t)
        aArray = aArray.astype(np.int64)
        previousR = self.R.copy()
        a_1 = aArray[0]
        self.a_m_t = aArray[len(aArray) - 1]
        self.R = [previousR[j] \
                    if j > self.a_m_t \
                    else np.sum(previousR[0:j]) + v - self.previous_value \
                    for j  in range(a_1 + 1)]
        if self.previous_value != v:
            self.changes+=1
        self.previous_value = v

    def select(self):
        """This is node selection strategy.
            Each node can report root of associated difference tree or the leaf node.
            NOTE: This function should be call after new_value function to make sure 
                    a_m_t is updated.

        Returns:
            [int, int]: The level of node to report and its value.
        """
        r_t = self.a_m_t
        h_t = np.random.randint(0, 2)
        if h_t >= 1:
            h_t = r_t
        else:
            h_t = 0
        return [self.R[h_t], h_t]

    def perturbation(self, v):
        """The perturbation mechanism.
            Having the new value of data, it will purturbe it and reports it either according to
            root node or leaf node.


        Args:
            v (int): The new value of data

        Returns:
           int: Either 1 or -1 is returned based on data changes and amount of budget usage.
        """
        rand = np.random.random()
        eps = self.calcualte_budget()
        if v == 0 or eps == 0:
            if rand < 0.5:
                return 1
            else:
                return -1
        else:
            self.count += 1
            self.budget_used = True
            set_to_one_p = 0.5 + (v/2) * ( (math.exp(eps) - 1) / \
                                (math.exp(eps) + 1) )
            if rand < set_to_one_p:
                return 1
            else:
                return -1
    def report(self, data):
        """Outer function which bundles internal functionalities.

        Args:
            data (int): The new value to report

        Returns:
            [int, int]: return both value and level of node respectively
        """
        self.new_value(data)
        [v, h] = self.select()
        v = self.perturbation(v)
        return [v, h]
    def how_many_changes(self):
        """In sparse dataset, data changes almost rarely.
            and here we return number of changes during reports.

        Returns:
            int: Number of times that data actually changed.
        """
        return self.changes
    def used_budget(self):
        """Returns the consumed budget for this bit.

        Returns:
            float: The consumed budget till now
        """
        return self.epsilon * self.count
    def budget_exhausted(self):
        """If budget is completely finished in parallel composition, you should call this function
            to avoid client from participating in next report.
        """
        self.budget_consumed = True
    def is_budget_used(self):
        """Determines if budget is used in last report and also reset indicator for next report

        Returns:
            bool: True if budget is used in last report and false otherwise
        """
        result = self.budget_used
        self.budget_used = False
        return result
