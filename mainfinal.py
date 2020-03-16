import numpy as np
import decimal
import operator

# console output config
np.set_printoptions(linewidth=200)

# print seperator
def sep():
    print('---------------------------------------')

# calculate the length of individual L-segments
def calculateL(inL, inSupport):
    result = []

    # if user did not enter any support, add one default support at L (so that a default 4x4 can be generated later on)
    if len(inSupport) == 0:
        result.append(round(inL,5))
        return result #return to calling program, skip all the code below

    # if user entered at least 1 support
    for i in range(0, len(inSupport) + 1):
        # first loop iteration: the first support location = length of first L-segment
        if i == 0:
            result.append(round(inSupport[0],5))

        # last loop iteration: length of last L-segment = L-last support location
        elif i == len(inSupport):
            result.append(round(inL - inSupport[i-1],5))

        # all other iterations: length of L-segment = current support location - previous support location
        else:
            result.append(round(inSupport[i] - inSupport[i-1],5))

    # check if all L-segments add up to L
    if round(sum(result),5) != inL:
        print("Something went wrong that is not supposed to happen!!!")
        exit(1) # if it doesn't, exit the program
    else:
        print('Sum of all L-segments verified!')

    # print
    print("There are {} L-segments of: {}, respectively.".format(len(result),result))
    sep()

    # returns a python list containing L-segments
    return result

# 4x4 matrix 'generator' based on 'L' value
def template4x4(L):
    # this is the template of a typical 4x4 matrix
    template = np.asmatrix([[(12/L**3),     (6/L**2),   (-12/L**3), (6/L**2)],
                            [(6/L**2),      (4/L),      (-6/L**2),  (2/L)],
                            [(-12/L**3),    (-6/L**2),  (12/L**3),  (-6/L**2)],
                            [(6/L**2),      (2/L),      (-6/L**2),  (4/L)]
                            ])
    # returns the matrix above, with the value of L subbed-in
    return template

# calculate global matrix
def calculateGlobal(inLVals):
    # generate 4x4 matrices for each L-segment, and store them in a python list: matrixList
    matrixList = []
    for Lseg in inLVals:
        matrixList.append(template4x4(Lseg))

    # prints each of the 4x4 matrices generated
    print("4 x 4 Matrices:")
    for i in range(0, len(matrixList)):
        print("Matrix [{}]:".format(i+1))
        print(matrixList[i], end="\n")
    sep()

    # calculation of global matrix starts here
    # creation of a default global matrix with all zeros
    globalmatrix = np.asmatrix(np.zeros((4,4)))

    for i in range(0, len(matrixList)):
        # first loop iteration: global matrix = first 4x4 matrix generated previously
        if (i == 0):
            globalmatrix = matrixList[0]
        
        # all other iterations: combine globalmatrix and 4x4 matrices
        else:
            # pad globalMatrix
            globalmatrix = np.pad(globalmatrix,[(0,2),(0,2)], mode='constant')

            # pad 4x4 matrix
            padWidth = globalmatrix.shape[0] - 4
            inMatrix = np.pad(matrixList[i],[(padWidth,0),(padWidth,0)], mode='constant')

            # combine both padded matrices
            globalmatrix = np.add(globalmatrix, inMatrix)

    print("Global matrix:")
    print(globalmatrix)
    sep()

    return globalmatrix

# fractions generator
def templateFormula(choice, p, a, b, l):
    # F-Left
    if choice == 1:
        result = (p*b**2*(b+3*a))/l**3
    # M-Left
    elif choice == 2:
        result = -(p*a*b**2)/l**2
    # F-Right
    elif choice == 3:
        result = (p*a**2*(a+3*b))/l**3
    # M-Right
    elif choice ==4:
        result = (p*b*a**2)/l**2
    return round(result,5)

