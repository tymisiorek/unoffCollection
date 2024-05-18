import nltk
import csv
import json
import pandas as pd
import chardet
import Levenshtein as lvs

#Change to whatever you need
filePathOriginal = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\SecondYearStuff\\ConnectedData\ValidationSets\\auburnO.csv"
filePathValidated = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\SecondYearStuff\\ConnectedData\ValidationSets\\auburnV.csv"
pageTitle = "auburnAccuracies"



def read_names_original(filePath,):
     # Detect file encoding
    with open(filePath, 'rb') as f:
        result = chardet.detect(f.read())
    try:
        # Read the CSV file
        df = pd.read_csv(filePath, sep='|', encoding=result['encoding'], skiprows = 1, on_bad_lines='skip')
        
        # Assuming the names or titles are in the first column
        nameColumn = df.iloc[:, 1]  # Access the first column by index
        nameString = "\n".join(nameColumn.astype(str))
        return nameString
    except Exception as e:
        print("Error: ", e)
        return ' '
    

def read_names_validated(filePath):
    # Detect file encoding
    with open(filePath, 'rb') as f:
        result = chardet.detect(f.read())
    try:
        # Read the CSV file
        df = pd.read_csv(filePath, encoding=result['encoding'], on_bad_lines='skip')

        # Assuming the names or titles are in the second column
        nameColumn = df.iloc[:, 1]  # Access the name column by index
        nameString = "\n".join(nameColumn.astype(str))
        return nameString
    except Exception as e:
        print("Error: ", e)
        return ' '

def extractAllOriginal(path):
    columnDict = {}
    with open(path, 'rb') as f:
        result = chardet.detect(f.read())
    df = pd.read_csv(path, sep = '|', encoding = result['encoding'], skiprows = 1, on_bad_lines = 'skip')
    titleColumn = df.iloc[:, 0].str.strip().tolist()
    nameColumn = df.iloc[:, 1].str.strip().tolist()
    educationColumn = df.iloc[:, 2].str.strip().tolist()
    affiliationColumn = df.iloc[:, 3].str.strip().tolist()
    # schoolColumn = df.iloc[:, 5].str.strip().tolist()
    columnDict['Title'], columnDict["Name"], columnDict["Education"], columnDict["Affiliation"] = titleColumn, nameColumn, educationColumn, affiliationColumn
    return columnDict


def extractAllValidation(filePath):
    #Goes through the entire table and stores everything in a dictionary (validation tables)
    columnDict = {}
    with open(filePath, 'rb') as f:
        result = chardet.detect(f.read())
    df = pd.read_csv(filePath, encoding=result['encoding'], skiprows = 0,on_bad_lines='skip')
    titleColumn = df.iloc[:, 0].str.strip().tolist()
    nameColumn = df.iloc[:, 1].str.strip().tolist()
    educationColumn = df.iloc[:, 2].str.strip().tolist()
    affiliationColumn = df.iloc[:, 3].str.strip().tolist()
    # schoolColumn = df.iloc[:, 5].str.strip().tolist()

    columnDict['Title'], columnDict["Name"], columnDict["Education"], columnDict["Affiliation"] = titleColumn, nameColumn, educationColumn, affiliationColumn
    return columnDict


def averageLevenshtein(distanceList, mode):
    #If supplied with a 0 for mode, use all values, if supplied with a 1, don't use outliers
    counter = 0
    summation = 0
    if mode == 0:
        for x in distanceList:
            counter+=1
            summation+=x
    elif mode == 1:
        for x in distanceList:
            if x != 0:
                counter+=1
                summation+=x
    else:
        print("Invalid mode selected. Choose a 0 or 1.")
        return
    average = summation/counter
    return average


