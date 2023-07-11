"""This module encapsulate bit_estimator to provide a server for estimating multivalue
"""
import numpy as np
from server.estimator.bit_estimator import Server


class WrappedServer:
    """WrapperServer for bit_estimator servers which wrap them in order to provide
        support for multi-value estimations.
    """
    def __init__(self, M, epsilon):
        self.M = M
        self.epsilon = epsilon
        self.servers = [Server(epsilon) for i in range(M)]

    def new_value(self, v, h, m, replicated):
        """Transfer given value to corresponding bit_estimator

        Args:
            v (int): The reported value
            h (int): The height of reported value
            m (int): The position of this bit
            replicated (int): Determines if this is original value or a replicated one.
        """
        if replicated is False:
            self.servers[m].new_value(v, h)
        else:
            self.servers[m].replica_new_value(v, h)

    def predicate(self, go_next):
        """Predicate the current value and prepare servers for next round if called with true

        Args:
            go_next (bool): Should go to next round or not?
        """
        estimation = []
        if go_next is True:
            for server in self.servers:
                result = server.go_to_next_round()
                estimation.append(result)
        else:
            for server in self.servers:
                result = server.predicate()
                estimation.append(result)
        return estimation

    def finish(self):
        """Get the results from the underlying bit_estimators and reports the frequency of data
        

        Returns:
            float[][]: The estimation of each bit in each round.
        """
        to_determine_shape = self.servers[0].finish()
        result = np.zeros([len(to_determine_shape), self.M])
        for index, server in enumerate(self.servers):
            result[:, index] = server.finish()
        # The first row is initialized 0 values of f array inside underlying servers.
        return result[1:]
        