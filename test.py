import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://steamcommunity.com/sharedfiles/filedetails/?id=1674170119')

# panels = driver.find_element(By.CLASS_NAME, 'stats_table')
# panels = panels.find_elements(By.TAG_NAME, 'tr')
# rows = [row.text for row in panels]

noUniqVis = 'N/A'
noSubs = 'N/A'
nofavs = 'N/A'

#Get number of unique visitors, favorites, subscriptions
try:
    panels = driver.find_element(By.CLASS_NAME, 'stats_table')
    panels = panels.find_elements(By.TAG_NAME, 'tr')
    rows = [row.text for row in panels]
    for row in rows:
        if 'Unique Visitors' in row:
            noUniqVis = row.split(' ')[0]
        elif 'Current Subscribers' in row:
            noSubs = row.split(' ')[0]
        elif 'Current Favorites' in row:
            nofavs = row.split(' ')[0]
        else:
            print('NEW ROW DATA: ', row)
except Exception as e:
    try:
        panel = driver.find_element(By.CLASS_NAME, 'detailsStatsContainerLeft')
        stats = panel.text.split('\n')
        noUniqVis = stats[0]
        noSubs = stats[1]
        nofavs = stats[2]
    except:
        print('NO STATS FOUND')



print('Unique Visitors:', noUniqVis)
print('Current Subscribers:', noSubs)
print('Current Favorites:', nofavs)

