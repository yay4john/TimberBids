# Import the required packages
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

#
# This function will download the content of the address of the link using the package Playwright.
#
def get_webpage_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state('networkidle')
        result = page.content()
        browser.close()
    return result

#
# This function gets the table body and return a list of rows with data fields.
#
def get_table_body_as_lists(table_obj):
    result = []
    table_body = table_obj.find('tbody')
    table_rows = table_body.find_all('tr')
    for row in table_rows:
        curr_row = []
        row_fields = row.find_all('td')
        for field_obj in row_fields:
            curr_row.append(field_obj.getText().strip())
        result.append(curr_row)
    return result

# Set address to the ODF timber bid results page and download
link = 'https://apps.odf.oregon.gov/Divisions/management/asset_management/ResultsSelection.asp?optDist=Astoria&Arc=Current'
content = get_webpage_content(link)

# Parse
soup = BeautifulSoup(content, 'html.parser')

# Find the first table in the web page
table = soup.find('table')

# Get data from the table head and table body
table_body = get_table_body_as_lists(table)

# Remove the first two sub-lists
del table_body[0:2]

# Convert to a data frame
df = pd.DataFrame(table_body)

print(df)