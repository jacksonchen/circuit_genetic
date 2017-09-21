class Gate:
    def __init__(self, gate, input1, input2):
        self.gate = gate
        self.input1 = input1
        self.input2 = input2

    def __str__(self):
        return "Gate {}, Input1: {}, Input2: {}".format(self.gate, self.input1, self.input2)

import numpy as np
import random
GEN_LIMIT = 1000
CHANCE_CONST = 0.05
MODIFIER_CONST = 0.05
NUM_CHILDREN = 10
ANNEAL_GEN_LIMIT = 50
ANNEAL_MAX = 0.9
NUM_LAYERS = 4

inputArr = np.array(np.genfromtxt('input.csv', delimiter=', ', dtype='str'))
inputArr = [int(s, 16) for s in inputArr]
outputArr = np.array(np.genfromtxt('output.csv', delimiter=', ', dtype='str'))
outputArr = [int(s, 16) for s in outputArr]

def generate():
    gates = []
    for i in range(random.randint(1,NUM_LAYERS)):
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
    inputChoices = [0, 1, 2, 3, 4]

    # Mutate the gate
    if random.random() < chance:
        newGate = random.randint(0,4)

    # Mutate first input
    if random.random() < chance:
        newinput1 = random.randint(0,4)
        inputChoices.remove(newinput1)

    # Mutate second input
    if random.random() < chance:
        newinput2 = random.choice(inputChoices)

    return Gate(newGate, newinput1, newinput2)

def mutate(organism, chance):
    mutatedOrg = []

    # Mutate number of layers
    if random.random() < chance:
        newLayers = random.randint(1,NUM_LAYERS)
        if newLayers <= len(organism):
            organismCopy = organism[:]
            for i in range(newLayers):
                mutatedOrgLayer = []
                chosenGateLayer = random.choice(organismCopy)
                organismCopy.remove(chosenGateLayer)
                for j in range(5):
                    mutatedOrgLayer.append(mutateGate(chosenGateLayer[j], chance))
                mutatedOrg.append(mutatedOrgLayer)
        else:
            for i in range(len(organism)):
                mutatedOrgLayer = []
                for j in range(5):
                    mutatedOrgLayer.append(mutateGate(organism[i][j], chance))
                mutatedOrg.append(mutatedOrgLayer)
            for i in range(newLayers - len(organism), newLayers):
                mutatedOrgLayer = []
                for j in range(5):
                    mutatedOrgLayer.append(Gate(random.randint(0,4), random.randint(0,4), random.randint(0,4)))
                mutatedOrg.append(mutatedOrgLayer)
    else:
        for i in range(len(organism)):
            mutatedOrgLayer = []
            for j in range(5):
                mutatedOrgLayer.append(mutateGate(organism[i][j], chance))
            mutatedOrg.append(mutatedOrgLayer)

    return mutatedOrg

# Generate initial
bestOrganism = generate()
best = evaluateBits(bestOrganism)
globalBest = best
print("New best: ", best)

generationCount = 1
chance = CHANCE_CONST
chanceHist = chance
modifier = MODIFIER_CONST
genLimit = GEN_LIMIT
avg = 0
improved = False

while 1:
    bestOrganismTmp = None
    best = 0
    for e in range(NUM_CHILDREN):
        mutated = mutate(bestOrganism, chance)
        evalNum = evaluateBits(mutated)
        avg += evalNum
        if evalNum > best:
            best = evalNum
            bestOrganismTmp = mutated
        if best > globalBest:
            print("New best: ", best, "Layers", len(bestOrganismTmp))
            globalBest = best
            improved = True

    bestOrganism = bestOrganismTmp
    if generationCount % 1000 == 0:
        avg /= (NUM_CHILDREN * 1000)
        print("Generation", generationCount, "Average", avg)
        avg = 0
    generationCount += 1

    # Annealing
    if improved:
        genLimit = GEN_LIMIT
        chance = CHANCE_CONST
        chanceHist = CHANCE_CONST
        improved = False
    else:
        genLimit -= 1

    if (chance != CHANCE_CONST and genLimit == GEN_LIMIT - ANNEAL_GEN_LIMIT):
        chanceHist = chance
        chance = CHANCE_CONST

    if (genLimit == 0 and chance < ANNEAL_MAX):
        chance = chanceHist + modifier
        genLimit = GEN_LIMIT
        print("Annealed chance now", chance)
