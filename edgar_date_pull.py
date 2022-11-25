import requests
import urllib
from bs4 import BeautifulSoup
import re
import finding_files
import pandas as pd
import passwords
from datetime import datetime
from sqlalchemy import create_engine
import psycopg2

headers = {'User-Agent': 'causalation, causalation@gmail.com'}

# let's first make a function that will make the process of building a url easy.
def make_url(base_url, comp):
    url = base_url
    # add each component to the base url
    for r in comp:
        url = '{}/{}'.format(url, r)

    return url


# Get the documents submitted for that filing.
base_url = r"https://www.sec.gov/Archives/edgar/data"
filing_numbers = finding_files.naming_files()
filing_numbers = filing_numbers[1]
filing_numbers = [filing_url for sublist in filing_numbers for filing_url in sublist]

list_of_filings_data = []

for filing_links in filing_numbers:
    formatted_filing_number = re.sub('-', '', filing_links)
    filings_url = make_url(base_url, [formatted_filing_number, f'{filing_links}-index.html'])
    # print(filings_url)

    response = requests.get(url=filings_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    html_with_date = soup.find_all('div', {'class': 'info'})
    html_with_date = str(html_with_date)
    html_with_date = html_with_date.partition('>')[2]
    html_with_date = html_with_date.partition('<')[0]

    list_of_filings_data.append((filing_links, filings_url, html_with_date))

# This DF has the links to the html pages where the files reside. If I want to change the scraping process to not
# Use that Edgar download package, I could loop through these links to scrape using beautiful soup here
df_with_dates = pd.DataFrame(list_of_filings_data, columns=['filing_number', 'filing_url', 'filing_date'])
# print(df_with_dates)

# conn_string = passwords.rds_access
#
# db = create_engine(conn_string)
# conn = db.connect()
#
# df.to_sql('sec_filing_dates', con=conn, if_exists='replace',
#           index=False)
# conn = psycopg2.connect(conn_string
#                         )
# conn.autocommit = True
# cursor = conn.cursor()
# conn.close()
# print('done')

