import re
import nltk
nltk.download('words')
from nltk.corpus import words


def cleanFile():
    page = open("C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\yellowBookStuff\\fileReads\\ocrresultsprocessed.txt", "r")
    pagelist = page.readlines()
    pagecont = pagelist[0]
    pagecont = pagecont.split(",")
    pagestrip = [i.strip('"') for i in pagecont]
    pagestrip = [x for x in pagestrip if str(x).strip() != '']
    pagestrip = [x.strip('" ').strip("[]") for x in pagestrip if x.strip('" '.strip("[]"))]
    regpage = [x for x in pagestrip if re.search(r'\w', x)]
    pattern = r'\.+'
    cleanreg = [re.sub(pattern, '', x) for x in regpage]
    
    #now trying to only use actual words
    removedList = []
    for x in cleanreg:
        if x in words.words():
            removedList.append(x)
    cleanedlist = [cleantext(x) for x in cleanreg]
    print(cleanedlist)


def cleantext(text):
    # Define a regular expression pattern to keep only alphanumeric and specific characters
    pattern = re.compile(r'[^A-Za-z0-9(),.:\-@;\s\[\]]')
    return re.sub(pattern, '', text)




print("Main method testing:")
cleanFile()