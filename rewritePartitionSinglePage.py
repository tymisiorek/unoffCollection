import spacy
import json
import nltk
from spacy import displacy
import re



'''
Currently this cannot account for the situation where there's a title that starts on the line above a name, but also leaks into the line with the name
SpaCy doesn't detect every name, so this ends up with blocks of multiple names somtimes
'''

filePath = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\standardizedSegmentResultsInit.json"
titleIndices = []
#Words that appear in titles
TITLE_BANK = ["assistant", "associate", "chief", "command", "controller", "counsel", "director", "dean", "deputy", "director", "executive", "general", "officer", "president", "provost", "registrar", "treasurer", "trustee", "vice"]


def pathToString(filePath):
    with open(filePath, 'r') as file:
        fullText = json.load(file)
    return fullText


def removeEmptyElements(page):
    page = list(filter(None, page))
    page = list(filter(lambda x: x.strip(), page))
    return page


def checkTitleBank(line):
    for term in TITLE_BANK:
        if term in line.lower():
            return True
    return False


#Uses spacy to detect the named entities on the page and labels them
def tagNames(rawData):
    lineNumber = 0
    nameLines = []
    for text in rawData:
        doc = nlp(text)
        for ent in doc.ents:
            isPerson = str(ent.label_) == "PERSON"
            #Add each line that contains a person into the nameLines list
            if isPerson:
                nameLines.append(text)

            isGPE = any(ent.label_ == "GPE" for ent in doc.ents)
            #Will have to add a different way to handle the word dean, just a temporary solution
            isDean = "Dean" in str(ent.text)
            noKeywords = all(keyword not in text for keyword in ["Education", "Affiliation", "Career:"])
            #Assign the next line, ensure that it's not out of bound. Also check two lines ahead
            #-------------------------------------------------------------------------------
            if lineNumber < len(rawData) - 1:
                nextLine = rawData[lineNumber+1]
            else:
                nextLine = rawData[0]

            if lineNumber < len(rawData) - 2:
                twoLines = rawData[lineNumber+2]
            else:
                twoLines = rawData[0]
            #-------------------------------------------------------------------------------
            
            noTel = "tel:" not in nextLine.lower() and "tel" not in twoLines.lower()

            if isPerson and noKeywords and not isDean and noTel:
                print(str(ent), '\n')
                checkStructure(text, rawData[lineNumber-1], str(ent.text), lineNumber, rawData, nameLines)

        lineNumber+=1 



#Given a line of text, check to see what the name/title layout is
def checkStructure(currentLine, previousLine, name, lineNumber, rawData, nameLines):
    nameStartIndex = currentLine.index(name)
    nameEndIndex = nameStartIndex + len(name)
    previousContainsTitle = checkTitleBank(previousLine)
    if(currentLine[nameEndIndex:] != "" and currentLine[:nameStartIndex] != ""):
        #Check for case where the title is above the name and on the same line. This is not a perfect check, but it should overcount instead of undercount
        #Check that the previousline wasn't tagged as a name line and that it doesn't contain a colon. (Education: , E-mail:, etc)
        if(":" not in previousLine and previousLine not in nameLines and previousContainsTitle):
            title = previousLine, currentLine[:nameStartIndex].replace("Dr.", "")
            titleIndices.append(lineNumber-1)
        else:
            title = currentLine[:nameStartIndex].replace("Dr.", "")
            titleIndices.append(lineNumber)
        # print("This is the current line: ", currentLine)
        # print("First case title: ", title)
        # print("\n\n")
    elif(currentLine[:nameStartIndex] == "" and currentLine[-2].isdigit() and previousContainsTitle):
        title = previousLine
        titleIndices.append(lineNumber-1)
        # print("This is the current line: ", currentLine)
        # print("Second case title: ", title)
        # print("\n\n")
    elif(currentLine[:nameStartIndex] == "" and currentLine[nameEndIndex:] != ""):
        title = currentLine[nameEndIndex:]
        titleIndices.append(lineNumber)
        # print("This is the current line: ", currentLine)
        # print("Third case title: ", title)
        # print("\n\n")
    return titleIndices


def formatText(page, titleIndices):
    fileName = "structuredDataPage1.txt"
    lineCounter = 0
    with open(fileName, 'w') as file:
        for line in page:
            if(lineCounter in titleIndices):
                file.write('\n\n')
            # print(line)
            file.write(str(line))
            file.write('\n')
            lineCounter+=1



