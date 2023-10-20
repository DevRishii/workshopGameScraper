import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

#Gets the game urls from steam workshop
def getGameUrls(driver):
    urls = list()
    # Get the total number of pages
    totalNumPages = int(driver.find_elements(By.CLASS_NAME, "workshop_apps_paging_pagelink")[-1].text)
    #print("Total Number of Pages:", totalNumPages)

    for i in range(totalNumPages):
        while True:
            try:
                gameList = driver.find_elements(By.CLASS_NAME, "app")
                activePage = int(driver.find_element(By.CSS_SELECTOR, "#workshop_apps_links > span.workshop_apps_paging_pagelink.active").text)
                print("Current Page(IDE):", i + 1)
                print("Current Page(Browser):", activePage)
                
                urlList = list()
                # Get the URLs of every game in workshop
                for game in gameList:
                    urlList.append(game.get_attribute("onclick")[19:-1])
                #print(len(urlList))
                # Click the next page button
                if activePage == i + 1:
                    urls.extend(urlList)
                    #print(len(urls))
                    driver.find_element(By.ID, "workshop_apps_btn_next").click()
                    time.sleep(0.3)
                    break  # Exit the loop if the actions were successful
            except:
                print("StaleElementReferenceException occurred. Refreshing elements and retrying.")
                continue  # Retry locating the elements

    return urls


# Collects item info and adds it to db
def getItemInfo(driver, itemUrl, df, numItems, gameName, itemType):
    driver.get(itemUrl)
    
    #get game id
    gameId = driver.find_element(By.CLASS_NAME, 'breadcrumbs').find_elements(By.TAG_NAME, 'a')[2].get_attribute('href').split('appid=')[-1]
    #print("gameId:", gameId)
    
    #get game link
    gameLink = driver.find_element(By.CLASS_NAME, 'breadcrumbs').find_elements(By.TAG_NAME, 'a')[1].get_attribute('href')
    #print("gameLink:", gameLink)
    
    #get number of items
    noItems = numItems
    #print("noItems:", noItems)
    
    #get item name
    itemName = driver.find_element(By.CLASS_NAME, 'workshopItemTitle').text
    #print("itemName:", itemName)
    
    #get created by
    createdByList = driver.find_elements(By.CLASS_NAME, 'friendBlockContent')
    createdBy = ''
    for name in createdByList:
        x = name.text
        x = x.replace('Offline', '').replace('Online','').split('In-Game')[0].strip()
        createdBy += x + ',\n'
    createdBy = createdBy.strip(',\n')
    #print("createdBy:", createdBy)

    if itemType == 'Collections':
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
    else:
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
            print('Not accepted or curated, this is the text:', gltext)
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
        print('Obtained stats_table')
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
                print('NEW ROW DATA: ', row)
                sendToErrors('NEW ROW DATA: ' + row, itemUrl, 'Extra row data found while getting noUniqVis, noSubs, noFavs')
    except:
        print('Failed to obtain stats_table')
        try:
            panel = driver.find_element(By.CLASS_NAME, 'detailsStatsContainerLeft')
            print('Obtained detailsStatsContainerLeft')
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
                    print('NEW ROW DATA: ', row.text)
                    # sendToErrors('NEW ROW DATA: ' + row.text, itemUrl, 'Extra row data found while getting noUniqVis, noSubs, noFavs')
            
        except Exception as e:
            sendToErrors(str(e), itemUrl, 'noUniqVis, noSubs, noFavs could not be found')
            print('noUniqVis, noSubs, noFavs could not be found\n', str(e))
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


    print('Sending to DB')
    sendToDB(gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating,df)

def sendToDB(gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating,df):
    #adds row to db
    df.loc[len(df)] = [gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating]
    #print('after:',df)
    df.to_csv('example.csv', index=False)
    print('SUCCESSFULLY ADDED TO DB')

def sendToErrors(errorMessage,link,note):
    df = pd.read_csv('errors.csv')
    #adds row to db
    df.loc[len(df)] = [errorMessage,link,note]
    df.to_csv('errors.csv', index=False)


# Create a new instance of the Chrome driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")


# Create a WebDriver instance
driver = webdriver.Chrome(options=chrome_options)

# driver = webdriver.Chrome()

itemUrl = 'https://steamcommunity.com/sharedfiles/filedetails/?id=1679883045'
itemType = 'Collections'
gameName = 'test'
df = pd.read_csv('example.csv')

driver.get("https://steamcommunity.com/workshop/?browsesort=Alphabetical&browsefilter=Alphabetical&p=1")

gameUrls = getGameUrls(driver)

#Split gameURLs into 


# driver.get(itemUrl)

# getItemInfo(driver, itemUrl, df, 1, gameName, itemType)

