# Import the required packages
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Set address to the ODF timber bid results page and download
link = 'https://apps.odf.oregon.gov/Divisions/management/asset_management/ResultsSelection.asp?optDist=Astoria&Arc=Current'
page = requests.get(link).text

# Parse
soup = BeautifulSoup(page, 'html.parser')

# Find the subtables that contain auction details and store them in a list
tables = soup.find_all('table',attrs={'width':'710'})

# Create empty dataframe to hold details
df = pd.DataFrame(columns=['SaleName','SaleID','BidOpening','Link'])

# for each table in the list, pull out each row and its columns
for tb in tables:
    for row in tb.find_all('tr'):
        columns = row.find_all('td')

        # if the column is not an empty list, grab the 4 fields and append them to the df
        if(columns != []):
            SaleName = columns[0].text.strip()
            SaleID = columns[1].text.strip()
            BidOpening = columns[2].text.strip()
            Link = columns[3].form['action']

            df = df.append({'SaleName': SaleName,  'SaleID': SaleID, 'BidOpening': BidOpening, 'Link': Link}, ignore_index=True)

print(df)