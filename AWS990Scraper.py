from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET

def loadRSS():
    #Get Data From a URL
    url = "https://pp-990-xml.s3.us-east-1.amazonaws.com/202201329349306075_public.xml?response-content-disposition=inline&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA266MJEJYTM5WAG5Y%2F20231001%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231001T212351Z&X-Amz-Expires=1800&X-Amz-SignedHeaders=host&X-Amz-Signature=e432c7f5936296533914b3ac6d7a6829deba0e256ec46cb7e878233dcff20a52"
    xml = requests.get(url)
    with open('boarddirectors.xml', 'wb') as f:
        f.write(xml.content)



def parseXML(xmlfile):
    #Create element tree object
    tree = ET.parse(xmlfile)
    #Get root element
    root = tree.getroot
    print(root)
    #Creates empty list for members
    boardMembers = []

    #Iterate Faculty
    #for item in root.findall()


#load rss from web to update existing xml
loadRSS()
#Parse the XML File
boardMembers = parseXML("boarddirectors.xml")

