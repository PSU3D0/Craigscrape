import requests
from bs4 import BeautifulSoup as bs4
import sys

SITES_URL = 'https://www.craigslist.org/about/sites'
SITE = '{0}.craigslist.org'


def retrieveSite(url):
    site = requests.get(url)
    
    if site.status_code != 200:
        print("Site not retrieved properly, check URL")
        sys.exit(1)
    data = bs4(site.text, 'html.parser')
    
    return data


def findString(uInput,text):
    text = text.lower()
    ct = 0
    if type(uInput) == list:
        uInput = [x.lower() for x in uInput]
        for item in uInput:
            ct += text.count(item)
        return ct

    else:
        uInput = uInput.lower()
        return text.count(uInput)


    

def selectCity(city=None,fullADR=True):
    http = 'https://'
    #Will generate list of cities from SITES_URL for user to choose from
    if city == None:
        city = input("Enter city:")
    city.rstrip()
    data = retrieveSite(SITES_URL)
    cityTag = data.find("li", text=city)
    if cityTag.text == city:
        cityURL = cityTag.find("a").get("href")
        cityURL = cityURL[:-1]
        return cityURL
    else:
        print("City not found, try again")
        selectCity()

    print(cityTag)



def selectSearch(category):
    #Matches user inputted category with available ones on main page, then returns search url
    if "/" in category:
        category = category.split("/")[0]
        category = category.rstrip()

    base_URL=selectCity()
    
    data = retrieveSite(base_URL)
    data = data.find("div",id="center")
    categories = data.find_all("li")
    titleL = []
    links = []

    for item in categories:
        title = item.text
        if "/" in title:
            title = title.split("/")[0]
            title = title.rstrip()
            titleL.append(title)
            links.append(item.find("a")["href"])
        else:
            titleL.append(item.text)
            links.append(item.find("a")["href"])
    
    if category not in titleL:
        print("Could not find category, please enter a category from the following list:\n")
        print(*titleL, sep='  -> ')
        selectSearch()
    else:
        sLink = links[titleL.index(category)]
        sLink = base_URL + sLink
        output = [category,sLink]
        return output


def pageScan(url,keywords=None,findMatch=True):
    #Performs all info extraction from page, ideally works across ALL listings
    page = retrieveSite(url)
    title = page.find("span",id="titletextonly").text
    location = page.find("div",class_="mapaddress")
    matchFound = None

    if location != None:
        location = location.text
    

    if keywords != None:
        #Dealing with Craiglists annoying html structure
        bodyText = page.find("section",id="postingbody")
        for un in bodyText.find_all("p",class_='print-qrcode-label'):
            un = None
        bodyText = bodyText.text
        bodyText = bodyText.strip("\n")
        bodyMatches = findString(keywords,bodyText)
        if bodyMatches > 0:
            matchFound = True
            return matchFound
        else:
            matchFound = False

    moveInDate = page.find("span", class_="housing_movein_now property_date shared-line-bubble")
    if moveInDate != None:
        moveInDate = moveInDate.text
    #Getting attributes
    attr = page.find_all("p", class_="attrgroup")
    if len(attr) != 0:
        if len(attr) > 1:
            attr = attr[1]
        else:
            attr = attr[0]
        attr = attr.text
        attr = attr.strip("\n")
        attributes = attr.split("\n\n")
        return title, attributes, matchFound
    else:
        return title, matchFound



def listingScrape(category,numResults=5,keywords=None):
    searchType,url = selectSearch(category)
    searchPage = retrieveSite(url)
    i,n = 0,0
    links = {}

    #Title and link
    for link in searchPage.find_all("a",class_="result-title hdrlnk"):
        
        url = link.get("href")
        title = link.text
        if i < numResults:
            price = searchPage.find_all("span",class_="result-price")
            if len(price) != 0:
                price = price[n]
                price = price.text
                n+=1

            if keywords != None:
                if findString(keywords,title) > 0:
                    links[title] = url
                    i+=1
                else:
                    isMatch = pageScan(url,keywords=keywords)
                    if isMatch == True:
                        links[title] = url
                        i+=1
            else:
                links[title] = url
                i+=1

    return links


def Main():
    print("Craigsearch v0.1 \n By Frankie Colson")
    print("Enter number from following list for desired command: \n 1 - Link Scrape")
    uIn = int(input(":")) 

    if uIn == 1:
        userCategory = input("Enter search category:")
        uKeywords = input("Enter keyword(s), if none wanted,press enter:")
        if len(uKeywords) < 2: uKeywords = None
        print(listingScrape(userCategory,keywords=uKeywords))
    else:
        print("Unrecognized command")
        sys.exit(1)

Main()