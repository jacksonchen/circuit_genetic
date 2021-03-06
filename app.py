class Gate:
    def __init__(self, gate, inputPins):
        self.gate = gate
        self.inputPins = inputPins

    def __str__(self):
        return "Gate {}, Input: {}".format(self.gate, self.inputPins)

import numpy as np
import random
GEN_LIMIT = 1000
CHANCE_CONST = 1
MODIFIER_CONST = 0
NUM_CHILDREN = 10
ANNEAL_GEN_LIMIT = GEN_LIMIT
ANNEAL_MAX = 0.9
AUTO_TERMINATE = 100000
SELECTION_POOL = 5

inputArr = np.array(np.genfromtxt('input.csv', delimiter=', ', dtype='str'))
inputArr = [int(s, 16) for s in inputArr]
outputArr = np.array(np.genfromtxt('output.csv', delimiter=', ', dtype='str'))
outputArr = [int(s, 16) for s in outputArr]

# Mask
#   Output Bits [5]
#       Layer 1 Gates
#           Pins, each associated with an input bit
#       Layer 2 Gate - Random gate connecting result of layer 1

def generate():
    mask = []
    for j in range(5):
        layer = []
        outputbits = []
        # Layer 1
        gate1count = random.randint(2,7)

        for k in range(gate1count):
            # All the pins that connect to one gate
            pins = []
            inputPins = random.randint(2,5)
            for l in range(inputPins):
                pins.append(random.randint(0,4))
            outputbits.append(Gate(random.randint(0,4), pins))
        layer.append(outputbits)

        # Layer 2
        mask.append(Gate(random.randint(0,4), []))

    return mask

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

                # Mutate the order of the gates
                gateOrder = list(range(5))
                if random.random() < chance:
                    random.shuffle(gateOrder)

                for j in gateOrder:
                    mutatedOrgLayer.append(mutateGate(chosenGateLayer[j], chance))
                mutatedOrg.append(mutatedOrgLayer)
        else:
            for i in range(len(organism)):
                mutatedOrgLayer = []
                gateOrder = list(range(5))
                if random.random() < chance:
                    random.shuffle(gateOrder)

                for j in gateOrder:
                    mutatedOrgLayer.append(mutateGate(organism[i][j], chance))
                mutatedOrg.append(mutatedOrgLayer)
            for i in range(newLayers - len(organism), newLayers):
                mutatedOrgLayer = []
                gateOrder = list(range(5))
                if random.random() < chance:
                    random.shuffle(gateOrder)

                for j in gateOrder:
                    mutatedOrgLayer.append(Gate(random.randint(0,4), random.randint(0,4), random.randint(0,4)))
                mutatedOrg.append(mutatedOrgLayer)
    else:
        for i in range(len(organism)):
            mutatedOrgLayer = []
            gateOrder = list(range(5))
            if random.random() < chance:
                random.shuffle(gateOrder)

            for j in gateOrder:
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
autoTerm = 0
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
        autoTerm = 0
        improved = False
    else:
        genLimit -= 1

    if (chance != CHANCE_CONST and genLimit == GEN_LIMIT - ANNEAL_GEN_LIMIT):
        chanceHist = chance
        chance = CHANCE_CONST

    # if (autoTerm >= AUTO_TERMINATE):
    #     print("==========Restarting==========")
    #
    #     bestOrganism = generate()
    #     best = evaluateBits(bestOrganism)
    #     globalBest = best
    #     print("New best: ", best)
    #
    #     generationCount = 1
    #     chance = CHANCE_CONST
    #     chanceHist = chance
    #     modifier = MODIFIER_CONST
    #     genLimit = GEN_LIMIT
    #     autoTerm = 0
    #     avg = 0
    #     improved = False
    if (genLimit == 0):
        chance = chanceHist + modifier
        genLimit = GEN_LIMIT
        autoTerm += GEN_LIMIT
        print("Annealed chance now", chance)