def tableCompare(original, validated, weight):
    #A weight value of zero will weigh every column the same, while 1 will put a larger emphasis on the name, title, and school
    #do not want to look at this function ever again
    distanceListT, distanceListN, distanceListE, distanceListA = [], [], [], []
    originalTitles, originalNames, originalEducation, originalAffiliation = original["Title"], original["Name"], original["Education"], original["Affiliation"]
    validatedTitles, validatedNames, validatedEducation, validatedAffiliation = validated["Title"], validated["Name"], validated["Education"], validated["Affiliation"]
    lengthdif = len(validatedNames) - len(originalNames)
    counterT, counterN, counterE, counterA, counterS, counterX = 0, 0, 0, 0, 0, 0
    
    if(lengthdif == 0):
        iterations = len(originalNames)
    elif(lengthdif > 0):
        iterations = len(originalNames)
    elif(lengthdif < 0):
        iterations = len(validatedNames)


    for x in range(iterations):
        skipRow = False
        skipRow2 = False
        #replace whitespace so we don't get weird scores
        originalNoWST, originalNoWSN, originalNoWSE, originalNoWSA = originalTitles[counterX].replace(" ", ""), originalNames[counterX].replace(" ", ""), originalEducation[counterX].replace(" ", ""), originalAffiliation[counterX].replace(" ", "")
        validatedNoWST, validatedNoWSN, validatedNoWSE, validatedNoWSA = validatedTitles[counterT].replace(" ", ""), validatedNames[counterN].replace(" ", ""), validatedEducation[counterE].replace(" ", ""), validatedAffiliation[counterA].replace(" ", "")
        distanceT, distanceN, distanceE, distanceA = lvs.ratio(originalNoWST, validatedNoWST), lvs.ratio(originalNoWSN, validatedNoWSN), lvs.ratio(originalNoWSE, validatedNoWSE), lvs.ratio(originalNoWSA, validatedNoWSA)

        #Name Distances
        if(distanceN < .6 and lengthdif > 0 or skipRow == True):
            distanceListN.append(0)
            counterN+=1
            skipRow = True 
        elif(distanceN < .6 and lengthdif < 0 or skipRow2 == True):
            distanceListN.append(0)
            skipRow2 = True

        #Title Distances
        if(skipRow == True):
            distanceListT.append(0)
            counterT+=1
        elif(skipRow2 == True):
            distanceListT.append(0)

    
        #Education Distances
        if(skipRow == True):
            distanceListE.append(0)
            counterE+=1
        elif(skipRow2 == True):
            distanceListE.append(0)

        #Affiliation distances
        if(skipRow == True):
            distanceListA.append(0)
            counterA+=1
        elif(skipRow2 == True):
            distanceListA.append(0)

        # #Schools distances
        # if(skipRow == True ):
        #     distanceListS.append(0)
        #     counterS+=1
        #     continue
        # elif(skipRow2 == True):
        #     distanceListS.append(0)
        #     continue

        distanceListN.append(distanceN)
        distanceListT.append(distanceT)
        distanceListE.append(distanceE)
        distanceListA.append(distanceA)
        # distanceListS.append(distanceS)

        #Increment the counters
        if(skipRow == False and skipRow2 == False):
            counterN, counterT, counterE, counterA, counterS, counterX = counterN+1, counterT+1, counterE+1, counterA+1, counterS+1, counterX+1
    
    #Compute average on all of them
    averageName, averageTitle, averageEducation, averageAffiliation = averageLevenshtein(distanceListN, 0), averageLevenshtein(distanceListT, 0), averageLevenshtein(distanceListE, 0), averageLevenshtein(distanceListA, 0)
    # print("Here is the average levenshtein distance for each column: ", averageName, averageTitle, averageEducation, averageAffiliation, averageSchool)
    if(weight == 0):
        fullAverageDistance = (averageName + averageTitle + averageEducation + averageAffiliation ) / 4
        return fullAverageDistance
    else:
        fullAverageDistance = (1.15*averageName + 0.88*averageTitle + 1.02*averageEducation + averageAffiliation )/4
        return fullAverageDistance 
    
    
#This function writes the average levenshtein to a text file
def writeDistances(averageDistance, pageName):
    path = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\SecondYearStuff\\ConnectedData\\ValidationSets\\refactoredDistances.txt"
    with open(path, 'a') as textfile:
        textfile.write(pageName + " Total Distances: " + str(averageDistance) + "\n")


def countMisses(original, validated):
    original = list(original.split("\n"))
    validated = list(validated.split("\n"))
    #find the larger list so we can choose which one to iterate until
    lengthdif = len(validated) - len(original)
    # print("This is length dif: ", lengthdif)
    return abs(lengthdif)
    

#This function takes the original names, and validated names, and calculates the levenshtein distance between all of them
def nameComparison(original, validated):
    distanceList = []
    original = list(original.split("\n"))
    validated = list(validated.split("\n"))
    #find the larger list so we can choose which one to iterate until
    lengthdif = len(validated) - len(original)
    if(lengthdif == 0):
        iterations = len(original)
    elif(lengthdif > 0):
        iterations = len(original)
    elif(lengthdif < 0):
        iterations = len(validated)

    counter = 0
    counterX = 0
    for x in range(iterations):
        #replace whitespace so we don't get weird scores
        originalNoWS = original[counterX].replace(" ", "")
        validatedNoWS = validated[counter].replace(" ", "")
        # print("These are the names: ", originalNoWS,   validatedNoWS)
        distance = lvs.ratio(originalNoWS, validatedNoWS)
        # print(originalNoWS, "     " , validatedNoWS)

        #If the names are way different, it's because there was a name that was missed, so catch it and increase/decrease the counter
        if(distance < .6 and lengthdif > 0):
            distanceList.append(0)
            counter+=1
            continue
        elif(distance < .6 and lengthdif < 0):
            distanceList.append(0)
            continue
        distanceList.append(distance)
        counter+=1
        counterX+=1

    # print(distanceList)
    return distanceList






# --------------- Method Testing --------------- #

# originalNames = read_names_original(filePathOriginal)
# validationNames = read_names_validated(filePathValidated)
# numMisses= countMisses(originalNames, validationNames)
# levDistances = nameComparison(originalNames, validationNames)
# averageDistance = averageLevenshtein(levDistances, 0)
# # writeDistances(numMisses, pageTitle)


# originalData = extractAllOriginal(filePathOriginal)
# validatedData = extractAllValidation(filePathValidated)
# fullDistances = tableCompare(originalData, validatedData,0)
# print(fullDistances)
# writeDistances(fullDistances, pageTitle)
# writeDistances(averageDistance, pageTitle)

# print("These are the original names: ", originalNames, "\n\n")
# print("These are the validation names: ", validationNames, "\n\n")
# print("Here are the individual Levenshtein distances of the names: ", levDistances)
# print("Here is the average Levenshtein distance of the names: ", averageDistance)