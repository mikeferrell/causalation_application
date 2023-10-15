import re
import os
import json
import shutil
import pandas as pd
import time
from datetime import datetime
import pathlib
import requests
from bs4 import BeautifulSoup


headers = {'User-Agent': 'causalation, causalation@gmail.com'}


#delete the edgar files from the local folder after the upload/analysis is complete
def delete_edgar_file_paths():
    folder = 'sec-edgar-filings/'
    retain = ["__init__.py"]
    for filename in os.listdir(folder):
        if filename not in retain:
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


#extract the filing number and file name out of the downloaded path information
def naming_files():
    company_name_folders = []
    company_filing_type_folders = []
    filing_date_folders = []
    filing_numbers = []
    file_names = []

    #This all iterates through naming convention to reconstruct the names of the files containing the text, and extracting
    #the filing number associated with the filing that we're viewing. Multiple files may exist
    parent_file_path = pathlib.PurePath(__file__).parent
    top_folder = f'{parent_file_path}/sec-edgar-filings'
    cik_numbers = [companies for companies in os.listdir(top_folder) if os.path.isdir(os.path.join(top_folder, companies))]
    for ciks in cik_numbers:
        new_folder = f'{parent_file_path}/sec-edgar-filings'+"/"+ciks
        company_name_folders.append(new_folder)
    for company_folder_link in company_name_folders:
        file_type = [files for files in os.listdir(company_folder_link) if os.path.isdir(os.path.join(company_folder_link, files))]
        for files in file_type:
            new_file_folder = company_folder_link + "/" + files
            company_filing_type_folders.append(new_file_folder)
    # print(company_filing_type_folders)

    # Creates a new list of the filing dates and then creates a new list of links for each company filing date
    for company_filings in company_filing_type_folders:
        dates = [files for files in os.listdir(company_filings) if os.path.isdir(os.path.join(company_filings, files))]
        for files in dates:
            new_file_folder = company_filings + "/" + files
            filing_date_folders.append(new_file_folder)
        filing_numbers.append(dates)
    # print(filing_numbers)

    for filing_folders in filing_date_folders:
        files_titles = filing_folders + "/full-submission.txt"
        file_names.append(files_titles)
    # print(file_names)
    return file_names, filing_numbers, cik_numbers

# naming_files()

def make_url(base_url, comp):
    url = base_url
    # add each component to the base url
    for r in comp:
        url = '{}/{}'.format(url, r)

    return url


#scrape edgar to find the filing date associated with each filing number we have
def edgar_filing_dates():
    base_url = r"https://www.sec.gov/Archives/edgar/data"
    filing_numbers = naming_files()[1]
    # print(filing_numbers)
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

        # print("links", filing_links, "url", filings_url, "date", html_with_date)
        list_of_filings_data.append((filing_links, filings_url, html_with_date))

    # This DF has the links to the html pages where the files reside. If I want to change the scraping process to not
    # Use that Edgar download package, I could loop through these links to scrape using beautiful soup here
    df_with_dates = pd.DataFrame(list_of_filings_data, columns=['filing_number', 'filing_url', 'filing_date'])
    return df_with_dates


def extract_text_from_sections_10q(link_to_10k):
    raw_10k = open(link_to_10k, "r")
    raw_10k = raw_10k.read()
    # Regex to find <DOCUMENT> tags
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    # Regex to find <TYPE> tag prceeding any characters, terminating at new line
    type_pattern = re.compile(r'<TYPE>[^\n]+')

    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]

    document = {}

    # Create a loop to go through each section type and save only the 10-K section in the dictionary
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-Q':
            document[doc_type] = raw_10k[doc_start:doc_end]

    regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|2|7A|7|8)\.{0,1})|(ITEM\s(1A|1B|2|7A|7|8))')
    matches = regex.finditer(document['10-Q'])

    # Create the dataframe
    test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])

    test_df.columns = ['item', 'start', 'end']
    test_df['item'] = test_df.item.str.lower()
    test_df.replace('&#160;', ' ', regex=True, inplace=True)
    test_df.replace('&nbsp;', ' ', regex=True, inplace=True)
    test_df.replace(' ', '', regex=True, inplace=True)
    test_df.replace('\.', '', regex=True, inplace=True)
    test_df.replace('>', '', regex=True, inplace=True)

    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    pos_dat.set_index('item', inplace=True)

    item_1a_raw = document['10-Q'][pos_dat['start'].loc['item1a']:pos_dat['start'].loc['item2']]

    try:
        item_1a_content = BeautifulSoup(item_1a_raw, 'lxml')
    except Exception:
        print(Exception)
        pass

    return item_1a_content.get_text("\n\n")

