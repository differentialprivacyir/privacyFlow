"""Frequency Estimator per Bit for Continual Reports
 """
import math
import numpy as np 


class Server:
    """This class estimates frequency of a single bit.
    """
    def __init__(self, epsilon):
        self.epsilon = epsilon
        self.coef = (1 + math.exp(self.epsilon))/(math.exp(self.epsilon) - 1)
        self.sum_v_of1 = 0
        self.sum_of_users_of1 = 0
        self.sum_v_ofh = 0
        self.sum_of_users_ofh = 0
        self.replica_sum_v_of1 = 0
        self.replica_sum_of_users_of1 = 0
        self.replica_sum_v_ofh = 0
        self.replica_sum_of_users_ofh = 0
        self.f1 = 0
        self.f2 = 0
        self.f = [0]
        self.variance_f = [0]
        self.t = 0
        self.last_root = 0
        self.replica_last_root = 0
        self.replica_activated = False

    def new_value(self, v, h):
        """Get values of clients and after callibrating them, it will store their value.

        Args:
            v (int): The value of client's report which is either 1 of -1
            h (int): The height of estimation.
        """
        callibrated_v = v * self.coef
        self.last_root = max(self.last_root, h)
        if h == 0:
            self.sum_of_users_of1 += 1
            self.sum_v_of1 += callibrated_v
        else:
            self.sum_of_users_ofh += 1
            self.sum_v_ofh += callibrated_v
        
    def replica_new_value(self, v, h):
        """Get replicated values of clients and after callibrating them, it will store their value.

        Args:
            v (int): The value of replicated client's report which is either 1 of -1
            h (int): The height of replicated estimation.
        """
        callibrated_v = v * self.coef
        self.replica_last_root = max(self.replica_last_root, h)
        if h == 0:
            self.replica_sum_of_users_of1 += 1
            self.replica_sum_v_of1 += callibrated_v
        else:
            self.replica_sum_of_users_ofh += 1
            self.replica_sum_v_ofh += callibrated_v

    def activate_replica(self):
        """Activate replica values so they are considered as value when 
            estimating results
        """
        self.sum_of_users_of1 += self.replica_sum_of_users_of1
        self.sum_v_of1 += self.replica_sum_v_of1
        self.sum_of_users_ofh += self.replica_sum_of_users_ofh
        self.sum_v_ofh += self.replica_sum_v_ofh
        temp = self.last_root
        self.last_root = self.replica_last_root
        self.replica_last_root = temp
        self.replica_activated = True

    def deactivate_replica(self):
        """Deactivate replica values so they are ignored when estimating results.
        """
        self.sum_of_users_of1 -= self.replica_sum_of_users_of1
        self.sum_v_of1 -= self.replica_sum_v_of1
        self.sum_of_users_ofh -= self.replica_sum_of_users_ofh
        self.sum_v_ofh -= self.replica_sum_v_ofh
        self.replica_sum_of_users_of1 = 0
        self.replica_sum_of_users_ofh = 0
        self.replica_sum_v_of1 = 0
        self.replica_sum_v_ofh = 0
        temp = self.last_root
        self.last_root = self.replica_last_root
        self.replica_last_root = temp
        self.replica_activated = False


    def variance_f1(self):
        """Computes varience of f1 which varience of users who are reporting leaf node.

        Returns:
            float: The varience of users who are reporting leaf node.
        """
        var_f1 = self.variance_f[len(self.variance_f) - 1] + \
                (((math.exp(self.epsilon) + 1)/(math.exp(self.epsilon) - 1))**2) / \
                    self.sum_of_users_of1
        return var_f1

    def variance_f2(self):
        """Computes varience of fw which varience of users who are reporting root node.

        Returns:
            float: The varience of users who are reporting root node.
        """
        t_prime = self.t - 2**self.last_root
        var_f2 = self.variance_f[t_prime] + \
                (((math.exp(self.epsilon) + 1)/(math.exp(self.epsilon) - 1)) ** 2) / \
                    self.sum_of_users_ofh
        return var_f2
    def compute_variance(self):
        """Computes varience of frequencies according to varience of f1 and f2

        Returns:
            float: The varience of frequency.
        """
        if self.t % 2 == 0:
            vf1 = self.variance_f1()
            vf2 = self.variance_f2()
            return (vf1 * vf2)/(vf1 + vf2)
        else:
            return self.variance_f[len(self.variance_f) - 1] + \
                    (((math.exp(self.epsilon) + 1)/(math.exp(self.epsilon) - 1)) ** 2) / \
                        self.sum_of_users_of1
    def compute_w1(self):
        """Computes w1 weight.

        Returns:
            float: weight of frequency
        """
        varf1 = self.variance_f1()
        return math.pow(varf1, -1)
    def compute_w2(self):
        """Computes w2 weight.

        Returns:
            float: weight of frequency
        """
        varf2 = self.variance_f2()
        return math.pow(varf2, -1)
    def compute_w(self):
        """Computes weight of frequency of users who are reporting leaf node.

        Returns:
            float: weight of frequency
        """
        w1 = self.compute_w1()
        w2 = self.compute_w2()
        return w1/(w1 + w2)
    def predicate(self):
        """Predicate frequency of this bit.
        """
        self.t += 1
        if self.t % 2 == 0:
            self.f1 = self.f[len(self.f) - 1] + \
                        (self.sum_v_of1 / self.sum_of_users_of1)
            t_prime = self.t - 2**self.last_root
            self.f2 = self.f[t_prime] + \
                        (self.sum_v_ofh / self.sum_of_users_ofh)
        else:
            self.f1 = self.f2 = self.f[len(self.f) - 1] + \
                        (self.sum_v_of1 / self.sum_of_users_of1)
        if self.t % 2 == 0:
            w = self.compute_w()
        else:
            w = 0.5 #Just to neutralize its effect.
        freq = w * self.f1 + (1 - w) * self.f2
        self.t -= 1
        return np.clip(freq, 0, 1)
        # self.f.append(freq)
        # varF = self.compute_variance()
        # self.variance_f.append(varF)
        #Reset state of server.
        # self.sum_v_of1 = 0
        # self.sum_of_users_of1 = 0
        # self.sum_v_ofh = 0
        # self.sum_of_users_ofh = 0

    def go_to_next_round(self):
        """Predicate frequency of this bit.
        """
        if self.replica_activated:
            raise ValueError('Error! Replica should be deactive to go to next round!')
        self.t += 1
        if self.t % 2 == 0:
            self.f1 = self.f[len(self.f) - 1] + \
                        (self.sum_v_of1 / self.sum_of_users_of1)
            t_prime = self.t - 2**self.last_root
            self.f2 = self.f[t_prime] + \
                        (self.sum_v_ofh / self.sum_of_users_ofh)
        else:
            self.f1 = self.f2 = self.f[len(self.f) - 1] + \
                        (self.sum_v_of1 / self.sum_of_users_of1)
        if self.t % 2 == 0:
            w = self.compute_w()
        else:
            w = 0.5 #Just to neutralize its effect.
        freq = w * self.f1 + (1 - w) * self.f2
        self.f.append(freq)
        varF = self.compute_variance()
        self.variance_f.append(varF)
        #Reset state of server.
        self.sum_v_of1 = 0
        self.sum_of_users_of1 = 0
        self.sum_v_ofh = 0
        self.sum_of_users_ofh = 0
        return np.clip(freq, 0, 1)

    def get_estimations(self):
        """Since data should be between -1 and 1, it truncates the data and return the value.

        Returns:
            float[]: final frequency of this bit.
        """
        result = np.clip(self.f, 0, 1)
        return result

    def finish(self):
        """Since data should be between -1 and 1, it truncates the data and return the value.

        Returns:
            float[]: final frequency of this bit.
        """
        self.f = np.clip(self.f, 0, 1)
        return self.f 