def printFormattedText(page, titleIndices):
    lineCounter = 0
    for line in page:
        if(lineCounter in titleIndices):
            print("\n\n")
        print(line)
        lineCounter+=1


#For getting the distance between two title indices
def distance(current, previous):
    distance = abs(int(current) - int(previous))
    # print("this is the distance: ", distance)
    return distance


#Check a name block and return true if a substring appears more than once in that block
def doubleOccurrence(list, substring):
    occurrences = 0
    for line in list:
        if substring in line:
            occurrences += 1
    # print(occurrences)
    return occurrences > 1


#Finds the first occurrence of a substring in a name block
def findFirstOccurrence(list, substring):
    lineNumber = 0
    # print("this is list: ", list)
    for line in list:
        # print("Thi is line: ", line, "    and this is substring: ", substring)
        if(substring in line):
            return lineNumber
        lineNumber += 1
    return lineNumber


#Takes two substrings, eg: Education: and Email:, and returns which one appears first
def appearsFirst(list, substring1, substring2):
    for line in list:
        if(substring1 in line):
            return substring1
        elif(substring2 in line):
            return substring2
    return ""


#Takes a block of text, identifies whether there's repeats of terms that only appear once per person, and split the block of text accordingly
def breakChunks(page, titleIndices):
    numTitles = len(titleIndices)
    startIndex = 0
    endIndex = 1
    while(endIndex < len(titleIndices)):

        if(startIndex < numTitles and distance(titleIndices[startIndex], titleIndices[endIndex]) > 3):
            nameBlock = page[titleIndices[startIndex]:titleIndices[endIndex]]
            firstAppeared = appearsFirst(nameBlock, "Education:", "E-mail:")

            if(doubleOccurrence(nameBlock, "Education:") and firstAppeared == "E-mail:"):
                #play around with this plus 1
                indexSplit = findFirstOccurrence(nameBlock, "Education:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1
            elif(doubleOccurrence(nameBlock, "E-mail:") and firstAppeared == "Education:"):
                indexSplit = findFirstOccurrence(nameBlock, "E-mail:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1
            elif(doubleOccurrence(nameBlock, "E-mail:") and firstAppeared == "E-mail:"):
                indexSplit = findFirstOccurrence(nameBlock, "E-mail:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1
            elif(doubleOccurrence(nameBlock, "Education:") and firstAppeared == "Education:"):
                indexSplit = findFirstOccurrence(nameBlock, "E-mail:") + titleIndices[startIndex] + 1
                titleIndices.insert(startIndex+1, indexSplit)
                startIndex += 1
                endIndex += 1

        startIndex+=1
        endIndex+=1
    return titleIndices


#Function to be called by other functions
#Check a block of text, and for each line that contains 4 or more periods, add that to the amount of people listed that block
def checkDots(list):
    nameCount = 0
    for line in list:
        dotCounter=  0
        for character in line:
            if character == '.':
                dotCounter+=1
        #this is an arbitrary value, cannot work for every occasion, but by making this one of many ways to check, hopefully this is not called often
        if dotCounter >= 3:
            nameCount += 1
    return nameCount


#Function to be called by other functions
#Check a block of text, and find the lines that contain 4 or more periods. Return the indec of the last line that contains 4 or more (should be the inde of second person in the block)
def checkSecondNameIndex(list):
    nameIndex = 0
    counter = 0
    for line in list:
        dotCounter=  0
        for character in line:
            if character == '.':
                dotCounter+=1
        if dotCounter >= 3:
            nameIndex = counter
        counter+=1
    return nameIndex





#Function to be called by other functions
def checkTitleNonTagged(page, secondNameIndex, nameBlock):
    secondNameString = page[secondNameIndex]
    secondNameSplit = secondNameString.split('.', 1)
    previousLine = page[secondNameIndex-1]
    print(secondNameSplit)
    #If there's a comma before the dots, there must be a title occurring on the same line as name with a comma (eg. Director, Media Relations Kali Chan)
    #This is not very robust and should be changed
    if(',' in secondNameSplit):
        #Check if the above line is also part of the title:
        if(':' not in previousLine and previousLine != nameBlock[0]):
            titleLine = secondNameIndex-1
        else:
            titleLine = secondNameIndex
    elif(secondNameString[-2].isdigit() and checkTitleBank(secondNameString) and checkTitleBank(previousLine) and ':' not in previousLine):
        titleLine = secondNameIndex-1
    elif(checkTitleBank(previousLine) and ':' not in previousLine):
        titleLine = secondNameIndex-1
    else:
        titleLine = secondNameIndex
    return titleLine
        
#Check for blocks of text that have more than one person in that block, and split them.
def breakDoubleNames(page, titleIndices):
    numTitles = len(titleIndices)
    startIndex = 0
    endIndex = 1
    #If we haven't reached the end of the titles
    while(endIndex < numTitles):
        nameBlock = page[titleIndices[startIndex]:titleIndices[endIndex]]
        numOfNames = checkDots(nameBlock)
        indexDistance = distance(titleIndices[startIndex], titleIndices[endIndex])
        #If there's more than 1 name and block is large enough
        if(numOfNames >= 2 and indexDistance > 2):
            secondNameIndex = checkSecondNameIndex(nameBlock) + titleIndices[startIndex]
            secondTitleIndex = checkTitleNonTagged(page, secondNameIndex, nameBlock)
            titleIndices.insert(startIndex+1, secondTitleIndex)
            startIndex+=1
            endIndex+=1
        #always increment these counters, increment by two if we add an element to titleIndices
        startIndex+=1
        endIndex+=1
    return titleIndices



#Breaks case where there's two consecutive names that have the title on the same line.
def breakTwoLineDoubleName(page, titleIndices):
    numTitles = len(titleIndices)
    startIndex = 0
    endIndex = 1
    while(endIndex < numTitles):
        nameBlock = page[titleIndices[startIndex]:titleIndices[endIndex]]
        numOfNames = checkDots(nameBlock)
        if(len(nameBlock) == 2 and numOfNames == 2):
            secondNameIndex = checkSecondNameIndex(nameBlock) + titleIndices[startIndex]
            titleIndices.insert(startIndex+1, secondNameIndex)
            startIndex+=1
            endIndex+=1
        #always increment these counters, increment by two if we add an element to titleIndices
        startIndex+=1
        endIndex+=1
    return titleIndices



#Takes single lines that weren't recognized as names and append them to the person below them. Needs to be tested more, I don't know if this can be used on a larger scale
def connectSingleLines(page, titleIndices):
    numTitles = len(titleIndices)
    startIndex = 0
    endIndex = 1
    while(endIndex < numTitles):
        numTitles = len(titleIndices)
        nameBlock = page[titleIndices[startIndex]:titleIndices[endIndex]]
        numLines = len(nameBlock)
        numOfNames = checkDots(nameBlock)
        if(numLines == 1 and numOfNames == 0):
            titleIndices.pop(startIndex+1)
            startIndex-=1
            endIndex-=1
        startIndex+=1
        endIndex+=1
    return titleIndices


def indicesToList(page, titleIndices):
    blockList = []
    numTitles = len(titleIndices)
    startIndex = 0
    endIndex = 1
    while(endIndex < numTitles):
        blockList.append(page[titleIndices[startIndex]:titleIndices[endIndex]])
        startIndex+=1
        endIndex+=1
    return blockList

        


# -----------------  Testing Methods  ----------------- #

nlp = spacy.load("en_core_web_sm")
rawData = pathToString(filePath)
singlePage = rawData[8]
singlePage = removeEmptyElements(singlePage)
tagNames(singlePage)
print("This is title indices before: ", titleIndices)
titleIndices = breakChunks(singlePage, titleIndices)
titleIndices = breakChunks(singlePage, titleIndices)
print("This is title indices midway: ", titleIndices)
titleIndices = breakDoubleNames(singlePage, titleIndices)
titleIndices = breakTwoLineDoubleName(singlePage, titleIndices)
titleIndices = connectSingleLines(singlePage, titleIndices)
print("This is title indices after: ", titleIndices)
formatText(singlePage, titleIndices)
print("\n\n\n\n")
printFormattedText(singlePage, titleIndices)
blockedText = indicesToList(singlePage, titleIndices)
print("\n\n")
print(blockedText)

print("\n\n\n")
print("Finished!")