# calculate F matrix
def calculateF(inL, inSupportVals, inForces, inLVals):

    # since both ends of beam have Rx-es, and every support is also an Rx,
    # this part ensures both ends of beam has an Rx

    if len(inSupportVals) == 0:
        inSupportVals.append(inL) 
    elif len(inSupportVals) != 1:
        inSupportVals.append(inL)
    elif len(inSupportVals) == 1 and max(inSupportVals)!= inL:
        inSupportVals.append(inL)
    inSupportVals.insert(0, 0.0)

    # this list will hold one sub-list for each force
    listofForces = []

    # generate left and right fractions for each force P
    for force in inForces:
        p = force[0]

        # find which L (index) the force belongs to
        index = 0
        for i in range (0, len(inSupportVals)):
            if force[1] < inSupportVals[i]:
                index = i-1
                break #break once found
        
        l = inLVals[i-1]
        a = round(force[1] - inSupportVals[index], 5)
        b = round(inSupportVals[i] - force[1], 5)
        F_Left = templateFormula(1,p,a,b,l)
        M_Left = templateFormula(2,p,a,b,l)
        F_Right = templateFormula(3,p,a,b,l)
        M_Right = templateFormula(4,p,a,b,l)

        # for verification purposes only
        print("{} \t Magnitude P = {} \t Position = {} \t L = {} \t a = {} \t b = {}".format(index, p,force[1], l, a,b))

        # add sub-list of a single force, to main list
        listofForces.append([index, F_Left, M_Left, F_Right, M_Right])

    # for verification purposes only, print all forces
    sep()
    for i in range (0, len(listofForces)):
        print("P{}:\tL{}\tF_Left: {}\tM_Left: {}\tF_Right: {}\tM_Right: {}".format(i+1,listofForces[i][0]+1,listofForces[i][1],listofForces[i][2],listofForces[i][3],listofForces[i][4]))
    sep()

    # calculate F and M for each of the Rx positions and assemble the F matrix
    result = []
    for i in range (0, len(inSupportVals)):
        F = 0
        M = 0

        # Add all the right sides
        for item in listofForces:
            if item[0] == i-1:
                F = round(F+item[3],5)
                M = round(M+item[4],5)

        # Add all the left sides
        for item in listofForces:
            if item[0] == i:
                F = round(F+item[1],5)
                M = round(M+item[2],5)

        # add to the F matrix
        result.append([F])
        result.append([M])

    # convert list to numpy matrix
    result = np.asmatrix(result)

    print("F Matrix:")
    print(result)
    sep()   
    return result

# reduce global matrix for FI calculation
def reduceGlobal_fi(inMatrix, inE, inI):

    # remove row and columns (simulate multiplying by D=0, choosing rows)
    inMatrix = np.delete(inMatrix, range(0, inMatrix.shape[0], 2), axis=0)
    inMatrix = np.delete(inMatrix, range(0, inMatrix.shape[1], 2), axis=1)

    # multiply E and I
    inMatrix = np.multiply(inMatrix, inE)
    inMatrix = np.multiply(inMatrix, inI)

    # print
    print("Reduced global matrix (FI) after multiplying E and I:")
    print(inMatrix)
    sep()

    return inMatrix

# reduce global matrix for RX calculation
def reduceGlobal_rx(inMatrix, inE, inI):

    #remove rows and columns (simulate multiplying by D=0, choosing rows)
    inMatrix = np.delete(inMatrix, range(1, inMatrix.shape[0], 2), axis=0)
    inMatrix = np.delete(inMatrix, range(0, inMatrix.shape[1], 2), axis=1)

    # multiply E and I
    inMatrix = np.multiply(inMatrix, inE)
    inMatrix = np.multiply(inMatrix, inI)

    # print
    print("Reduced global matrix (RX) after multiplying E and I:")
    print(inMatrix)
    sep()

    return inMatrix




# Program starts here!
# user input for L
while True:
    try:
        l = float(input("Please length L of beam >> "))
        if l <=0: 
            print("L cannot be less than or equals to 0!")
            continue

    # so that you can quit using CTRL+C
    except KeyboardInterrupt: 
        exit(0)

    # when conversion to float fails (means user entered non-number)
    except:
        print("Please enter a valid number!")
        continue
    else:
        break

# user input for support positions
while True:
    support_Values=[]
    try:
        supportStr = input("Please enter support positions separated by commas >> ")

        # if users enters nothing
        if supportStr=='':
            print("Default values used.")
            break
        # users enters something
        else:
            support_Values = supportStr.split (",")
            support_Values = [ float(x) for x in support_Values ]
            support_Values.sort() #sort ascending

            # ensure support positions are within range (position = 0 or L will still crash!!)
            if max(support_Values) > l or min(support_Values) < 0:
                support_Values.clear()
                print("Support positions cannot be less than 0 or more than L!")
                continue

    # so that you can quit using CTRL+C
    except KeyboardInterrupt:
        exit(0)

    # when conversion to float or list fails (means user entered non-number, or no comma, etc)
    except Exception:
        print("Your input is not valid!!")
        continue
    else:
        break

