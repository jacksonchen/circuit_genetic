class Gate:
    def __init__(self, gate, input1, input2):
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

def generate():
    gates = []
    for i in range(random.randint(1,6)):
        subGates = []
        for j in range(5):
            ggate = Gate(random.randint(0,4), random.randint(0,4), random.randint(0,4))
            subGates.append(ggate)

        gates.append(subGates)

    return gates

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

        # Check the bits match
        for i in range(4):
            if (logicGate >> i) & 1 == (outputArr[k] >> i) & 1:
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

def mutateGate(gate, chance):
    newGate = gate.gate
    newinput1 = gate.input1
    newinput2 = gate.input2
    if random.random() < chance:
        newGate = random.randint(0,4)
    if random.random() < chance:
        newinput1 = random.randint(0,4)
    if random.random() < chance:
        newinput2 = random.randint(0,4)

    return Gate(newGate, newinput1, newinput2)

def mutate(organism, chance):
    mutatedOrg = []
    for i in range(len(organism)):
        mutatedOrgLayer = []
        for j in range(len(organism[i])):
            mutatedOrgLayer.append(mutateGate(organism[i][j]), chance)
        mutatedOrg.append(mutatedOrgLayer)

    return mutatedOrg

# Generate initial
bestOrganism = generate()
best = evaluateBits(bestOrganism)
print("New best: ", best)

generationCount = 1
chance = 0.1

while 1:
    bestOrganismTmp = bestOrganism
    for e in range(10):
        mutated = mutate(bestOrganism, chance)
        evalNum = evaluateBits(mutated)
        if (evalNum > best):
            best = evalNum
            bestOrganismTmp = mutated
            print("New best: ", best)
    bestOrganism = bestOrganismTmp
    if generationCount % 1000 == 0:
        print("Completed generation ", generationCount)
    generationCount += 1
