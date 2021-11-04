# Import the required packages
import requests                     # get html, submit posts
from bs4 import BeautifulSoup       # parse and search through html
import pandas as pd                 # dataframes!
import json                         # convert string to dictionary

# Set address to the ODF timber bid results page and download
baseURL = 'https://apps.odf.oregon.gov/Divisions/management/asset_management/'
link = 'https://apps.odf.oregon.gov/Divisions/management/asset_management/ResultsSelection.asp?optDist=Astoria&Arc=Current'
page = requests.get(link, timeout=10.0).text

# Parse
soup = BeautifulSoup(page, 'html.parser')

# Find the subtables that contain auction details and store them in a list
tables = soup.find_all('table',attrs={'width':'710'})

# Create empty dataframe to hold details
df = pd.DataFrame(columns=['SaleName','SaleID','BidOpeningDate','Link','PostInput'])

# for each table in the list, pull out each row and its columns
for tb in tables:
    for row in tb.find_all('tr'):
        columns = row.find_all('td')

        postString = ''

        # if the column is not an empty list, grab the 4 main fields, plus the details needed for post request
        if(columns != []):
            SaleName = columns[0].text.strip()
            SaleID = columns[1].text.strip()
            BidOpeningDate = columns[2].text.strip()
            Link = baseURL + columns[3].form['action']
            # there are 9 fields used in the post request, so build the string that contains them all
            for i in range(9):
                postString = postString + '"' + columns[3].find_all('input')[i]['name'] + '":"' + columns[3].find_all('input')[i]['value'] + '",'
            PostInput = '{' + postString[:-1] + '}'

            df = df.append({'SaleName': SaleName,  'SaleID': SaleID, 'BidOpeningDate': BidOpeningDate, 'Link': Link, 'PostInput': PostInput}, ignore_index=True)

# Clean spaces and appostrophes out of the link
df['Link'] = df['Link'].str.replace(' ','%20')
df['Link'] = df['Link'].str.replace("'",'%27')

# for now, just work with one sale. Will need to use that json bit in the future loop, it converts the string into a dictionary
newURL = df.iloc[0,3]
poststuff = json.loads(df.iloc[0,4])

auction = requests.post(newURL,data = poststuff,timeout=10.0).text
auctionSoup = BeautifulSoup(auction, 'html.parser')

appraisal = auctionSoup.select('body > p:nth-child(4) > table')

# Create empty dataframe to hold details
dfAppraisal = pd.DataFrame(columns=['Volume','Species','Price'])

# for each table in the list, pull out each row and its columns
for tb in appraisal:
    for row in tb.find_all('tr'):
        columns = row.find_all('td')

        # if the column is not an empty list, grab the 4 main fields, plus the details needed for post request
        if(columns != []):
            Volume = columns[0].text.strip()
            Species = columns[1].text.strip()
            Price = columns[2].text.strip()

            dfAppraisal = dfAppraisal.append({'Volume': Volume,  'Species': Species, 'Price': Price}, ignore_index=True)

print(dfAppraisal)

winners = auctionSoup.select('body > table:nth-child(7)')
print(winners)
# Create empty dataframe to hold details
dfBids = pd.DataFrame(columns=['Bidder','Species','Price'])

# for each table in the list, pull out each row and its columns
for tb in winners:
    for row in tb.find_all('tr'):
        columns = row.find_all('td')

        # if the column is not an empty list, grab the 4 main fields, plus the details needed for post request
        if(columns != []):
            Bidder = columns[0].text.strip()
            Species = columns[2].text.strip()
            Price = columns[1].text.strip()

            dfBids = dfBids.append({'Bidder': Bidder,  'Species': Species, 'Price': Price}, ignore_index=True)

print(dfBids)