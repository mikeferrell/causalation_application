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
import passwords
from sqlalchemy import create_engine
from sec_edgar_downloader import Downloader
import psycopg2
import spacy
import ml_models.dataframes_from_queries as dataframe_from_queries


headers = {'User-Agent': 'causalation, causalation@gmail.com'}


# Pull CIKs for most current list of S&P 500
def current_sp_cik_list():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})

    cik_list = []
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) >= 2:
            cik = columns[6].text.strip()
            cik_list.append(cik)
    return cik_list


def update_edgar_files(filing_type, cik_batch):
    # cik_list = ['DDOG', 'SNOW']
    #pull all CIKs from JSON
    # with open('all_stock_cik.json', 'r') as file:
    #     cik_data = json.load(file)
    # cik_list = [list(item.values())[0] for item in cik_data]

    print("starting updates", datetime.now())
    for ciks in cik_batch:
        dl = Downloader("causalation", "causalation@gmail.com")
        try:
            dl.get(f"{filing_type}", f"{ciks}", after=f"2022-11-11", before=f"2023-11-11")
        except Exception as error:
            print(error)
            continue
        # print(ciks)
    print("ending updates", datetime.now())

# update_edgar_files('10-Q', ['SNOW'])

def append_to_postgres(df, table, append_or_replace):
    df = df
    conn_string = passwords.rds_access
    db = create_engine(conn_string)
    conn = db.connect()
    df.to_sql(table, con=conn, if_exists=append_or_replace,
              index=False)
    conn = psycopg2.connect(conn_string
                            )
    conn.autocommit = True
    cursor = conn.cursor()
    conn.close()

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



def count_topics_in_10ks(link_to_10k):
    #keywords that align to topics to find
    keyword_list = dataframe_from_queries.keyword_list

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

    # Create a loop to go through each section type and save it in the dictionary
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        document[doc_type] = raw_10k[doc_start:doc_end]

    # Combine all sections into a single document
    full_document = '\n'.join(document.values())

    try:
        all_text = BeautifulSoup(full_document, 'lxml')
    except Exception as e:
        print(e)
        pass

    #this is going to return a lot of junk. revert back to filtering on just the relevant sections in the doc
    all_text = all_text.get_text("\n\n")
    all_text = all_text[:200000]

    # use the spacy library of similar words
    nlp = spacy.load("en_core_web_md")
    similar_words_dict = {}

    # Split the text into sentences
    sentences = [sent.text for sent in nlp(all_text).sents]

    for target_word in keyword_list:
        for sentence in sentences:
            doc = nlp(sentence)

            # Check if the pattern is present in the current sentence
            if target_word in doc.text:
                print(f"Pattern '{target_word}' found in the text.")
                print(sentence)
                similar_word_found = 1
                break
            else:
                similar_word_found = 0
            similar_words_dict[target_word] = []
            similar_words_dict[target_word].append(similar_word_found)
        print(similar_words_dict)

    return similar_words_dict


# count_topics_in_10ks('/Users/michaelferrell/PycharmProjects/causalation_dashboard/sec-edgar-filings/O/10-Q/0000726728-23-000068/full-submission.txt')


def analyze_edgar_files_for_employee_count():
    print("starting file finder", datetime.now())
    file_names = naming_files()[0]
    # print("file names", file_names)
    ten_k_df = pd.DataFrame()
    print("starting analyzer", datetime.now())
    for names in file_names:
        try:
            item1 = count_topics_in_10ks(names)
        except (KeyError, ValueError) as error1:
            print(error1)
            item1 = 'null'
            df_result = pd.DataFrame({'Column1': ['null'], 'Column2': ['null']})
            continue

            # print("names", names)
        translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)

        #find the company name by using regex to extract the CIK number, then look it up in the json file
        extracted_cik_number = re.findall(r'/0{3}\d{5,12}', names)
        extracted_cik_number = str(extracted_cik_number)
        extracted_cik_number = extracted_cik_number.translate(translation_table)
        # print("EC", extracted_cik_number)
        with open('static/shorter_stock_cik.json', 'r') as file:
            cik_data = json.load(file)
        target_value = extracted_cik_number.lstrip('0').split(',')[0]
        # print("TV", target_value)
        found_key = None
        for item in cik_data:
            for key, value in item.items():
                # print("Item", item, "key", key, "Value", value)
                if value == target_value:
                    found_key = key
                    # print("FK", found_key)
                    break  # Exit the inner loop if a match is found
            if found_key:
                break  # Exit the outer loop if a match is found

        if found_key:
            extracted_company_names = found_key
        else:
            extracted_company_names = 'unknown'
        # print("company", extracted_company_names)

        extracted_filing_type = re.findall("/\w+-\w+/", names)
        extracted_filing_type = str(extracted_filing_type)
        extracted_filing_type = extracted_filing_type.translate(translation_table)

        extracted_dates = re.findall("/\d+-\d+-\d+/", names)
        extracted_dates = str(extracted_dates)
        extracted_dates = extracted_dates.translate(translation_table)

        df_extraction = item1
        df_extraction['company_name'] = extracted_company_names
        df_extraction['filing_type'] = extracted_filing_type
        df_extraction['filing_number'] = extracted_dates
        ten_k_df = ten_k_df.append(df_extraction, ignore_index=True)
        # print("df_extraction", df_extraction)
        time.sleep(0.2)

    # print("dict", ten_k_df)
    print("ending analyzer", datetime.now())
    print("starting df changes", datetime.now())
    df_with_dates = edgar_filing_dates()
    # print("df_with_dates", df_with_dates)
    df = pd.merge(ten_k_df, df_with_dates, how='inner', on=['filing_number'])
    df = df.drop_duplicates()
    print("ending df changes", datetime.now())
    # print("df_for_upload", df)
    return df

# df_for_upload = analyze_edgar_files_for_employee_count()
# append_to_postgres(df_for_upload, 'dd_test_edgar_data', 'replace')


def full_edgar_job_10ks():
    with open('static/shorter_stock_cik.json', 'r') as file:
        cik_data = json.load(file)
    cik_list = [list(item.values())[0] for item in cik_data]

    batch_size = 10
    total_ciks = len(cik_list)

    for i in range(0, total_ciks, batch_size):
        cik_batch = cik_list[i:i + batch_size]
        update_edgar_files('10-K', cik_batch)
        time.sleep(10)

        count = 0
        for root_dir, cur_dir, files in os.walk(r'sec-edgar-filings/'):
            count += len(files)
        if count > 1:
            df_for_upload = analyze_edgar_files_for_employee_count()
            append_to_postgres(df_for_upload, 'dd_edgar_data', 'append')
            time.sleep(5)
            delete_edgar_file_paths()
        else:
            print("no files to analyze")

        print(f"Processed {i + batch_size} CIKs out of {total_ciks}")
    print("done with edgar cron job")

#
# full_edgar_job_10ks()
