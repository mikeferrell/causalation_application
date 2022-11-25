import extract_risk_factors_v2
import finding_files
import re
import pandas as pd
import edgar_date_pull
import passwords
from sqlalchemy import create_engine
import psycopg2
import time

from sec_edgar_downloader import Downloader
import dataframes_from_queries
from datetime import datetime

ticker_list = dataframes_from_queries.stock_dropdown()

def update_edgar_10ks():
    print("starting updates", datetime.now())
    for ticker in ticker_list:
        dl = Downloader("/Users/michaelferrell/Desktop/edgar_files/")
        # dl.get("10-K", ticker, after="2017-01-01", before="2022-08-20")
        try:
            dl.get("10-K", ticker, after="2022-10-20", before="2022-11-05")
        except Exception as error:
            print(error)
            continue
    print("ending updates", datetime.now())

def update_edgar_10qs():
    for ticker in dataframes_from_queries.stock_dropdown():
        dl = Downloader("/Users/michaelferrell/Desktop/edgar_files/")
        # dl.get("10-K", ticker, after="2017-01-01", before="2022-08-20")
        try:
            dl.get("10-Q", ticker, after="2022-10-20", before="2022-11-05")
        except Exception as error:
            print(error)
            continue

def analyze_edgar_files_10q():
    finding_files.naming_files()
    for names in finding_files.file_names:
        extracted_company_names = re.findall("/([A-Z]{1,5})/", names)
        extracted_company_names = str(extracted_company_names)
        translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)
        extracted_company_names = extracted_company_names.translate(translation_table)
        extracted_filing_type = re.findall("/\w+-\w+/", names)
        extracted_filing_type = str(extracted_filing_type)
        extracted_filing_type = extracted_filing_type.translate(translation_table)
        extracted_dates = re.findall("/\d+-\d+-\d+/", names)
        extracted_dates = str(extracted_dates)
        extracted_dates = extracted_dates.translate(translation_table)
        key = names
        finding_files.ten_k_file_dict.setdefault(key, [])
        finding_files.ten_k_file_dict[key].append(extracted_company_names)
        finding_files.ten_k_file_dict[key].append(extracted_filing_type)
        finding_files.ten_k_file_dict[key].append(extracted_dates)

    # print(finding_files.ten_k_file_dict)

    for files in finding_files.file_names:
        company_name = re.findall("/([A-Z]{1,5})/", files)
        company_name = str(company_name)
        translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)
        company_name = company_name.translate(translation_table)
        # timestamp = time.time()
        try:
            item1a = extract_risk_factors_v2.extract_text_from_sections_10k(files)
            # (item1a, item7) = extract_risk_factors_v2.extract_text_from_sections_10k(files)
        except (KeyError, ValueError) as error1:
            print(error1)
            continue
        try:
            finding_files.ten_k_file_dict[files].append(item1a)
        except (KeyError, ValueError) as error2:
            print(error2)
            continue
        time.sleep(0.2)
        # try:
        #     finding_files.ten_k_file_dict[files].append(item7)
        # except ValueError:
        #     continue
        # print(finding_files.ten_k_file_dict)

    # print(list(finding_files.ten_k_file_dict.items()))

    df = pd.DataFrame(list(finding_files.ten_k_file_dict.items()))
    df.columns = ['file_location', 'nested_data']
    df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(),
                                     columns=['company_name', 'filing_type', 'filing_number',
                                              'risk_factors'])
    # df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(), columns = ['company_name', 'filing_type', 'filing_number',
    #                                                           'risk_factors', 'risk_disclosures'])
    df = pd.merge(df_with_risk_data, edgar_date_pull.df_with_dates, how='inner', on='filing_number')
    df = df.drop_duplicates()
    # print(df)

    # append_postgres('edgar_test_data', df)
    return df

def analyze_edgar_files(filing_type):
    print("starting file finder", datetime.now())
    file_names = finding_files.naming_files()
    file_names = file_names[0]
    # print(file_names)
    ten_k_file_dict = {}
    print("starting analyzer", datetime.now())
    for names in file_names:
        # print("names", names)
        translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)

        extracted_company_names = re.findall("/([A-Z]{1,5})/", names)
        extracted_company_names = str(extracted_company_names)
        extracted_company_names = extracted_company_names.translate(translation_table)

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

    # print(finding_files.file_names)

    for files in file_names:
        # print("files", files)
        if filing_type == '10k':
            try:
                item1a = extract_risk_factors_v2.extract_text_from_sections_10k(files)
                item1a = item1a[0]
            except (KeyError, ValueError) as error1:
                print(error1)
                continue
            try:
                ten_k_file_dict[files].append(item1a)
            except (KeyError, ValueError) as error2:
                print(error2)
                continue
            try:
                item7 = extract_risk_factors_v2.extract_text_from_sections_10k(files)
                item7 = item7[1]
            except (KeyError, ValueError) as error1:
                print(error1)
                continue
            try:
                ten_k_file_dict[files].append(item7)
            except ValueError:
                continue
            time.sleep(0.2)
        else:
            try:
                item1a = extract_risk_factors_v2.extract_text_from_sections_10q(files)
                item1a = item1a[0]
            except (KeyError, ValueError) as error1:
                print(error1)
                continue
            try:
                ten_k_file_dict[files].append(item1a)
            except (KeyError, ValueError) as error2:
                print(error2)
                continue
            time.sleep(0.2)


    print("ending analyzer", datetime.now())

    # print(list(finding_files.ten_k_file_dict.items()))
    print("starting df changes", datetime.now())
    df = pd.DataFrame(list(ten_k_file_dict.items()))
    df.columns = ['file_location', 'nested_data']
    df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(),
                                     columns=['company_name', 'filing_type', 'filing_number',
                                              'risk_factors', 'risk_disclosures'])
    df = pd.merge(df_with_risk_data, edgar_date_pull.df_with_dates, how='left', on=['filing_number'])
    df = df.drop_duplicates()
    print("ending df changes", datetime.now())
    # print(df)

    # append_postgres('edgar_test_data', df)
    print("starting pg upload", datetime.now())
    conn_string = passwords.rds_access
    db = create_engine(conn_string)
    conn = db.connect()
    df.to_sql('edgar_test_data', con=conn, if_exists='replace',
              index=False)
    conn = psycopg2.connect(conn_string
                            )
    conn.autocommit = True
    cursor = conn.cursor()
    conn.close()
    print("done")

# analyze_edgar_files_10k()
# analyze_edgar_files_10q()

# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(test_update_edgar_10ks, 'cron', hour=6, minute=51)
#     # scheduler.add_job(update_edgar_10qs, 'cron', hour=16, minute=51)
# #     scheduler.add_job(update_stock_data, 'cron', hour=7, minute=47)
# #     scheduler.add_job(keyword_count_cron_job, 'cron', hour=7, minute=13)
# #     scheduler.add_job(weekly_stock_opening_cron_job, 'cron', hour=7, minute=14)
#     scheduler.start()
#     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
# # # day_of_week='tue-sat'
#
#     try:
#         # This is here to simulate application activity (which keeps the main thread alive).
#         while True:
#             time.sleep(2)
#     except (KeyboardInterrupt, SystemExit):
#         # Not strictly necessary if daemonic mode is enabled but should be done if possible
#         scheduler.shutdown()