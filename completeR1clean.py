import csv
import json

#Declaring globals
rstringDict = {}
eo1 = {}
eo2 = {}
eo3 = {}
codeRevMap = {}

def readFile():
    global rstringDict
    r = open("halfverifiedlist.txt", "r")
    rstringList = r.readlines()
    rstring = rstringList[0]
    #Need to convert string to dictionary. The key-value pair is School Name - EIN Numbers
    rstringDict = json.loads(rstring)
    #print(rstringDict)

def procEOs():
    with open("eo1.csv") as csvfile:
        data = csv.reader(csvfile)
        #Go through the csv, making the keys EIN numbers and values the other data (the revenue)
        for row in data:
            key = row[0]
            values = row[25]
            eo1[key] = values
    with open("eo2.csv") as csvfile2:
        data2 = csv.reader(csvfile2)
        #Go through the csv, making the keys EIN numbers and values the other data
        for row2 in data2:
            key = row2[0]
            values = row2[25]
            eo2[key] = values
    with open("eo3.csv") as csvfile3:
        data3 = csv.reader(csvfile3)
        #Go through the csv, making the keys EIN numbers and values the other data
        for row3 in data3:
            key = row3[0]
            values = row3[25]
            eo3[key] = values
    #print(eo1)




def fixEINs():
    #This loop is stupid dont know if it will work
    for x in eo1:
        if(x in rstringDict.values()):
            codeRevMap[x] = eo1[x]
            # key = [i for i in rstringDict if rstringDict[i] == x]
            # highRev = int(eo1[x])
            # highKey = key[0]
            # if highKey is not None:
            #     rstringDict[highKey] = x
            #     highRev = 0
    for y in eo2:
        if(y in rstringDict.values()):
            codeRevMap[y] = eo2[y]
            # key = [j for j in rstringDict if rstringDict[j] == y]
            # highRev = int(eo2[y])
            # highKey = key[0]
            # if highKey is not None:
            #     rstringDict[highKey] = y
            #     highRev = 0
    for z in eo3:
        if(z in rstringDict.values()):
            codeRevMap[z] = eo3[z]
            # key = [k for k in rstringDict if rstringDict[k] == z]
            # highRev = int(eo3[z])
            # highKey = key[0]
            # if highKey is not None:
            #     rstringDict[highKey] = z
            #     highRev = 0
    with open('correspondingeins.txt', 'w') as file:
        file.write(json.dumps(codeRevMap))
    

def maptoschool():
    highrev = 0
    emptystring = ""
    map = open("SingledEINs.txt", "r")
    #Go through keys of codeRevMap, if that key is a key of rstringDict, iterate through that key's values
    for x in codeRevMap:
        highrev = 0
        if(x in rstringDict):
            values = rstringDict[x]
            usedEIN = ""
            for y in values:
                if(codeRevMap[x] != emptystring and int(codeRevMap[x]) > highrev):
                    highrev = codeRevMap[x]
                    usedEIN = y
            rstringDict[x] = usedEIN

    with open('SingledEINs.txt', 'w') as file:
        file.write(json.dumps(rstringDict))






# ------------- Main Testing Here. Don't add anything past this line -------------
print("Starting Main Testing Now: ")
readFile()
print("Dictionary rstringDict initialized. \nNow processing EOs")
procEOs()
print("Finished processing EOs")
fixEINs()
print("EINs Fixed! (hopefully)")
maptoschool()
print("Singled out EINS! (i think)")
