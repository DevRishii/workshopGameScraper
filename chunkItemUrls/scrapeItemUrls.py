import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import os
import pandas as pd
import sys


# Collects item info and adds it to db
def getItemInfo(driver, itemUrl, noItems, gameName, itemType, gameLink, gameId):
    driver.get(itemUrl)
    
    try:
        #get item name
        itemName = driver.find_element(By.CLASS_NAME, 'workshopItemTitle').text
    except Exception as e:
        sendToErrors(str(e), itemUrl, 'itemName could not be found')
        itemName = 'N/A'
    #print("itemName:", itemName)
    

    try:
        #get created by
        createdByList = driver.find_elements(By.CLASS_NAME, 'friendBlockContent')
        createdBy = ''
        for name in createdByList:
            x = name.text
            x = x.replace('Offline', '').replace('Online','').split('In-Game')[0].strip()
            createdBy += x + ',\n'
        createdBy = createdBy.strip(',\n')
    except Exception as e:
        sendToErrors(str(e), itemUrl, 'createdBy could not be found')
        createdBy = 'N/A'
    #print("createdBy:", createdBy)

    if itemType == 'Collections':
        try:
            details = driver.find_elements(By.CLASS_NAME, 'detailsStatRight')
            #get item size
            itemSize = 'N/A'
            #print("itemSize:", itemSize)
            
            #get posted time
            postedTime = details[3].text
            #print("postedTime:", postedTime)
            
            #get updated time
            if len(details) == 5:
                updatedTime = details[4].text
            else:
                updatedTime = 'N/A'
            #print("updatedTime:", updatedTime)
        except Exception as e:
            sendToErrors(str(e), itemUrl, 'itemSize, postedTime, updatedTime could not be found')
            itemSize = 'N/A'
            postedTime = 'N/A'
            updatedTime = 'N/A'
    else:
        try:
            #get item size, posted time, updated time
            details = driver.find_elements(By.CLASS_NAME, 'detailsStatRight')

            #get item size
            itemSize = details[0].text
            #print("itemSize:", itemSize)
            #get posted time
            postedTime = details[1].text
            #print("postedTime:", postedTime)
            #get updated time
            if len(details) == 3:
                updatedTime = details[2].text
            else:
                updatedTime = 'N/A'
            #print("updatedTime:", updatedTime)
        except Exception as e:
            sendToErrors(str(e), itemUrl, 'itemSize, postedTime, updatedTime could not be found')
            itemSize = 'N/A'
            postedTime = 'N/A'
            updatedTime = 'N/A'

    try:
        #get item description
        itemDesc = driver.find_element(By.CLASS_NAME, 'workshopItemDescription').text
        #print("itemDesc:", itemDesc)
    except Exception as e:
        # sendToErrors(str(e), itemUrl, 'itemDesc could not be found')
        itemDesc = 'N/A'
        #print("itemDesc:", itemDesc)

    #get is curated and is RTU and is accepted
    try:
        gltext = driver.find_element(By.CLASS_NAME, 'greenlight_controls').text
        if 'Would you like' in gltext: 
            isCurated = 'Yes'
            isRTU = 'No'
            isAccepted = 'No'
        elif 'This item has been accepted' in gltext:
            isCurated = 'Yes'
            isRTU = 'No'
            isAccepted = 'Yes'
        else:
            sendToErrors(gltext, itemUrl, 'Not accepted or curated, this is the text:')
            isCurated = 'N/A'
            isRTU = 'N/A'
            isAccepted = 'N/A'
            #print('Not accepted or curated, this is the text:', gltext)
    except:
        isCurated = 'No'
        isRTU = 'Yes'
        isAccepted = 'No'

    
    #Get number of unique visitors, favorites, subscriptions
    try:
        noUniqVis = 'N/A'
        noSubs = 'N/A'
        noFavs = 'N/A'
        
        panels = driver.find_element(By.CLASS_NAME, 'stats_table')
        #print('Obtained stats_table')
        panels = panels.find_elements(By.TAG_NAME, 'tr')
        
        rows = [row.text for row in panels]
        for row in rows:
            if 'Unique Visitors' in row:
                noUniqVis = row.split(' ')[0]
            elif 'Current Subscribers' in row:
                noSubs = row.split(' ')[0]
            elif 'Current Favorites' in row:
                noFavs = row.split(' ')[0]
            else:
                print('NEW ROW DATA: ', row, '\nitemUrl:', itemUrl)
                sendToErrors('NEW ROW DATA: ' + row, itemUrl, 'Extra row data found while getting noUniqVis, noSubs, noFavs')
    except:
        #print('Failed to obtain stats_table')
        try:
            panel = driver.find_element(By.CLASS_NAME, 'detailsStatsContainerLeft')
            #print('Obtained detailsStatsContainerLeft')
            # stats = panel.find_elements(By.CLASS_NAME, 'detailsStatLeft')
            # print('stats:', stats)
    
            stats = panel.text.split('\n')
            # print('stats:', stats)
            
            for row in details:
                if 'Unique Visitors' in row.text:
                    noUniqVis = stats[0]
                elif 'Current Subscribers' in row.text:
                    noSubs = stats[1]
                elif 'Current Favorites' in row.text:
                    if itemType == 'Collections':
                        #Collections have noFavs in the 2nd index
                        noFavs = stats[1]
                    else:
                        noFavs = stats[2]
                    # print('INSIDE CF:', noFavs ,stats[2])
                elif 'Total Unique Favorites' in row.text:
                    pass
                else:
                    #print('NEW ROW DATA: ', row.text)
                    # sendToErrors('NEW ROW DATA: ' + row.text, itemUrl, 'Extra row data found while getting noUniqVis, noSubs, noFavs')
                    pass
            
        except Exception as e:
            sendToErrors(str(e), itemUrl, 'noUniqVis, noSubs, noFavs could not be found')
            #print('noUniqVis, noSubs, noFavs could not be found\n', str(e))
            noUniqVis = 'N/A'
            noSubs = 'N/A'
            noFavs = 'N/A'
        
    try:
        #get ratings
        ratingLink = driver.find_element(By.CSS_SELECTOR, '#detailsHeaderRight > div > div > img').get_attribute('src').split('/')[-1]
        if ratingLink == '1-star_large.png?v=2':
            rating = '1'
        elif ratingLink == '2-star_large.png?v=2':
            rating = '2'
        elif ratingLink == '3-star_large.png?v=2':
            rating = '3'
        elif ratingLink == '4-star_large.png?v=2':
            rating = '4'
        elif ratingLink == '5-star_large.png?v=2':
            rating = '5'
        else:
            rating = 'N/A'
    except Exception as e:
        # sendToErrors(str(e), itemUrl, 'rating could not be found')
        rating = 'N/A'
        ratingLink = 'N/A'
        

    #print('Sending to DB')
    sendToDB(gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating)