def extract_text_from_sections_10k(link_to_10k):
    raw_10k = open(link_to_10k, "r")
    raw_10k = raw_10k.read()
    # Regex to find <DOCUMENT> tags
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    # Regex to find <TYPE> tag prceeding any characters, terminating at new line
    type_pattern = re.compile(r'<TYPE>[^\n]+')

    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]

    document = {}

    # Create a loop to go through each section type and save only the 10-K section in the dictionary
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-K':
            document[doc_type] = raw_10k[doc_start:doc_end]

    regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|2|7A|7|8)\.{0,1})|(ITEM\s(1A|1B|2|7A|7|8))')
    matches = regex.finditer(document['10-K'])

    # Create the dataframe
    test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])

    test_df.columns = ['item', 'start', 'end']
    test_df['item'] = test_df.item.str.lower()
    test_df.replace('&#160;', ' ', regex=True, inplace=True)
    test_df.replace('&nbsp;', ' ', regex=True, inplace=True)
    test_df.replace(' ', '', regex=True, inplace=True)
    test_df.replace('\.', '', regex=True, inplace=True)
    test_df.replace('>', '', regex=True, inplace=True)

    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    pos_dat.set_index('item', inplace=True)

    item_1a_raw = document['10-K'][pos_dat['start'].loc['item1a']:pos_dat['start'].loc['item1b']]
    # item_3_raw = document['10-K'][pos_dat['start'].loc['item3']:pos_dat['start'].loc['item4']]
    item_7_raw = document['10-K'][pos_dat['start'].loc['item7']:pos_dat['start'].loc['item7a']]

    #item_7a_raw = document['10-K'][pos_dat['start'].loc['item7a']:pos_dat['start'].loc['item8']]
    try:
        item_1a_content = BeautifulSoup(item_1a_raw, 'lxml')
    except Exception:
        print(Exception)
        pass
    # item_3_content = BeautifulSoup(item_3_raw, 'lxml')
    try:
        item_7_content = BeautifulSoup(item_7_raw, 'lxml')
    except Exception:
        print(Exception)
        pass
    # print(item_1a_content.get_text("\n\n")[0:10], item_7_content.get_text("\n\n")[0:10])

    return item_1a_content.get_text("\n\n"), item_7_content.get_text("\n\n")




def analyze_edgar_files(filing_type):
    print("starting file finder", datetime.now())
    file_names = naming_files()[0]
    # print(file_names)
    ten_k_file_dict = {}
    print("starting analyzer", datetime.now())
    for names in file_names:
        # print("names", names)
        translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)

        #find the company name by using regex to extract the CIK number, then look it up in the json file
        extracted_cik_number = re.findall(r'/0{3}\d{5,12}/', names)
        extracted_cik_number = str(extracted_cik_number)
        extracted_cik_number = extracted_cik_number.translate(translation_table)
        with open('static/all_stock_cik.json', 'r') as file:
            cik_data = json.load(file)
        target_value = extracted_cik_number.lstrip('0')
        found_key = None
        for item in cik_data:
            for key, value in item.items():
                if value == target_value:
                    found_key = key
                    break  # Exit the inner loop if a match is found
            if found_key:
                break  # Exit the outer loop if a match is found

        if found_key:
            extracted_company_names = found_key
        else:
            extracted_company_names = 'unknown'
        # print(extracted_company_names)

        extracted_filing_type = re.findall("/\w+-\w+/", names)
        extracted_filing_type = str(extracted_filing_type)
        extracted_filing_type = extracted_filing_type.translate(translation_table)

        extracted_dates = re.findall("/\d+-\d+-\d+/", names)
        extracted_dates = str(extracted_dates)
        extracted_dates = extracted_dates.translate(translation_table)

        ten_k_file_dict.setdefault(names, [])
        ten_k_file_dict[names].append(extracted_company_names)
        ten_k_file_dict[names].append(extracted_filing_type)
        ten_k_file_dict[names].append(extracted_dates)

    # print("dict", ten_k_file_dict)

    for files in file_names:
        # print("files", files)
        if filing_type == '10k':
            try:
                item1a = extract_text_from_sections_10k(files)
                item1a = item1a[0]
            except (KeyError, ValueError) as error1:
                print(error1)
                item1a = 'null'
            try:
                ten_k_file_dict[files].append(item1a)
            except (KeyError, ValueError) as error2:
                print(error2)
                continue
            try:
                item7 = extract_text_from_sections_10k(files)
                item7 = item7[1]
            except (KeyError, ValueError) as error1:
                print(error1)
                item7 = 'null'
            try:
                ten_k_file_dict[files].append(item7)
            except ValueError:
                continue
            time.sleep(0.2)
        else:
            try:
                item1a = extract_text_from_sections_10q(files)
            except (KeyError, ValueError) as error1:
                print(error1)
                item1a = 'null'
            try:
                ten_k_file_dict[files].append(item1a)
            except (KeyError, ValueError) as error2:
                print(error2)
                continue
            time.sleep(0.2)
    print("ending analyzer", datetime.now())

    print("starting df changes", datetime.now())
    df_with_dates = edgar_filing_dates()
    # print("with dates", df_with_dates)
    df = pd.DataFrame(list(ten_k_file_dict.items()))
    df.columns = ['file_location', 'nested_data']
    print("first df", df)
    if filing_type == '10k':
        df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(),
                                         columns=['company_name', 'filing_type', 'filing_number',
                                                  'risk_factors', 'risk_disclosures'])
        df = pd.merge(df_with_risk_data, df_with_dates, how='inner', on=['filing_number'])
    else:
        df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(),
                                         columns=['company_name', 'filing_type', 'filing_number',
                                                  'risk_factors'])
        df = pd.merge(df_with_risk_data, df_with_dates, how='inner', on=['filing_number'])
    df = df.drop_duplicates()
    print("ending df changes", datetime.now())
    # print(df)
    return df

# analyze_edgar_files('10q')

