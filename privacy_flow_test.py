"""Contains test of Privacy Flow algorithm and result evaluation for it.
"""
from sklearn.metrics import mean_squared_error
import numpy as np
from server.manager import PrivacyFlow
from WrappedClient import WrappeedClient

# Number of users:
N = 128000
# Privacy Budget Levels:
levels = [(i+1)/10 for i in range(0, 10)]
# Determines how many different value types are available in dataset: 
# (Each bit is responsible for a separate value)
DATA_SET_SIZE = 8
# Creates data for each client:
dataSet = [[i for i in np.random.randint(2 ** DATA_SET_SIZE - 1, size=N)]]
# Determine selected privacy level of each client:
clientSelectedLevel = np.random.randint(len(levels), size=N)
# Creates actual clients:
clients = [WrappeedClient(levels, clientSelectedLevel[i]) for i in range(N)]
# Initialize Server:
server = PrivacyFlow(None, levels, DATA_SET_SIZE)
# Number of rounds to run the code:
ROUND_CHANGES = 1
# Prepare to keep results of estimations:
estimations = []
# Start the test
for i in range(ROUND_CHANGES):
    # Prepare server data:
    serverData = {i: [] for i in levels}
    for j in range(N):
        # Report the data by client:
        [allV, allH] = clients[j].report(dataSet[i][j])
        # Gather reports for server:
        serverData[levels[clientSelectedLevel[j]]].append({
            'userID': j,
            'value': {
                'v': allV,
                'h': allH
            }
        })
    # Give the results to the server:
    server.new_data_set(serverData)
    # Call this method if you want to get estimation of data:
    estimations.append([])
    for l in levels:
        estimations[0].append(server.estimate(l))
    # Always call this method when you are going to the next round:
    server.next_round()

# Compute bit frequency of real values:
bitRepresentationOfDataSet = [bin(i)[2:].zfill(DATA_SET_SIZE) for i in dataSet]
numericalBitRepresentationDataSet = [[int(char) for char in list(data)] \
                                        for data in bitRepresentationOfDataSet]
frequencies = np.sum(numericalBitRepresentationDataSet, axis=0)
normalized = frequencies / N

# Evaluate mean error:
error = []
for index, estimation in enumerate(estimations[0]):
    print(f'Evaluation for level eps = {levels[index]}') 
    for i, _ in enumerate(normalized):  # calculating errors
        error.append(abs(estimation[i] - normalized[i]) * 100)
        print("index:", i, "-> Estimated:", estimation[i], " Real:", normalized[i], " Error: %", int(error[-1]))
    print("Global Mean Square Error:", mean_squared_error(normalized, estimation))
