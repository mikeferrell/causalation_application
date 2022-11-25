# import extract_risk_factors_v2
# import finding_files
# import re
# import pandas as pd
# import edgar_date_pull
# import passwords
# from sqlalchemy import create_engine
# import psycopg2
# import time
#
# from sec_edgar_downloader import Downloader
# import dataframes_from_queries
# from datetime import date, timedelta
# from apscheduler.schedulers.background import BackgroundScheduler
# import os
#
# class EdgarCronJobs:
#     def __init__(self):
#         url = passwords.rds_access
#         engine = create_engine(url)
#         self.connect = engine.connect()
#
#         today = date.today()
#         yesterdays_date = today - timedelta(days=1)
#         yesterdays_date = str(yesterdays_date)
#         year = int(yesterdays_date[0:4])
#         month = int(yesterdays_date[5:7])
#         day = int(yesterdays_date[8:10])
#
#         self.yesterday = str(date(year, month, day))
#         self.end_date = str(date(year, month, day))
#
#         self.symbols_list = dataframes_from_queries.stock_dropdown()
#
#     def append_postgres(self, table, df):
#         df.to_sql(table, con=self.connect, if_exists='append',
#                   index=False)
#         conn = psycopg2.connect(self.url)
#         conn.autocommit = True
#         cursor = conn.cursor()
#         conn.close()
#         print('done')
#
#     def update_edgar_10ks(self):
#         for ticker in self.symbols_list:
#             dl = Downloader("/Users/michaelferrell/Desktop/edgar_files/")
#             # dl.get("10-K", ticker, after="2017-01-01", before="2022-08-20")
#             try:
#                 dl.get("10-K", ticker, after="2022-10-20", before="2022-11-05")
#             except Exception as error:
#                 print(error)
#                 continue
#         time.sleep(30)
#
#     def update_edgar_10qs(self):
#         for ticker in self.symbols_list:
#             dl = Downloader("/Users/michaelferrell/Desktop/edgar_files/")
#             # dl.get("10-K", ticker, after="2017-01-01", before="2022-08-20")
#             try:
#                 dl.get("10-Q", ticker, after="2022-10-20", before="2022-11-05")
#             except Exception as error:
#                 print(error)
#                 continue
#         time.sleep(30)
#
#     def analyze_edgar_files_10q(self):
#         for names in finding_files.file_names:
#             extracted_company_names = re.findall("/([A-Z]{1,5})/", names)
#             extracted_company_names = str(extracted_company_names)
#             translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)
#             extracted_company_names = extracted_company_names.translate(translation_table)
#             extracted_filing_type = re.findall("/\w+-\w+/", names)
#             extracted_filing_type = str(extracted_filing_type)
#             extracted_filing_type = extracted_filing_type.translate(translation_table)
#             extracted_dates = re.findall("/\d+-\d+-\d+/", names)
#             extracted_dates = str(extracted_dates)
#             extracted_dates = extracted_dates.translate(translation_table)
#             key = names
#             finding_files.ten_k_file_dict.setdefault(key, [])
#             finding_files.ten_k_file_dict[key].append(extracted_company_names)
#             finding_files.ten_k_file_dict[key].append(extracted_filing_type)
#             finding_files.ten_k_file_dict[key].append(extracted_dates)
#
#         # print(finding_files.ten_k_file_dict)
#
#         for files in finding_files.file_names:
#             company_name = re.findall("/([A-Z]{1,5})/", files)
#             company_name = str(company_name)
#             translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)
#             company_name = company_name.translate(translation_table)
#             # timestamp = time.time()
#             try:
#                 item1a = extract_risk_factors_v2.extract_text_from_sections_10k(files)
#                 # (item1a, item7) = extract_risk_factors_v2.extract_text_from_sections_10k(files)
#             except (KeyError, ValueError) as error1:
#                 print(error1)
#                 continue
#             try:
#                 finding_files.ten_k_file_dict[files].append(item1a)
#             except (KeyError, ValueError) as error2:
#                 print(error2)
#                 continue
#             time.sleep(0.2)
#             # try:
#             #     finding_files.ten_k_file_dict[files].append(item7)
#             # except ValueError:
#             #     continue
#             # print(finding_files.ten_k_file_dict)
#
#         # print(list(finding_files.ten_k_file_dict.items()))
#
#         df = pd.DataFrame(list(finding_files.ten_k_file_dict.items()))
#         df.columns = ['file_location', 'nested_data']
#         df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(),
#                                          columns=['company_name', 'filing_type', 'filing_number',
#                                                   'risk_factors'])
#         # df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(), columns = ['company_name', 'filing_type', 'filing_number',
#         #                                                           'risk_factors', 'risk_disclosures'])
#         df = pd.merge(df_with_risk_data, edgar_date_pull.df_with_dates, how='inner', on='filing_number')
#         df = df.drop_duplicates()
#         # print(df)
#
#         # append_postgres('edgar_test_data', df)
#         return df
#
#     def analyze_edgar_files_10k(self):
#         for names in finding_files.file_names:
#             translation_table = dict.fromkeys(map(ord, '''[]'()/'''), None)
#
#             extracted_company_names = re.findall("/([A-Z]{1,5})/", names)
#             extracted_company_names = str(extracted_company_names)
#             extracted_company_names = extracted_company_names.translate(translation_table)
#
#             extracted_filing_type = re.findall("/\w+-\w+/", names)
#             extracted_filing_type = str(extracted_filing_type)
#             extracted_filing_type = extracted_filing_type.translate(translation_table)
#
#             extracted_dates = re.findall("/\d+-\d+-\d+/", names)
#             extracted_dates = str(extracted_dates)
#             extracted_dates = extracted_dates.translate(translation_table)
#
#             finding_files.ten_k_file_dict.setdefault(names, [])
#             finding_files.ten_k_file_dict[names].append(extracted_company_names)
#             finding_files.ten_k_file_dict[names].append(extracted_filing_type)
#             finding_files.ten_k_file_dict[names].append(extracted_dates)
#
#         # print(finding_files.file_names)
#
#         for files in finding_files.file_names:
#             try:
#                 item1a = extract_risk_factors_v2.extract_text_from_sections_10k(files)
#             except (KeyError, ValueError) as error1:
#                 print(error1)
#                 continue
#             try:
#                 finding_files.ten_k_file_dict[files].append(item1a)
#             except (KeyError, ValueError) as error2:
#                 print(error2)
#                 continue
#             try:
#                 item7 = extract_risk_factors_v2.extract_text_from_sections_10k(files)
#             except (KeyError, ValueError) as error1:
#                 print(error1)
#                 continue
#             try:
#                 finding_files.ten_k_file_dict[files].append(item7)
#             except ValueError:
#                 continue
#             # print(finding_files.ten_k_file_dict)
#             time.sleep(0.2)
#
#         # print(list(finding_files.ten_k_file_dict.items()))
#
#         df = pd.DataFrame(list(finding_files.ten_k_file_dict.items()))
#         df.columns = ['file_location', 'nested_data']
#         df_with_risk_data = pd.DataFrame(df['nested_data'].to_list(),
#                                          columns=['company_name', 'filing_type', 'filing_number',
#                                                   'risk_factors', 'risk_disclosures'])
#         df = pd.merge(df_with_risk_data, edgar_date_pull.df_with_dates, how='left', on=['filing_number'])
#         df = df.drop_duplicates()
#         # print(df)
#
#         # append_postgres('edgar_test_data', df)
#         return df
#
#
#
#
#
# # analyze_edgar_files_10k()
# # analyze_edgar_files_10q()
#
# # symbols_list = dataframes_from_queries.stock_dropdown()
# #
# # def test_update_edgar_10ks():
# #     for ticker in symbols_list:
# #         dl = Downloader("/Users/michaelferrell/Desktop/edgar_files/")
# #         # dl.get("10-K", ticker, after="2017-01-01", before="2022-08-20")
# #         try:
# #             dl.get("10-K", ticker, after="2022-10-30", before="2022-11-05")
# #         except Exception as error:
# #             print(error)
# #             continue
# #     time.sleep(600)
# #     analyze_edgar_files_10k()
#
# # if __name__ == '__main__':
# #     scheduler = BackgroundScheduler()
# #     scheduler.add_job(test_update_edgar_10ks, 'cron', hour=6, minute=51)
# #     # scheduler.add_job(update_edgar_10qs, 'cron', hour=16, minute=51)
# # #     scheduler.add_job(update_stock_data, 'cron', hour=7, minute=47)
# # #     scheduler.add_job(keyword_count_cron_job, 'cron', hour=7, minute=13)
# # #     scheduler.add_job(weekly_stock_opening_cron_job, 'cron', hour=7, minute=14)
# #     scheduler.start()
# #     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
# # # # day_of_week='tue-sat'
# #
# #     try:
# #         # This is here to simulate application activity (which keeps the main thread alive).
# #         while True:
# #             time.sleep(2)
# #     except (KeyboardInterrupt, SystemExit):
# #         # Not strictly necessary if daemonic mode is enabled but should be done if possible
# #         scheduler.shutdown()