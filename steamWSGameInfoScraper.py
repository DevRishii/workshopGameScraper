import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import threading

# Returns a list of game URLs from the Steam Workshop
def getGameUrls(driver):
    urls = list()
    
    # Get the total number of pages
    totalNumPages = int(driver.find_elements(By.CLASS_NAME, "workshop_apps_paging_pagelink")[-1].text)

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
                print(len(urlList))
                # Click the next page button
                if activePage == i + 1:
                    urls.extend(urlList)
                    print(len(urls))
                    driver.find_element(By.ID, "workshop_apps_btn_next").click()
                    time.sleep(0.3)
                    break  # Exit the loop if the actions were successful
            except selenium.common.exceptions.StaleElementReferenceException:
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
        totalNumPages = int(driver.find_elements(By.CLASS_NAME, 'pagelink')[-1].text)
        print(totalNumPages)
    #If there is only one page
    except selenium.common.exceptions.NoSuchElementException:
        urlList = driver.find_elements(By.CLASS_NAME, "ugc")
        if len(urlList) == 0:
            print('No items found')
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
            print('No items found')
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
                    print('No items found')
                    return items
                hold = list()
                for item in urlList:
                    hold.append(item.get_attribute("href"))
                print(len(hold))

                # time.sleep(0.3)
                items.extend(hold)
                print(len(items))
                print('going to page:',i + 1)
                driver.get(tabUrl + str(i + 1))
                break
            except selenium.common.exceptions.StaleElementReferenceExceptin:
                print("StaleElementReferenceException occurred. Refreshing elements and retrying.")
                continue  # Retry locating the elements

    return items

# Collects item info and adds it to db
def getItemInfo(driver, itemUrl, df, numItems):
    driver.get(itemUrl)
    while True:
        try:
            #get game name
            gameName = driver.find_element(By.CLASS_NAME, 'workshopItemTitle').text
            print("gameName:", gameName)
            #get game id
            gameId = driver.find_element(By.CLASS_NAME, 'breadcrumbs').find_elements(By.TAG_NAME, 'a')[2].get_attribute('href').split('appid=')[-1]
            print("gameId:", gameId)
            #get game link
            gameLink = driver.find_element(By.CLASS_NAME, 'breadcrumbs').find_elements(By.TAG_NAME, 'a')[1].get_attribute('href')
            print("gameLink:", gameLink)
            #get number of items
            noItems = numItems
            print("noItems:", noItems)
            #get number of RTU items
            noRTUItems = numItems #not present on all pages
            print("noRTUItems:", noRTUItems)
            #get item name
            itemName = driver.find_element(By.CLASS_NAME, 'workshopItemTitle').text
            print("itemName:", itemName)
            #get created by
            createdBy = driver.find_element(By.CLASS_NAME, 'friendBlockContent').text
            print("createdBy:", createdBy)

            #get item size, posted time, updated time
            details = driver.find_elements(By.CLASS_NAME, 'detailsStatRight')

            #get item size
            itemSize = details[0].text
            print("itemSize:", itemSize)
            #get posted time
            postedTime = details[1].text
            print("postedTime:", postedTime)
            #get updated time
            if len(details) == 3:
                updatedTime = details[2].text
            else:
                updatedTime = 'N/A'
            print("updatedTime:", updatedTime)
            #get item description
            itemDesc = driver.find_element(By.CLASS_NAME, 'workshopItemDescription').text
            print("itemDesc:", itemDesc)
            #get is curated
            # isCurated = driver.find_element(By.CLASS_NAME, 'detailsStatRight').text
            isCurated = 'N/A' #not present on all pages
            print("isCurated:", isCurated)
            #get is RTU
            isRTU = 'N/A' #not present on all pages
            print("isRTU:", isRTU)
            #get number of unique visitors
            noUniqVis = driver.find_element(By.XPATH, '//*[@id="rightContents"]/div/div[2]/table/tbody/tr[1]/td[1]').text
            print("noUniqVis:", noUniqVis)
            #get number of favorites
            nofavs = driver.find_element(By.XPATH, '//*[@id="rightContents"]/div/div[2]/table/tbody/tr[3]/td[1]').text
            print("nofavs:", nofavs)
            #get number of subscriptions
            noSubs = driver.find_element(By.XPATH, '//*[@id="rightContents"]/div/div[2]/table/tbody/tr[2]/td[1]').text
            print("noSubs:", noSubs)
            #get reviews
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
            print('rating:', rating)
            break
        except selenium.common.exceptions.StaleElementReferenceException:
            print("StaleElementReferenceException occurred. Refreshing elements and retrying.")
            continue
    with csv_lock:
        addToDB(gameName,gameId,gameLink,noItems,noRTUItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,noUniqVis,nofavs,noSubs,rating,df) 

