import sys
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Returns a list of game URLs from the Steam Workshop
def getGameUrls(driver):
    urls = list()
    
    # Get the total number of pages
    totalNumPages = int(driver.find_elements(By.CLASS_NAME, "workshop_apps_paging_pagelink")[-1].text.replace(',',''))
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

# Returns a list of items from the game's page
def getItems(driver, tabUrl):
    items = list()
    #Navigate to the tab
    driver.get(tabUrl + '1')
    # Get the total number of pages
    try:
        totalNumPages = int(driver.find_elements(By.CLASS_NAME, 'pagelink')[-1].text.replace(',',''))
        #print(totalNumPages)
    #If there is only one page
    except selenium.common.exceptions.NoSuchElementException:
        urlList = driver.find_elements(By.CLASS_NAME, "ugc")
        if len(urlList) == 0:
            #print('No items found')
            return items
        hold = list()
        for item in urlList:
            hold.append(item.get_attribute("href"))
        # time.sleep(0.3)
        items.extend(hold)
        return items
    #If there are no items
    except IndexError:
        urlList = driver.find_elements(By.CLASS_NAME, "ugc")
        if len(urlList) == 0:
            #print('No items found')
            return items
        hold = list()
        for item in urlList:
            hold.append(item.get_attribute("href"))
        # time.sleep(0.3)
        items.extend(hold)
        return items
    #loop through all pages
    for i in range(1, totalNumPages + 1):
        while True:
            try:
                urlList = driver.find_elements(By.CLASS_NAME, "ugc")
                if len(urlList) == 0:
                    #print('No items found')
                    return items
                hold = list()
                for item in urlList:
                    hold.append(item.get_attribute("href"))
                #print(len(hold))

                # time.sleep(0.3)
                items.extend(hold)
                #print(len(items))
                #print('going to page:',i + 1)
                driver.get(tabUrl + str(i + 1))
                break
            except selenium.common.exceptions.StaleElementReferenceExceptin:
                print("StaleElementReferenceException occurred. Refreshing elements and retrying.")
                continue  # Retry locating the elements

    return items

# Collects item info and adds it to db
def getItemInfo(driver, itemUrl, df, noItems, gameName, itemType, gameLink, gameId, csvFile):
    driver.get(itemUrl)
    
    # while True:
    #     try:
    #         #get game id
    #         gameId = driver.find_element(By.CLASS_NAME, 'breadcrumbs').find_elements(By.TAG_NAME, 'a')[2].get_attribute('href').split('appid=')[-1]
    #         break
    #     except:
    #         pass
    #     #print("gameId:", gameId)
    
    # try:
    #     #get game link
    #     gameLink = driver.find_element(By.CLASS_NAME, 'breadcrumbs').find_elements(By.TAG_NAME, 'a')[1].get_attribute('href')
    # except:
    #     pass
    #     #print("gameLink:", gameLink)
  
    
    # #get number of items
    # noItems = numItems
    # #print("noItems:", noItems)
    

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
                #print('NEW ROW DATA: ', row)
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
    sendToDB(gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating,df,csvFile)

def sendToDB(gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating,df,csvFile):
    #adds row to db
    df.loc[len(df)] = [gameName,gameId,gameLink,itemType,noItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,isAccepted,noUniqVis,noFavs,noSubs,rating]
    #print('after:',df)
    df.to_csv(csvFile, index=False)
    #print('SUCCESSFULLY ADDED TO DB')

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


# df = pd.read_csv('workshopDB.csv')
driver.get("https://steamcommunity.com/workshop/?browsesort=Alphabetical&browsefilter=Alphabetical&p=1")

#gets the total number of games
totalNumGames = driver.find_element(By.XPATH, "//*[@id=\"workshop_apps_total\"]").text
#gets rid of the ',' in the number
totalNumGames = int(totalNumGames[0:1] + totalNumGames[2:])

#chunk number given from command line argument in position 2
CHUNK_NUM = int(sys.argv[1])

filename = 'chunkGameUrls' + str(CHUNK_NUM) + '.txt'
csvFile = 'workshopDBChunk' + str(CHUNK_NUM) + '.csv'
df = pd.read_csv(csvFile)

print('Getting Game URLs')
gameUrls = list()

with open(filename, 'r') as f:
    lines = f.readlines()
    for line in lines:
        gameUrls.append(line.strip('\n'))
print('Game URLs obtained, total of:', len(gameUrls))

# gameUrls = getGameUrls(driver)

for game in gameUrls:
    driver.get(game)
    browseTab = driver.find_element(By.XPATH, '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div[3]/div/div[2]/div[2]/a')
    # Gets a list of all the links in the browse tab and grabs the ones that are links
    # browseList = [x + '&p=' for i, x in enumerate(browseTab.get_attribute('data-dropdown-html').split('\"')) if i % 2 == 1]
    # print(browseList)
    appId = game.split('/')[-3]
    browseList = ['https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=trend&section=readytouseitems&p=', 'https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=trend&section=collections&p=', 'https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=trend&section=mtxitems&p=', 'https://steamcommunity.com/workshop/browse/?appid='+ appId +'&browsesort=accepted&section=mtxitems&p=1&browsefilter=accepted&p=']
    gameName = driver.find_element(By.CLASS_NAME, 'apphub_AppName').text
    for tabLink in browseList:
        driver.get(tabLink)
        #print(tabLink)
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
        gameItems = getItems(driver, tabLink)
        #print('Items obtained, total of:', len(gameItems))

        if len(gameItems) != 0:
            #print('Getting Item Info')
            for item in gameItems:
                getItemInfo(driver, item, df, numItems, gameName, itemType, game, appId, csvFile)
    

# Quit the driver
driver.quit() 
