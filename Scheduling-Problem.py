from collections import OrderedDict
from colorama import init
from copy import deepcopy
import numpy as np
import itertools as it


numOfAgents = 3
numOfChores = 6
count = 0
minNumOfEF1Alloc = np.inf
highValue = -1
lowValue = -2
tables = []
allEF1Sketches = []

def initialiseTables(numOfAgents, numOfChores, valuationProfile, tables):
    # Table consists of sketches
    # Sketch = (total valuation, worstchore for each agent, ith agent who got chore)
    table = []
    for i in range(numOfAgents):
        allocation = [i] + [-1] * (numOfChores-1) # -1 means chore has not been allocated yet
        valuations = [0] * numOfAgents
        valuations[i] = valuationProfile[0]
        worstChores = [0] * numOfAgents
        worstChores[i] = valuationProfile[0]
        sketch = [valuations, worstChores, i]
        table += [sketch]

    tables += [table]
    # tables = list(OrderedDict.fromkeys(tables))


# Simulate code now 
def dpCode(numOfAgents, numOfChores, valuationProfile, tables):
    
    for i in range(1, numOfChores):
       
        table = tables[i-1]
        print("Chore ", i-1, " table: ", table, "\nSize: ", len(table))
        newTable = []
        
        for sketch in table:
            agentToNotAssign = sketch[2]
            # print("Sketch is: ", sketch, "AgentL: ", agentToNotAssign)
            
            for j in range(numOfAgents):
                
                if j == agentToNotAssign:
                    continue
                
                else:
                    newSketch = deepcopy(sketch)
                    newSketch[2] = j
                    newSketch[1][j] = min(valuationProfile[i], newSketch[1][j])
                    newSketch[0][j] += valuationProfile[i]
                    # if (newSketch[1][j] == -1 or valuationProfile[newSketch[1][j]] > valuationProfile[i]):
                    #     newSketch[1][j] = i
                    
                    flag = True
                    for test in newTable:
                        if newSketch == test:
                            flag = False

                    if flag: 
                        newTable += [newSketch]
                # print("Sketch after: ", sketch)
                    
        # print("New Table is: ", newTable)
        tables += [newTable]

    print("Chore ", numOfChores-1, " table: ", tables[-1],  "\nSize: ", len(tables[-1]))

def mainFunction(numOfAgents, numOfChores, valuationProfile, tables):
    initialiseTables(numOfAgents, numOfChores, valuationProfile, tables)
    dpCode(numOfAgents, numOfChores, valuationProfile, tables)
    
   
# Table's last element has all the information to check for EF1
def isEF1(numOfAgents, sketch, valuationProfile):

    EF1Flag = True
    totalValuations = deepcopy(sketch[0])
    worstChores = deepcopy(sketch[1])
    agent1 = -1
    agent2 = -1

    for agent in range(numOfAgents):
        agentsOwnValuation = totalValuations[agent]
        agentsWorstChore = worstChores[agent]
        for otherAgents in range(numOfAgents):
            otherAgentsValuation = totalValuations[otherAgents]
            # print(agentsOwnValuation + " " + )
            if (agentsOwnValuation - agentsWorstChore < otherAgentsValuation):
                EF1Flag = False
                agent1 = agent
                agent2 = otherAgents
                return EF1Flag, agent1, agent2
            
    return EF1Flag, agent1, agent2


fileName = "data_agents_dpcode_" + str(numOfAgents) + "_chores_" + str(numOfChores) + ".txt"
f = open(fileName, "w")
print("highValue =", highValue, file=f)
print("lowValue =", lowValue, file=f)

for valueProfile in it.product([highValue, lowValue], repeat=numOfChores):

    impossible = True
    tableAllocations = []
    numOfEF1Alloc = 0
    mainFunction(numOfAgents, numOfChores, valueProfile, tableAllocations)
    print("\nvalueProfile =", valueProfile, file=f)
    print("\nEF1 Sketches for this valueProfile: ", file=f)
    for sketch in tableAllocations[-1]:

        feasibleTest = isEF1(numOfAgents, sketch, valueProfile)

        # print("\tSketch =", sketch)
        print("------------------------------------------------------------")

        if feasibleTest[0]: print("this is EF1")
        else: print("this is NOT EF1")
        

        if feasibleTest[0]:
            
            print("\tTHE ALLOCATION IS EF1")
            print("\tvalueProfile =", valueProfile)
            print("\tSketch: ", sketch)
            print("\tSketch: ", sketch, file=f)
            numOfEF1Alloc += 1
            impossible = False

                
        else:
            print("\tTHE ALLOCATION IS NOT EF1")
            print("\tvalueProfile =", valueProfile)
            print("\tSketch: ", sketch)
            print("\tAgent who envies: ", feasibleTest[1])
            print("\tAgent being envied: ", feasibleTest[2])

    if impossible:
        print("Eureka! Found a value profile where no feasible allocation is EF1")
        print("What value profile is it?")
        print("valueProfile =", valueProfile)
        input()
        

    else:
        # print("\nvalueProfile =", valueProfile, file=f)
        print("Number of EF1 allocations =", numOfEF1Alloc)
        if numOfEF1Alloc < minNumOfEF1Alloc:
            minNumOfEF1Alloc = numOfEF1Alloc
       

    count += 1

print("\nNumber of valuation profiles =", count, file=f)
print("minNumOfEF1Alloc =", minNumOfEF1Alloc, file=f)
f.close()
