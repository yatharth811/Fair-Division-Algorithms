from tkinter import E
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it
import time

showSlow = False

def createLineGraph(length):
    firstList = [0, 1] + [0] * (length - 2)
    lastList = [0] * (length - 2) + [1, 0]

    baseList = [1, 0, 1] + [0] * (length - 3)

    finalList = [firstList]

    for i in range(length-2):
        tempList = [0] * i + baseList[:length-i]
        finalList.append(tempList)

    finalList.append(lastList)

    return finalList

###### BEGIN CHANGE THE PARAMETERS #########
adjMat = createLineGraph(4)
adjMat = np.array(adjMat)

numOfAgents = 3 # 3 or more on a line graph means all chores will be allocated
highValue = -1
lowValue = -2
###### END CHANGE THE PARAMETERS #########

def show_graph(adjacency_matrix):
    rows, cols = np.where(adjacency_matrix == 1)
    edges = zip(rows.tolist(), cols.tolist())
    gr = nx.Graph()
    gr.add_edges_from(edges)
    nx.draw(gr, node_size=500, with_labels=True)
    plt.show()

print(adjMat)
# show_graph(adjMat)
# input()

numOfChores = adjMat.shape[0]
print("numOfChores =", numOfChores)

# check EF1

def isEF1(allocation, valueProfile):
    valueProfile = np.array(valueProfile)

    flagEF1 = True 
    EF1FromAgent = -1
    EF1ToAgent = -1

    for agent in range(numOfAgents):
        choresToAgent = np.where(allocation == agent)
        # print("agent =", agent)
        # print("choresToAgent[0] =", choresToAgent[0])
        # print("valueProfile[choresToAgent[0]] =", valueProfile[choresToAgent[0]])

        if choresToAgent[0].size == 0:
            print("this agent got nothing")
            toCompareWOMostNegative = 0
        else: 
            toCompareWOMostNegative = sum(valueProfile[choresToAgent[0]]) - min(valueProfile[choresToAgent[0]])

        for otherAgent in range(numOfAgents):
            if otherAgent != agent:
                choresToOtherAgent = np.where(allocation == otherAgent)
                # print("otherAgent =", otherAgent)
                # print("choresToOtherAgent[0] =", choresToOtherAgent[0])
                # print("valueProfile[choresToOtherAgent[0]] =", valueProfile[choresToOtherAgent[0]])

                if choresToOtherAgent[0].size == 0:
                    print("this other agent got nothing")
                    othersBundleValue = 0
                else:
                    othersBundleValue = sum(valueProfile[choresToOtherAgent[0]])

                if toCompareWOMostNegative < othersBundleValue:
                    flagEF1 = False
                    EF1FromAgent = agent
                    EF1ToAgent = otherAgent
                    break

    return flagEF1, EF1FromAgent, EF1ToAgent

allFeasibleAlloc = [] # a matrix where each row corresponds to a feasible allocation wrt the given graph

# iterate over all allocations and rule out the infeasible ones

for allocation in it.product(range(numOfAgents), repeat=numOfChores):

    print("allocation =", allocation)
    allocation = np.array(allocation)
    # is this allocation feasible?

    feasible = True

    for agent in range(numOfAgents):
        choresToAgent = np.where(allocation == agent)
        # print("agent =", agent)
        # print("choresToAgent[0] =", choresToAgent[0])

        for chorePair in it.combinations(choresToAgent[0], 2): # chore pairs that can potentially share an edge
            if adjMat[chorePair] == 1:
                feasible = False
                break
    
        if not feasible:
            print("this allocation is not feasible")
            break
    
    if feasible:
        allFeasibleAlloc.append(list(allocation))

allFeasibleAlloc = np.array(allFeasibleAlloc)
print("allFeasibleAlloc =")
print(allFeasibleAlloc)
# input()
if showSlow: time.sleep(1)

numOfFeasibleAllocs = allFeasibleAlloc.shape[0]

