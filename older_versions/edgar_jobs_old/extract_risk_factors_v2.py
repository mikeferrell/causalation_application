from bs4 import BeautifulSoup
import re
import pandas as pd


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


