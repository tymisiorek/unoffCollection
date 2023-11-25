import requests
import time
import json
from bs4 import BeautifulSoup

#defining url
url = "https://projects.propublica.org/nonprofits/organizations/"
urlmod = "https://projects.propublica.org"

#Read from text file with EINS
f = open("R1EINS.txt", "r")
fullText = f.readlines()

# print(fullText)
schoolDict = {}

#Make an array containing only the school names with an available EIN
schoolArray = []
iterator = 0


#Go through the text and add to the dictionary, University name as keys, EIN number as values
for x in fullText:
    x = x[4:].strip()
    x = x.split(':')
    if "N/A" not in x[1]:
        schoolDict[x[0]] = url + x[1].strip()
        schoolArray.append(x[0])
        #print(x[0])

# print(schoolDict)
# print("---------------------")
# print(schoolArray)

#Define a dictionary with the university as key, and the link to xml as a value
schoolXML = {}


for j in schoolDict.values():
    #Make requests every second, as allowed by the robots.txt
    time.sleep(1.01)
    #sending get request to url
    response = requests.get(j)

    #parse the html content with bs4
    soup = BeautifulSoup(response.text, "html.parser")

    #find all anchor tags (links) on the page
    links = soup.find_all("a", class_="btn")

    #Get only the first link with the specified url section, because the first one is always what we want.
    for link in links:
        href = link.get("href")
        #print("this is the href: " + href)
        if '/nonprofits/download' in href:
            schoolXML[schoolArray[iterator]] = urlmod + href
            #print(schoolXML)
            #print(urlmod + href)
            break
    iterator += 1

#Write the contents of schoolXML into a text file

with open('XMList.txt', 'w') as file:
    file.write(json.dumps(schoolXML))

#print(schoolXML)


'''
#sending get request to url
response = requests.get(url)

#parse the html content with bs4
soup = BeautifulSoup(response.text, "html.parser")

#find all anchor tags (links) on the page
links = soup.find_all("a", class_="btn")

#Get only the first link with the specified url section, because the first one is always what we want.
secondaryIt = 0
for link in links:
    href = link.get("href")
    #print("this is the href: " + href)
    if '/nonprofits/download' in href:
        print(href)
        break
'''
 