def isPO(feasibleAlloc, valueProfile):
    valueProfile = np.array(valueProfile)

    agentTotalValues = np.zeros(numOfAgents)
    beatingAllocation = -1 * np.ones(numOfChores)

    paretoEfficient = True

    for agent in range(numOfAgents):
        choresToAgentInGivenAlloc = np.where(feasibleAlloc == agent)
        print("agent =", agent)
        print("choresToAgentInGivenAlloc[0] =", choresToAgentInGivenAlloc[0])

        agentTotalValues[agent] = sum(valueProfile[choresToAgentInGivenAlloc[0]])
    

    for allocation in allFeasibleAlloc:
        # does it Pareto dominate the given feasibleAlloc?

        competingAgentTotalValues = np.zeros(numOfAgents)

        for agent in range(numOfAgents):
            choresToAgentInCompetingAlloc = np.where(allocation == agent)
            print("agent =", agent)
            print("choresToAgentInCompetingAlloc[0] =", choresToAgentInCompetingAlloc[0])

            competingAgentTotalValues[agent] = sum(valueProfile[choresToAgentInCompetingAlloc[0]])

        print("valueProfile =", valueProfile)
        print("given allocation =", feasibleAlloc)
        print("agentTotalValues =", agentTotalValues)
        print("potential beating allocation =", allocation)
        print("competingAgentTotalValues =", competingAgentTotalValues)
        # input()

        print("(competingAgentTotalValues >= agentTotalValues).all() and (competingAgentTotalValues > agentTotalValues).any() =", (competingAgentTotalValues >= agentTotalValues).all() and (competingAgentTotalValues > agentTotalValues).any())
        # input()

        if (competingAgentTotalValues >= agentTotalValues).all() and (competingAgentTotalValues > agentTotalValues).any():
            paretoEfficient = False
            print("beats it, not PO")
            print("beating allocation =", allocation)
            beatingAllocation = allocation
            input()
            break

    return paretoEfficient, beatingAllocation



minNumOfEF1Alloc = np.inf
count = 0

fileName = "data_agents_" + str(numOfAgents) + "_chores_" + str(numOfChores) + ".txt"
f = open(fileName, "w")
print("highValue =", highValue, file=f)
print("lowValue =", lowValue, file=f)

for valueProfile in it.product([highValue, lowValue], repeat=numOfChores):

    impossible = True
    PO_EF1_impossible = True
    EF1_allocations = []
    # input()

    # print("valueProfile =", valueProfile, file=f)

    # iterate over all feasible allocation to see if any one of them is EF1
    for feasibleAlloc in allFeasibleAlloc:

        feasibleTest = isEF1(feasibleAlloc, valueProfile)
        feasiblePOTestBefore = isPO(feasibleAlloc, valueProfile)

        print("\tfeasibleAlloc =", feasibleAlloc)
        print("Want to check if all allocations are PO in this code")
        if feasibleTest[0]: print("this is EF1")
        else: print("this is NOT EF1")
        if feasiblePOTestBefore[0]: print("this is PO")
        else: print("this is NOT PO")
        # input()
        

        if feasibleTest[0]:
            print("\tTHE ALLOCATION IS EF1")
            print("\tvalueProfile =", valueProfile)
            impossible = False 
            EF1_allocations.append(list(feasibleAlloc))
            feasiblePOTest = isPO(feasibleAlloc, valueProfile)

            if feasiblePOTest[0]:
                print("\tTHE ALLOCATION IS PO AS WELL")
                print("\tHENCE, THIS VALUE PROFILE HAS A EF1 + PO ALLOCATION")
                print("\tfeasibleAlloc =", feasibleAlloc)
                print("\tis not a counterexample")
                PO_EF1_impossible = False
                if showSlow: time.sleep(1)
            else:
                print("\tThe allocation is not PO")
                print("\tBeating allocation =", feasiblePOTest[1])
                input()
                
        else:
            print("\tTHE ALLOCATION IS NOT EF1")
            print("\tEF1FromAgent =", feasibleTest[1])
            print("\tEF1ToAgent =", feasibleTest[2])

    if impossible:
        print("Eureka! Found a value profile where no feasible allocation is EF1")
        print("What value profile is it?")
        print("valueProfile =", valueProfile)
        input()

    else:
        EF1_allocations = np.array(EF1_allocations)
        print("\nvalueProfile =", valueProfile, file=f)
        print("EF1 allocations for this valueProfile:", file=f)
        print(EF1_allocations, file=f)
        numOfEF1Alloc = EF1_allocations.shape[0]
        print("Number of EF1 allocations =", numOfEF1Alloc)
        if numOfEF1Alloc < minNumOfEF1Alloc:
            minNumOfEF1Alloc = numOfEF1Alloc
        # input()
        if showSlow: time.sleep(0.5)

    if PO_EF1_impossible:
        print("Eureka! Found a value profile where no feasible allocation is both EF1 and PO")
        print("What value profile is it?")
        print("valueProfile =", valueProfile)
        input()

    count += 1

print("\nNumber of valuation profiles =", count, file=f)
print("minNumOfEF1Alloc =", minNumOfEF1Alloc, file=f)

f.close()