# Gets item urls from file and returns a list of urls and a boolean indicating if there are more files to read
def getItemFromFile(fname: str, fileNum: int) -> (list, bool):
    # Check if the file exists before opening it
    if os.path.isfile(fname + str(fileNum) + '.txt'):
        # Read the file and store URLs in a list
        with open(fname + str(fileNum) + '.txt', 'r') as file:
            gameItems = [line.strip() for line in file]
            
        if os.path.isfile(fname + str(fileNum + 1) + '.txt'):
            return gameItems, True
        else:
            return gameItems, False

    else:
        return [], False

def sendToDB(gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating):
    #adds row to db
    db_df.loc[len(db_df)] = [gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating]
    #print('after:',df)
    db_df.to_csv(csvFile, index=False)
    print('SUCCESSFULLY ADDED TO DB')

def sendToErrors(errorMessage,link,note):
    #adds row to error dataframe
    err_df.loc[len(err_df)] = [errorMessage,link,note]
    err_df.to_csv(errorFile, index=False)


# Create a new instance of the Chrome driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

# Create a WebDriver instance
driver = webdriver.Chrome(options=chrome_options)

# gameNum = int(input('1-Arma, 2-Europa, 3-Dota\nEnter the game number: '))
gameNum = int(sys.argv[1])

# tabNum = int(input('\nOptions for each game:\nGame 1 - {0, 1}\nGame 2 - {0, 1}\nGame 3 - {0, 1, 2, 3}\nEnter the tab number: '))
tabNum = int(sys.argv[2])


global csvFile, errorFile
csvFile = 'chunkItemUrls/itemUrls' + str(gameNum) +'.csv'
if not os.path.isfile(csvFile):
    csvFile = 'itemUrls' + str(gameNum) +'.csv'
    if not os.path.isfile(csvFile):
        csvFile = input('Enter the name/path of the csv file to store the item urls: ')
errorFile = 'chunkItemUrls/itemErrors' + str(gameNum) +'.csv'
if not os.path.isfile(errorFile):
    errorFile = 'itemErrors' + str(gameNum) +'.csv'
    if not os.path.isfile(errorFile):
        errorFile = input('Enter the name/path of the csv file to store the errors: ')

global db_df, err_df
db_df = pd.read_csv(csvFile)
err_df = pd.read_csv(errorFile)


#1 is Arma
#2 is Europa
#3 is Dota
gameUrls = ['https://steamcommunity.com/app/107410/workshop/', 
            'https://steamcommunity.com/app/236850/workshop/', 
            'https://steamcommunity.com/app/570/workshop/']

game = gameUrls[gameNum - 1]

driver.get(game)

appId = game.split('/')[-3]
tabList = ['https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=trend&section=readytouseitems&actualsort=mostrecent&p=', 
           'https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=trend&section=collections&p=', 
           'https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=trend&section=mtxitems&p=', 
           'https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=accepted&section=mtxitems&p=1&browsefilter=accepted&p=']

gameName = driver.find_element(By.CLASS_NAME, 'apphub_AppName').text
tabLink = tabList[tabNum]

driver.get(tabLink)

try:
    numItems = driver.find_element(By.CLASS_NAME, 'workshopBrowsePagingInfo').text.split(' ')[-2]
except Exception as e:
    sendToErrors(str(e), tabLink, 'numItems could not be found')
    numItems = 0
#print('Num of Items is: ', numItems)

#get item type
try:
    itemType = driver.find_element(By.CLASS_NAME, 'workshop_browsing_section').text
except Exception as e:
    sendToErrors(str(e), tabLink, 'itemType could not be found')
    itemType = 'N/A'

print('Getting Items from game:', gameName, 'and tab:', itemType)


fName = 'chunkItemUrls/itemUrlsGame' + str(gameNum) + 'Tab' + str(tabNum) + '-'

if not os.path.isfile(fName + '1.txt'):
    fName = 'itemUrlsGame' + str(gameNum) + 'Tab' + str(tabNum) + '-'
    if not os.path.isfile(fName + '1.txt'):
        fName = input('Enter the name/path of the file that stores the item urls: ')
        

nextFile, fileNum = True, 0

while (nextFile):
    fileNum += 1
    gameItems, nextFile = getItemFromFile(fName, fileNum)
    if len(gameItems) != 0:
        for item in gameItems:
            getItemInfo(driver, item, numItems, gameName, itemType, game, appId)
            