#adds entries to db
def addToDB(gameName,gameId,gameLink,noItems,noRTUItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,noUniqVis,nofavs,noSubs,rating,df):
    #adds row to db
    df.loc[len(df)] = [gameName,gameId,gameLink,noItems,noRTUItems,itemName,createdBy,itemSize,postedTime,updatedTime,itemDesc,isCurated,isRTU,noUniqVis,nofavs,noSubs,rating]
    df.to_csv('workshopGameScraper/workshopDB.csv', index=False)

#worker function for multithreading
def worker(gameUrls, start, end):
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()
    df = pd.read_csv('../workshopDB.csv')
    for game in gameUrls[start:end]:
        driver.get(game)
        browseTab = driver.find_element(By.XPATH, '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div[3]/div/div[2]/div[2]/a')
        # Gets a list of all the links in the browse tab and grabs the ones that are links
        browseList = [x + '&p=' for i, x in enumerate(browseTab.get_attribute('data-dropdown-html').split('\"')) if i % 2 == 1]
        for tabLink in browseList:
            driver.get(tabLink)
            print(tabLink)
            try:
                numItems = driver.find_element(By.CLASS_NAME, 'workshopBrowsePagingInfo').text.split(' ')[-2]
            except:
                numItems = 0
            print('Num of Items is: ', numItems)
            gameItems = getItems(driver, tabLink)
            print(gameItems)
            print(len(gameItems))
            if len(gameItems) != 0:
                for item in gameItems:
                    getItemInfo(driver, item, df, numItems)
    driver.quit()

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()
df = pd.read_csv('../workshopDB.csv')
driver.get("https://steamcommunity.com/workshop/?browsesort=Alphabetical&browsefilter=Alphabetical&p=1")

# # Get the total number of pages
# totalNumPages = int(driver.find_elements(By.CLASS_NAME, "workshop_apps_paging_pagelink")[-1].text)
#gets the total number of games
totalNumGames = driver.find_element(By.XPATH, "//*[@id=\"workshop_apps_total\"]").text.split(',')
#gets rid of the ',' in the number
totalNumGames = int(''.join(x for x in totalNumGames if x.isdigit()))
print(totalNumGames)


gameUrls = getGameUrls(driver)
print(gameUrls)
# gameUrls = ['https://steamcommunity.com/app/1905530/workshop/']

# Define the number of threads you want to use
num_threads = 4
# Create a lock to prevent multiple threads from writing to the CSV file simultaneously
csv_lock = threading.Lock()
# Split the gameUrls list into chunks for each thread
chunk_size = totalNumGames // num_threads
threads = []

# Create and start worker threads
for i in range(num_threads):
    start = i * chunk_size
    end = (i + 1) * chunk_size if i != num_threads - 1 else len(gameUrls)
    thread = threading.Thread(target=worker, args=(gameUrls, start, end))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

# for game in gameUrls:
#     driver.get(game)
#     browseTab = driver.find_element(By.XPATH, '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div[3]/div/div[2]/div[2]/a')
#     # Gets a list of all the links in the browse tab and grabs the ones that are links
#     browseList = [x + '&p=' for i, x in enumerate(browseTab.get_attribute('data-dropdown-html').split('\"')) if i % 2 == 1]
#     for tabLink in browseList:
#         driver.get(tabLink)
#         print(tabLink)
#         try:
#             numItems = driver.find_element(By.CLASS_NAME, 'workshopBrowsePagingInfo').text.split(' ')[-2]
#         except:
#             numItems = 0
#         print('Num of Items is: ', numItems)
#         gameItems = getItems(driver, tabLink)
#         print(gameItems)
#         print(len(gameItems))
#         if len(gameItems) != 0:
#             for item in gameItems:
#                 getItemInfo(driver, item, df, numItems)
    

# Print the final results
# print(len(gameUrls))
# print(totalNumGames)

# Quit the driver
driver.quit() 
