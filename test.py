import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# driver = webdriver.Chrome()

# Create a new instance of the Chrome driver
chrome_options = Options()
chrome_options.add_argument("--headless")

chromedriver_path = "chromedriver.exe"

# Create a WebDriver instance
driver = webdriver.Chrome(options=chrome_options)



driver.get('https://steamcommunity.com/sharedfiles/filedetails/?id=2545853797')

# panels = driver.find_element(By.CLASS_NAME, 'stats_table')
# panels = panels.find_elements(By.TAG_NAME, 'tr')
# rows = [row.text for row in panels]

noUniqVis = 'N/A'
noSubs = 'N/A'
nofavs = 'N/A'

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
        panel = driver.find_elements(By.CLASS_NAME, 'detailsStatsContainerLeft')
        print('Obtained detailsStatsContainerLeft')
        print('panel.text:', panel.text)
        stats = panel.text.split('\n')
        print('stats:', stats)
        noUniqVis = stats[0]
        noSubs = stats[1]
        noFavs = stats[2]
    except Exception as e:
        # sendToErrors(str(e), itemUrl, 'noUniqVis, noSubs, noFavs could not be found')
        print('noUniqVis, noSubs, noFavs could not be found\n', str(e))
        noUniqVis = 'N/A'
        noSubs = 'N/A'
        noFavs = 'N/A'



print('Unique Visitors:', noUniqVis)
print('Current Subscribers:', noSubs)
print('Current Favorites:', nofavs)

