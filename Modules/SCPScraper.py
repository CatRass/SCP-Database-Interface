import requests
import urllib.request
from bs4 import BeautifulSoup
import inspect

def scraper(scp):

        #   This function is responsible for scraping the SCP Wiki and collecting all the relevant information for displaying it on the database GUI. Currently it collects:
        #       - Headings  (<strong></strong>)
        #       - Paragaphs/Text (<p></p>)
        #       - Image Captions
        #   This is accomplished through grabbing a specific pages source code using Requests, and breaking the scraped code with BeautifulSoup

    url = 'https://scp-wiki.wikidot.com/scp-{}'.format(scp)
    htmlSource = requests.get(url)  #   The sites HTML is scraped
    soup = BeautifulSoup(htmlSource.text, 'html.parser')    #   htmlSource is transformed into a bs4 object for analysis
    pageContents = soup.find("div", { "id" : "page-content" })  #   The webpage is redyuced to everything within div "page-content"
                                                                #   ↑ Refer to Folio (Analysis → Research → SCP Wiki Article Structure)
    relevantPageContents = pageContents.find_all("p")    #   Find all contents with the <p></p> tag

    allContents = {}
    currentKey = "None" #   In case text doesnt have a heading, the previous one will be used

    removableText = [
    "« SCP-{previous} | SCP-{current} | SCP-{next} »".format(previous="00"+str(int(scp)-1),current="00"+str(int(scp)),next="00"+str(int(scp)+1))]
    # print(removableText)

    def textRemover(currentEntry):
        for i in removableText:
            # print(i)
            if i == currentEntry:
                currentEntry = "Cring"

    for i in range(0,len(relevantPageContents)):

        # TODO: Fix issues with similar non-none <strong></strong> headings being put into one variable such as the case for SCP-163


        try:    #   Not every piece of text will have a heading, hence a try except statement in case it does not.
            currentTitle = relevantPageContents[i].find('strong')   #   If a heading is found add to variable
        except:
            currentTitle = None #   If a heading not found, make None

        currentText = relevantPageContents[i]   #   Set text to the current item

        if currentTitle != None:
            for strong in currentText.find_all('strong'): strong.extract()
            for pTags in currentText.find_all("p"):    #   Find all contents with the <p></p> tag
                currentText = currentText.get_text() #   Remove <p></p> tags

            # textRemover(currentText.text)
            # print(currentText)

            allContents[currentTitle.text]=currentText.text #   Append text into dictionary
            currentKey = currentTitle.text  #   Set the previous key in case next item has no heading
        else:
            try:    #   In case this is the first item without a heading, we use try/except
                # textRemover(currentText)
                # print(currentText)
                allContents[currentKey]+=(currentText.text+"\n\n")  #   Add to previous heading
            except:
                # textRemover(currentText)
                # print(currentText)
                allContents[currentKey]=currentText.text    #   If no previous heading, create new one with currrentKey

    try:
        imageContents = soup.find("div", { "class" : "scp-image-block block-right" })
        relevantImageContents = imageContents.find("img", { "class" : "image" })
        print(relevantImageContents["src"])
        allContents["Image"] = relevantImageContents["src"]
    except:
        allContents["Image"] = None

    print("SCP {} Scraped Info:".format(str(scp)),allContents)
    return allContents
