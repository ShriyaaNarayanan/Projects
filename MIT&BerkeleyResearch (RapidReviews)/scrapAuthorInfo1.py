from requests_html import HTMLSession
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import requests, openpyxl
from datetime import datetime

link = ""
namesAndInfo = {}
s = HTMLSession()
excel  = openpyxl.Workbook()
# ^^ prints out ['Sheet']
# active sheet is where we load the data
sheet = excel.active
sheet.title = 'Authors and Basic Info from PubMed'
sheet.append(['Author Name', 'Affiliation', 'Email'])


class basicAuthorInfoFromPubMed:

    def __init__(self, link):
        self.link = link
        self.namesAndInfo = {}
    #print("Current Time 1 =",datetime.now().strftime("%H:%M:%S"))

    def getAuthorNamesOnly(self):
        names = []
        site = s.get(self.link)
        soup = BeautifulSoup(site.text, 'html.parser')
        place = soup.find(class_="authors-list")
        namesAndDetails = place.find_all(class_ = "authors-list-item")
        for name in namesAndDetails:
            innerclass = name.find(class_ = "full-name")
            if (innerclass):
                stringName = innerclass.get("data-ga-label")
                if stringName:
                    names.append(stringName)
        return names
    
    def getNamesAndInfo(self):
        return self.namesAndInfo
    
    async def pubMedSearch(self):

        names = self.getAuthorNamesOnly()
        #print(names)
        #print("Current Time 1 =",datetime.now().strftime("%H:%M:%S"))
        search_tasks = []
        #print("Inside pubMedSearch")
        async with aiohttp.ClientSession() as session:
            for name in names:
                #print("The name is "+name)
                first_and_last_list = name.split(" ")
                search_url = "https://pubmed.ncbi.nlm.nih.gov/?term="+first_and_last_list[0]
                for i in range(1, len(first_and_last_list)):
                    search_url += "+" + first_and_last_list[i]
                search_url += "&filter=years.2023-2024"
                search_tasks.append(asyncio.create_task(self.fetch_affiliation(session, name, search_url)))

            #print("Current Time 4 =",datetime.now().strftime("%H:%M:%S"))
            results = await asyncio.gather(*search_tasks)
            return results
            #print(self.namesAndLinks)

            
    async def fetch_affiliation(self, session, name, search_url):
        #print(search_url)
        #print("Current Time 5 =",datetime.now().strftime("%H:%M:%S"))
        async with session.get(search_url) as response:
            html = await response.text()
            #print("Current Time 6 =",datetime.now().strftime("%H:%M:%S"))
            #g = basicAuthorInfoFromPubMed(self.link)
            affiliation = None
            soup = BeautifulSoup(html, 'html.parser')
            if (soup.find(class_="single-result-redirect-message") is not None):
                affiliation = await self.getSpecificAuthorNameInfo(search_url, name,session)
            else:
                for div in soup.find_all('div', class_='docsum-content'):
                    linker = div.find('a')['href']
                    linker = "https://pubmed.ncbi.nlm.nih.gov" + linker
                    affiliation = await self.getSpecificAuthorNameInfo(linker, name,session)
                    if affiliation is not None:
                        break

            if affiliation is not None:
                self.namesAndInfo[name] = affiliation
                #print(self.namesAndLinks[name])
                #print(self.namesAndLinks[name])
            else:
                print(name, None)
                self.namesAndInfo[name] = None

    async def getAuthorNamesAndInfo(self):
        site = s.get(self.link)
        soup = BeautifulSoup(site.text, 'html.parser')
        place = soup.find(class_="authors-list")
        namesAndDetails = place.find_all(class_ = "authors-list-item")
        #h = AuthorAffiliationThroughPubMed(link)
        await self.pubMedSearch()
        '''
        self.namesAndInfo = self.getNamesAndInfo()
        for name in namesAndDetails:
            innerclass = name.find(class_ = "full-name")
            stringName = innerclass["data-ga-label"]
            if stringName in self.namesAndInfo:
                if (self.namesAndInfo[stringName]):
                    affiliationListInfo = self.namesAndInfo[stringName]
                    affiliation = affiliationListInfo[0]
                    if len(affiliationListInfo)>1:
                        email = affiliationListInfo[1]
                        sheet.append([stringName, affiliation, email])
                    else:
                        sheet.append([stringName, affiliation])
            else:
                pass
            '''
            #affiliationClass = name.find(class_="affiliation-links")
        print("These are the names: ", self.namesAndInfo)
        #excel.save("Author Names And Info.xlsx")
        #print("Current Time 2 =",datetime.now().strftime("%H:%M:%S"))
    def getSpecificAuthorNameInfoSynchronously(self, name):
        site = s.get(self.link)
        soup = BeautifulSoup(site.text, 'html.parser')
        place = soup.find(class_="authors-list")
        namesAndDetails = place.find_all(class_ = "authors-list-item")
        for namer in namesAndDetails:
            innerclass = namer.find(class_ = "full-name")
            if (innerclass):
                stringName = innerclass.get("data-ga-label")
                #print(stringName)
                if (stringName):
                    if (stringName == name):
                        affiliationClass = namer.find(class_="affiliation-links")
                        if affiliationClass:
                            newAffiliationClass = affiliationClass.find(class_="affiliation-link")
                            affiliationListInfo = newAffiliationClass["title"].split(". ")
                            affiliation = affiliationListInfo[0]
                            if len(affiliationListInfo)>1:
                                email = affiliationListInfo[1]
                            else:
                                self.namesAndInfo [stringName] = affiliationListInfo 
                        else:
                            self.namesAndInfo[stringName] = None
                        #print(affiliationListInfo)
                        try:
                            #print(stringName, affiliationListInfo)
                            return affiliationListInfo
                        except Exception as e:
                            #print(stringName, "No affiliationListInfo - ",e)
                            return None

    async def getSpecificAuthorNameInfo(self,link, name,session):
        #print(name,",",link)
        async with session.get(link) as response:
        #site = s.get(link)
            soup = BeautifulSoup(await response.text(), 'html.parser')
            place = soup.find(class_="authors-list")
            if (place is None):
                print(soup.prettify())
            namesAndDetails = place.find_all(class_ = "authors-list-item")
            for namer in namesAndDetails:
                innerclass = namer.find(class_ = "full-name")
                if (innerclass):
                    stringName = innerclass.get("data-ga-label")
                    #print(stringName)
                    if (stringName):
                        if (stringName == name):
                            affiliationClass = namer.find(class_="affiliation-links")
                            if affiliationClass:
                                newAffiliationClass = affiliationClass.find(class_="affiliation-link")
                                affiliationListInfo = newAffiliationClass["title"].split(". ")
                                affiliation = affiliationListInfo[0]
                                namesAndInfo[stringName] = affiliationListInfo
                            else:
                                namesAndInfo[stringName] = None
                            #print(affiliationListInfo)
                            try:
                                if (stringName == "Noushin Mohammadifard"):
                                    print("AAAAA ", stringName, affiliationListInfo)
                                namesAndInfo[stringName] = affiliationListInfo
                                return affiliationListInfo
                            except Exception as e:
                                #print("AAAAAB ", stringName, "No affiliationListInfo - ",e)
                                return None
                else :
                    print("did not find class full-name")
            
    
    
    
    
                    #print("Did not get value")
        """for name in names:
            first_and_last_list = name.split(" ")
            search_url = "https://pubmed.ncbi.nlm.nih.gov/?term="+first_and_last_list[0]
            for i in range(1, len(first_and_last_list)):
                search_url += "+" + first_and_last_list[i]
            search_url += "&filter=years.2023-2024"
            search_query = s.get(search_url)
            soup = BeautifulSoup(search_query.text, 'html.parser')
            
            for div in soup.find_all('div', class_='docsum-content'):
                linker = div.find('a')['href']
                linker = "https://pubmed.ncbi.nlm.nih.gov"+linker
                affiliation = g.getSpecificAuthorNameInfo(linker, name)
                if (affiliation!=None):
                    self.namesAndLinks[name] = affiliation
                    break
            self.namesAndLinks[name] = None"""
        
    """def findAuthorAffiliationSynchronously(self, name):
        first_and_last_list = name.split(" ")
        search_url = "https://pubmed.ncbi.nlm.nih.gov/?term="+first_and_last_list[0]
        for i in range(1, len(first_and_last_list)):
            search_url += "+" + first_and_last_list[i]
        search_url += "&filter=years.2023-2024"
        search_query = s.get(search_url)
        soup = BeautifulSoup(search_query.text, 'html.parser')
        
        for div in soup.find_all('div', class_='docsum-content'):
            linker = div.find('a')['href']
            linker = "https://pubmed.ncbi.nlm.nih.gov"+linker
            affiliation = self.getSpecificAuthorNameInfoSynchronously( name)
            if (affiliation!=None):
                #namesAndInfo[name] = affiliation
                print(affiliation)
                return affiliation
        return None"""

async def main():
    #g = basicAuthorInfoFromPubMed("https://pubmed.ncbi.nlm.nih.gov/36609584/")
    #await g.getAuthorNamesAndInfo()
    h = basicAuthorInfoFromPubMed("https://pubmed.ncbi.nlm.nih.gov/36215063/")
    #h.findAuthorAffiliationSynchronously("Noushin Mohammadifard")
    #h.findAuthorAffiliationSynchronously("Aleksei Sholokhov")
    await h.getAuthorNamesAndInfo()
    #n = basicAuthorInfoFromPubMed("https://pubmed.ncbi.nlm.nih.gov/23407571/")
    #n.findAuthorAffiliationSynchronously("Geoffrey Johnston")
    #n.getSpecificAuthorNameInfoSynchronously("Christopher M Barker")
    #n.getSpecificAuthorNameInfoSynchronously("Louis Lambrechts")
    #await n.getAuthorNamesAndInfo()

asyncio.run(main())






    
