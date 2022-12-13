#    _____ __________     ____        __        __
#   / ___// ____/ __ \   / __ \____ _/ /_____ _/ /_  ____ _________
#   \__ \/ /   / /_/ /  / / / / __ `/ __/ __ `/ __ \/ __ `/ ___/ _ \
#  ___/ / /___/ ____/  / /_/ / /_/ / /_/ /_/ / /_/ / /_/ (__  )  __/
# /____/\____/_/      /_____/\__,_/\__/\__,_/_.___/\__,_/____/\___/
#
#
#               Created by Darrel (CatRass#5748)

import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPalette, QColor, QIcon
import requests
from bs4 import BeautifulSoup

def SCPScraper(scp):

        #   This function is responsible for scraping the SCP Wiki and collecting all the relevant information for displaying it on the database GUI. Currently it collects:
        #       - Headings
        #       - Paragaphs/Text
        #       - Image Captions
        #   This is accomplished through grabbing a specific pages source code using Requests, and breaking the scraped code with BeautifulSoup

    url = 'https://scp-wiki.wikidot.com/scp-{}'.format(scp)
    htmlSource = requests.get(url)  #   The sites HTML is scraped
    soup = BeautifulSoup(htmlSource.text, 'html.parser')    #   htmlSource is transformed into a bs4 object for analysis
    pageContents = soup.find("div", { "id" : "page-content" })  #   The webpage is redyuced to everything within div "page-content"
                                                                #   ↑ Refer to Folio (Analysis → Research → SCP Wiki Article Structure)
    headingContents = pageContents

    headings = []   #   Regular headings are styled with <strong></strong> tag
    text = []    #   Regular headings are styled with <p></p> tag

    for strongTags in headingContents.find_all("strong"):   #   Find all contents with the <strong></strong> tag
        headings.append(strongTags.get_text())  #   Remove the <strong></strong> tags and append 'headings'

    for i in pageContents.find_all('strong'): i.extract()   #   Remove all <strong></strong> tags from pageContents to properly process only text, with no headings
                                                            #   ↑ This is important as text is structured as <p><strong>Heading</strong>Actual text</p>

    for pTags in pageContents.find_all("p"):    #   Find all contents with the <p></p> tag
        text.append(pTags.get_text())  #   Remove the <p></p> tags and append 'text'

    try:    #   While testing the scraper on SCP-173, it was noticed not all regular SCP Articles have images, and thus would not have captions.
        imageCaptionBlock = pageContents.find("div", { "class" : "scp-image-caption" }) #   Scraping div id "scp-image-caption" to isolate captions
        imageCaption = []   #   In regular SCP articles image caption are formatted with <p></p>
                            #   ↑ This is why it is important to isolate image captions from text as they both use <p> but are in different divs
        for pTags in imageCaptionBlock.find_all("p"):   #   Find all contents with the <p></p> tag
            imageCaption.append(pTags.get_text())   #   Remove the <p></p> tags and append to 'imageCaption'

        if len(imageCaption) > 0:
            for i in imageCaption: text.pop(text.index(i))  #   Remove any image captions from 'text'
                                                            #   ↑ This is done by checking the index of an image caption in 'text' and then popping it
        allContents = {"Headings":headings,"Text":text,"Image Captions":imageCaption,}  #   Compile all lists into an accessible dictionary
    except: #   In case there are no images with captions, execute the following
        allContents = {"Headings":headings,"Text":text}  #   Compile all lists into an accessible dictionary, without image captions

    return allContents  #   Return the dictionary for future access

class Color(QWidget):   #   Debug Widget that shows a coloured square
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.toolSelector = toolSelector(["SCP's","Tales", "GOI's"])

class toolSelector(QComboBox):  #   Editable ComboBox
    def __init__(self,options):
        super(toolSelector,self).__init__()
        self.addItems(options)

class inputBar(QLineEdit):
    def __init__(self,placeHolderText,returnFunction):
        super(inputBar,self).__init__()
        self.setMaxLength(4)
        self.setPlaceholderText(placeHolderText)
        self.returnPressed.connect(returnFunction)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('icon.ico'))
        self.toolSelector = toolSelector(["SCP's","Tales"])
        self.scpInput = inputBar("Enter SCP Number",self.scpSearched)

        self.setWindowTitle("SCP Database")
        #self.setFixedSize(QSize(400, 300))

        self.button = QPushButton("Search", self)
        self.button.setFixedSize(60, 30)
        self.button.clicked.connect(self.scpSearched)

        self.layout = QGridLayout()
        secondaryLayout = QVBoxLayout()
        self.layout.addWidget(self.scpInput, 0,0)
        self.layout.addWidget(self.button, 0,1)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def scpSearched(self):
        scpInfo = SCPScraper(self.scpInput.text())
        print(scpInfo)

        self.scroll = QScrollArea()
        self.scpInformation = QWidget()

        key = 0
        for i in range(0,len(scpInfo['Headings'])):

            self.scpHeadingLabel = QLabel(self.scpInformation)
            self.scpHeadingLabel.setText(scpInfo['Headings'][i])
            self.scpHeadingLabel.setObjectName("Heading")

            self.scpTextLabel = QLabel(self.scpInformation)
            self.scpTextLabel.setText(scpInfo['Text'][i])
            self.scpTextLabel.setObjectName("Text")

            self.layout.addWidget(self.scpHeadingLabel, key, 0)
            self.layout.addWidget(self.scpTextLabel, key, 1)

            key += 1


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
