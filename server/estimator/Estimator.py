import json
import mmh3 
import numpy as np
from Server import Server


class WrappedServer:
    def __init__(self, M, epsilon):
        self.M = M
        self.epsilon = epsilon
        self.Servers = [Server(epsilon) for i in range(M)]

    def newValue(self, v, h, m):
        self.Servers[m].newValue(v, h)

    def predicate(self):
        for server in self.Servers:
            server.predicate()
    
    def finish(self):
        toDetermineShape = self.Servers[0].finish()
        result = np.zeros([len(toDetermineShape), self.M])
        for index, server in enumerate(self.Servers):
            result[:, index] = server.finish()
        return result[1:]