# user input for force magnitude and positions
inputForce = []
while True:
    try:
        print("Please enter magnitude and position of ONE force separated by a comma.")
        print("If you have none left, simply press ENTER.")
        forceStr = input(">> ")

        # if user entered blank, stop asking for more (given user has already entered at least one valid force before this)
        if forceStr == "" and len(inputForce)>0:
            print("okay, moving on!")
            break
        else:
            inForce = forceStr.split (",")
            inForce = [ float(x) for x in inForce ]

            # check if force position is within the beam L
            if inForce[1] > l or inForce[1] < 0:
                print("Force positions cannot be less than 0 or more than L!\n")
                continue

            # add input to the python list of forces
            inputForce.append(inForce)

    # so that you can quit using CTRL+C
    except KeyboardInterrupt:
        exit(0)
    
    # when conversion to float or list fails (means user entered non-number, or no comma, etc)
    except:
        print("Your input is not valid!!")
        continue

# user input for E
while True:
    try:
        E = float(input("Please enter desired value of E >> "))

    # so that you can quit using CTRL+C
    except KeyboardInterrupt:
        exit(0)

    # when conversion to float fails (means user entered non-number)
    except:
        print("Please enter a valid number")
        continue
    else:
        break

# user input for b
while True:
    try:
        b = float(input("Please enter desired value of B >> "))

    # so that you can quit using CTRL+C
    except KeyboardInterrupt:
        exit(0)
    
    # when conversion to float fails (means user entered non-number)
    except:
        print("Please enter a valid number")
        continue
    else:
        break

# user input for h
while True:
    try:
        h = float(input("Please enter desired value of H >> "))

    # so that you can quit using CTRL+C
    except KeyboardInterrupt:
        exit(0)

    # when conversion to float fails (means user entered non-number)
    except:
        print("Please enter a valid number")
        continue
    else:
        break

# print summary of input
sep()
sep()
sep()
print("Here's a summary of your inputs:")
print("L = ", l)
print("Support locations at:", support_Values)
sep()

# calculate L-segments
LVals = calculateL(l, support_Values)

# after getting all the user input, start calculations from here onwards
# l = the L that the user entered
# support_Values = a python list of all the support locations the user entered
# globalmatrix holds the FULL global matrix
globalmatrix = calculateGlobal(LVals)

#calculate I using b and h
I = round((b*h**3)/12,5)
print("I = {}".format(I))
sep()

# sort force positions, ascending
inputForce = sorted(inputForce, key=operator.itemgetter(1))

# calculate the fmatrix
fmatrix = calculateF(l, support_Values, inputForce, LVals)


### solving for FIs ###
# reduce global matrix (for calculating FIs) and multiply EI
globalmatrix_reduced_fi = reduceGlobal_fi(globalmatrix, E, I)

# remove unwanted rows from F-matrix for FI calculation
fmatrix_reduced_fi = np.delete(fmatrix, range(0, fmatrix.shape[0], 2), axis=0)
print("Reduced FMatrix (FI):")
print(fmatrix_reduced_fi)
sep()

# solve for the 'fi's and store into dmatrix
dmatrix = np.linalg.solve(globalmatrix_reduced_fi, fmatrix_reduced_fi)
print("DMatrix: (FI's in order)")
print(dmatrix)
sep()

### solving for RX-es ###
# reduce global matrix (for calculating RX-es) and multiply EI
globalmatrix_reduced_rx = reduceGlobal_rx(globalmatrix, E, I)

# calculate Rx-es
# multiply the global matrix by the 'FI's
globalmatrix_reduced_rx = np.matmul(globalmatrix_reduced_rx,dmatrix)

# remove unwanted rows from F-matrix for RX calculation
fmatrix_reduced_rx = np.delete(fmatrix, range(1, fmatrix.shape[0], 2), axis=0)
print("Reduced FMatrix (RX):")
print(fmatrix_reduced_rx)
sep()

# solve for Rx-es by subtracting left and right sides
RXmatrix = np.subtract(fmatrix_reduced_rx, globalmatrix_reduced_rx)
RXmatrix = np.around(RXmatrix, 5) # round to 5dc
print("RXmatrix: (rx's in order)")
print(RXmatrix)

sep()
input('Press ENTER to exit!')