import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


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


driver.get('https://steamcommunity.com/sharedfiles/filedetails/?id=2545853797')

# panels = driver.find_element(By.CLASS_NAME, 'stats_table')
# panels = panels.find_elements(By.TAG_NAME, 'tr')
# rows = [row.text for row in panels]

noUniqVis = 'N/A'
noSubs = 'N/A'
nofavs = 'N/A'


details = driver.find_elements(By.CLASS_NAME, 'detailsStatRight')

#get item size
itemSize = 'N/A'
#print("itemSize:", itemSize)
#get posted time
# postedTime = driver.find_element(By.XPATH, '//*[@id="rightContents"]/div[2]/div[4]/div/div[2]/div[1]').text
postedTime = details[3].text
#print("postedTime:", postedTime)
#get updated time
if len(details) == 5:
    updatedTime = details[4].text
else:
    updatedTime = 'N/A'


#Get number of unique visitors, favorites, subscriptions
try:
    panels = driver.find_element(By.CLASS_NAME, 'stats_table')
    print('Obtained stats_table')
    panels = panels.find_elements(By.TAG_NAME, 'tr')
    noUniqVis = 'N/A'
    noSubs = 'N/A'
    noFavs = 'N/A'
    
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
            # sendToErrors('NEW ROW DATA: ' + row, itemUrl, 'Extra row data found while getting noUniqVis, noSubs, noFavs')
except:
    print('Failed to obtain stats_table')
    try:
        panel = driver.find_element(By.CLASS_NAME, 'detailsStatsContainerLeft')
        print('Obtained detailsStatsContainerLeft')
        # stats = panel.find_elements(By.CLASS_NAME, 'detailsStatLeft')
        # print('stats:', stats)
  
        stats = panel.text.split('\n')
        print('stats:', stats)
        
        for row in details:
            print('row:', row.text)
            if 'Unique Visitors' in row.text:
                noUniqVis = stats[0]
            elif 'Current Subscribers' in row.text:
                noSubs = stats[1]
            elif 'Current Favorites' in row.text:
                noFavs = stats[2]
                print('INSIDE CF:', noFavs ,stats[2])
            elif 'Total Unique Favorites' in row.text:
                pass
            else:
                print('NEW ROW DATA: ', row.text)
                # sendToErrors('NEW ROW DATA: ' + row, itemUrl, 'Extra row data found while getting noUniqVis, noSubs, noFavs')
        
    except Exception as e:
        # sendToErrors(str(e), itemUrl, 'noUniqVis, noSubs, noFavs could not be found')
        print('noUniqVis, noSubs, noFavs could not be found\n', str(e))
        noUniqVis = 'N/A'
        noSubs = 'N/A'
        noFavs = 'N/A'



print('Unique Visitors:', noUniqVis)
print('Current Subscribers:', noSubs)
print('Current Favorites:', noFavs)
print('itemSize:', itemSize)
print('postedTime:', postedTime)
print('updatedTime:', updatedTime)



