# Import the required packages
import requests                     # get html, submit posts
from bs4 import BeautifulSoup       # parse and search through html
import pandas as pd                 # dataframes!
import json                         # convert string to dictionary
import html5lib                     # used to parse the html
import time                         # pause between scrapings, don't want to anger any IT people
import random                       # make the pause randomized, so the scraper looks less... scraper-y

# Create empty dataframes
dfAuctions = pd.DataFrame(columns=['District','SaleName','SaleID','BidOpeningDate','Link','PostInput'])     # list of auctions
dfBids = pd.DataFrame(columns=['SaleID','Bidder','Price','Species','Winner'])                               # list of bids
dfAppraisals = pd.DataFrame(columns=['SaleID','Volume','Species','Price'])                                  # list of appraisals

# manually populate the list of districts
districts = ["Klamath-Lake","Southwest%20Oregon","Western%20Lane","Coos","West%20Oregon","N.%20Cascade",
    "Tillamook","Forest%20Grove","Astoria"]

# Set base address to the ODF timber bid results page
baseURL = 'https://apps.odf.oregon.gov/Divisions/management/asset_management/'

#----------------------------------------------------------------------------------------------------------------------
# The loop below goes through each district page and pulls a list of auctions. We then go to each auction's result page
#  and pull out the appraisal and bid info
#----------------------------------------------------------------------------------------------------------------------
for district in districts:
    link = baseURL + 'ResultsSelection.asp?optDist=' + district + '&Arc=Current'    #assemble the district url
    
    # get the html and parse it
    page = requests.get(link, timeout=10.0).text
    soup = BeautifulSoup(page, 'html5lib')

    tables = soup.find_all('table',attrs={'width':'710'})   # Find the subtables that contain auction details

    # ODF stores each auction in its own table, so iterate through each table and pull the auction details
    for tb in tables:
        for row in tb.find_all('tr'):
            columns = row.find_all('td')

            postString = ''     #initialize the post string

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

                dfAuctions = dfAuctions.append({'District': district,'SaleName': SaleName,  'SaleID': SaleID, 'BidOpeningDate': BidOpeningDate,
                 'Link': Link, 'PostInput': PostInput}, ignore_index=True)

    # Clean spaces and appostrophes out of the link
    dfAuctions['Link'] = dfAuctions['Link'].str.replace(' ','%20')
    dfAuctions['Link'] = dfAuctions['Link'].str.replace("'",'%27')

    # now that we have a list of auctions, go to each auction site and pull appraisal and bid details
    for i in range(len(dfAuctions)):

        # grab the sale url and post info, along with the sale id, which we'll use as a key
        auctionSaleID = dfAuctions.iloc[i,2]
        newURL = dfAuctions.iloc[i,4]
        poststuff = json.loads(dfAuctions.iloc[i,5])

        # get the auction results page html and parse it
        auction = requests.post(newURL,data = poststuff,timeout=10.0).text
        auctionSoup = BeautifulSoup(auction, 'html5lib')

        appraisal = auctionSoup.select('body > p:nth-child(4) > table')     # grab the appraisal table

        # for each table in the list (in this case, just the one), pull out each row and its columns
        for tb in appraisal:
            for row in tb.find_all('tr'):
                columns = row.find_all('td')

                # if the column is not an empty list, grab the 4 main fields, plus the details needed for post request
                if(columns != []):
                    try:
                        # check if this is the header row, ignore if it is
                        if columns[1].text.strip() != 'Species':
                            Volume = columns[0].text.strip()
                            Species = columns[1].text.strip()
                            Price = columns[2].text.strip()

                            dfAppraisals = dfAppraisals.append({'SaleID': auctionSaleID, 'Volume': Volume,  'Species': Species, 'Price': Price}
                            , ignore_index=True)
                    except:
                        dfAppraisals = dfAppraisals.append({'SaleID': auctionSaleID, 'Volume': 'manual',  'Species': 'manual', 'Price': 'manual'}
                            , ignore_index=True)
                        continue

        winner = auctionSoup.select('body > table:nth-child(7)')        # next, get the winning bid details

        # for each table in the list (again, there's only one), pull out each row and its columns
        for each in winner:
            for row in each.find_all('tr'):
                columns = row.find_all('td')
                
                # if the column is not an empty list, grab the 4 main fields, plus the details needed for post request
                if columns != []:
                    try:
                        # check if this is the header row, ignore if it is
                        if columns[2].text.strip() != 'Bid Species':

                            # odf format has the table in tabular format, so the nth row for a bidder will have one fewer column
                            if len(columns)==5:
                                Bidder = columns[0].text.strip()
                                Price = columns[1].text.strip()
                                Species = columns[2].text.strip()

                            else:    
                                Price = columns[0].text.strip()
                                Species = columns[1].text.strip()

                            dfBids = dfBids.append({'SaleID': auctionSaleID, 'Bidder': Bidder,  'Species': Species, 'Price': Price, 'Winner' : 1}
                            , ignore_index=True)
                    except:
                        dfBids = dfBids.append({'SaleID': auctionSaleID, 'Bidder': 'manual',  'Species': 'manual', 'Price': 'manual', 'Winner' : 1}
                            , ignore_index=True)

        otherBids = auctionSoup.select('body > table:nth-child(9)')     # now grab the other bidder details

        # same as above, pull out each row and its columns
        for each in otherBids:
            for row in each.find_all('tr'):
                columns = row.find_all('td')
                
                # if the column is not an empty list, grab the 4 main fields, plus the details needed for post request
                if columns != []:
                    try:
                        # check if this is the header row, ignore if it is
                        if columns[1].text.strip() != 'Bid Species':

                            # odf format has the table in tabular format, so the nth row for a bidder will have one fewer column
                            if len(columns)==5:
                                Bidder = columns[0].text.strip()
                                Species = columns[1].text.strip()
                                Price = columns[2].text.strip()

                            else:    
                                Species = columns[0].text.strip()
                                Price = columns[1].text.strip()

                            dfBids = dfBids.append({'SaleID': auctionSaleID, 'Bidder': Bidder,  'Species': Species, 'Price': Price, 'Winner' : 0}
                            , ignore_index=True)
                    except:
                        dfBids = dfBids.append({'SaleID': auctionSaleID, 'Bidder': 'manual',  'Species': 'manual', 'Price': 'manual', 'Winner' : 0}
                            , ignore_index=True)
        
        time.sleep(random.randrange(5,20)) # pause after grabbing the auction results to ease server load
    
    time.sleep(random.randrange(5,20)) # pause after grabbing the list of auctions to ease server load

print(dfAuctions)
print(dfAppraisals)
print(dfBids)

dfAuctions.to_csv('ODF_Auctions.csv')
dfAppraisals.to_csv('ODF_Appraisals.csv')
dfBids.to_csv('ODF_Bids.csv')