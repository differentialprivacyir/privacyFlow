"""Contains test of Privacy Flow algorithm and result evaluation for it.
"""
import math
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import numpy as np
import pandas as pd
from server.manager import PrivacyFlow
from WrappedClient import WrappeedClient
from time import time
from datetime import datetime

#Overal Algorithm Execution Rounds:
OAER = 1
# Number of rounds to run the code:
ROUND_CHANGES = 20
# Privacy Budget Levels:
# levels = [(i+1)/10 for i in range(0, 10)]
levels = [0.1, 0.5, 1, 5, 10]
averageMSE = [[0] * ROUND_CHANGES for i in levels]
averageMAE = [[0] * ROUND_CHANGES for i in levels]
averageME = [[0] * ROUND_CHANGES for i in levels]

for oaer in range(OAER):
    print(f'Start of round {oaer} at:', datetime.now())
    # Number of users:
    N = 10000
    # Determines how many different value types are available in dataset: 
    # (Each bit is responsible for a separate value)
    DATA_SET_SIZE = 8
    # Creates data for each client:
    # dataSet = [[i for i in np.random.randint(2 ** DATA_SET_SIZE - 1, size=N)]]
    # dataSet = [[math.floor(i) for i in np.random.normal(100, 10, size=N)]]
    # Read dataset from file:
    csvContent = pd.read_csv('./hpcDatasets/normalMu=150Sigma=50N=10kR=20.csv')
    dataSet = np.transpose(csvContent.to_numpy())
    # Determine selected privacy level of each client:
    # clientSelectedLevel = np.random.randint(len(levels), size=N)
    clientSelectedLevel = [0] * 2000 + [1] * 2000 + [2] * 2000 + [3] * 2000 + [4] * 2000
    # Creates actual clients:
    clients = [WrappeedClient(DATA_SET_SIZE, levels, clientSelectedLevel[i], ROUND_CHANGES) for i in range(N)]
    # Initialize Server:
    server = PrivacyFlow(None, levels, DATA_SET_SIZE)
    # Prepare to keep results of estimations:
    estimations = []

    startRoundTime = time()
    
    # Start the test
    for i in range(ROUND_CHANGES):
        print(f'round {i} started')
        startTimestamp = time()
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

        endTimestamp = time()
        print(f'Clients reported at {(endTimestamp-startTimestamp)/60} minutes')
        startTimestamp = time()
        # Give the results to the server:
        server.new_data_set(serverData)
        # Call this method if you want to get estimation of data:
        estimations.append([])
        for l in levels:
            estimations[i].append(server.estimate(l))
        # Always call this method when you are going to the next round:
        server.next_round()
        endTimestamp = time()
        print(f'Server estimated at {(endTimestamp-startTimestamp)/60} minutes')
        startTimestamp = time()

    endRoundTime = time()
    print(f'Round took {(endRoundTime - startRoundTime) / 60} minutes.')
    # print(server.finish())
    # Compute bit frequency of real values:
    frequencies = []
    for singleRound in dataSet:
        bitRepresentationOfDataSet = [bin(i)[2:].zfill(DATA_SET_SIZE) for i in singleRound]
        numericalBitRepresentationDataSet = [[int(char) for char in list(data)] \
                                            for data in bitRepresentationOfDataSet]
        frequencies.append(np.sum(numericalBitRepresentationDataSet, axis=0))
    normalized = np.array(frequencies) / N

    # Evaluate mean error:
    for r in range(ROUND_CHANGES):
        print(f'\n\n\n ========================================== \nResults of Round {r}:\n==========================================')
        error = []
        for index, estimation in enumerate(estimations[r]):
            print(f'Evaluation for level eps = {levels[index]}')
            for i, _ in enumerate(normalized[r]):  # calculating errors
                error.append(abs(estimation[i] - normalized[r][i]) * 100)
                print("index:", i, "-> Estimated:", estimation[i], " Real:", normalized[r][i], " Error: %", int(error[-1]))
            print("Global Mean Square Error:", mean_squared_error(normalized[r], estimation))
            print("Global Mean Absolute Error:", mean_absolute_error(normalized[r], estimation))
            averageMSE[index][r] = (averageMSE[index][r] * r + mean_squared_error(normalized[r], estimation))/(r+1)
            averageMAE[index][r] = (averageMAE[index][r] * r + mean_absolute_error(normalized[r], estimation))/(r+1)
            


    meanOfRounds = np.mean(dataSet, axis=1)
    print('Real Mean of rounds is:', meanOfRounds)
    outputMean = []
    for r in range(ROUND_CHANGES):
        outputMean.append([])
        for index, estimationAtL in enumerate(estimations[r]):
            ROUND_MEAN = 0
            REAL_ROUND_MEAN = 0
            for index2, number in enumerate(estimationAtL):
                ROUND_MEAN += (number*(N) * 2 ** (len(estimationAtL) - 1 - index2))
                REAL_ROUND_MEAN += (normalized[r][index2]*(N) * 2 ** (len(estimationAtL) - 1 - index2))
            ROUND_MEAN /= N
            REAL_ROUND_MEAN /= N
            print(f'Mean Difference at round {r} and level {levels[index]}:', abs(ROUND_MEAN - meanOfRounds[r]), abs(meanOfRounds[r] - REAL_ROUND_MEAN))
            averageME[index][r] = (averageME[index][r] * r + abs(ROUND_MEAN - meanOfRounds[r]))/(r+1)
            outputMean[r].append(ROUND_MEAN)
    print("Estimated Mean is:", outputMean)

print("Results for Averaged MSE:", averageMSE)
print("Results for Averaged MAE:", averageMAE)
print("Results for Averaged ME:", averageME)