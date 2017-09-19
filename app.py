class Gate:
    def __init__(self, input1, input2, gate):
        self.gate = gate
        self.input1 = input1
        self.input2 = input2

    def __str__(self):
        return "Gate {}, Input1: {}, Input2: {}".format(self.gate, self.input1, self.input2)

import numpy as np
import random

inputArr = np.array(np.genfromtxt('input.csv', delimiter=', ', dtype='str'))
inputArr = [int(s, 16) for s in inputArr]
outputArr = np.array(np.genfromtxt('output.csv', delimiter=', ', dtype='str'))
outputArr = [int(s, 16) for s in outputArr]

# for i in range(len(inputArr)):
#     inputArr[i] = np.binary_repr(inputArr[i])
#     outputArr[i] = np.binary_repr(outputArr[i])

def generate():
    # gates = np.ndarray(shape=(5,6))
    gates = []
    for i in range(1):
        subGates = []
        for j in range(5):
            ggate = Gate(random.randint(0,4), random.randint(0,4), random.randint(0,4))
            subGates.append(ggate)
            print(ggate)

        gates.append(subGates)

    # return evaluateBits(gates)
    print("Correct ", evaluateBits(gates))

def evaluateBits(gates):
    correct = 0
    for k in range(len(inputArr)):
        logicGate = inputArr[k]
        for i in range(len(gates)):
            logicGateBit = 0
            for j in range(len(gates[i])):
                logicGateBit <<= 1
                logicGateBit += runGate(gates[i][j], logicGate)
            logicGate = logicGateBit

        print([logicGate, outputArr[k]])
        if logicGate == outputArr[k]:
            correct += 1

    return correct

def runGate(gate, binNum):
    val1 = (binNum >> gate.input1) & 1
    val2 = (binNum >> gate.input2) & 1

    if gate.gate == 0: # and
        return val1 & val2
    elif gate.gate == 1: # or
        return val1 | val2
    elif gate.gate == 2: # xor
        return val1 ^ val2
    elif gate.gate == 3: # wire
        return val1
    else: # negate
        return 0 if val1 == 1 else 1


# while (generate() == 0):
generate()
