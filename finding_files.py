import os, re

def naming_files():
    top_folder = '/Users/michaelferrell/Desktop/edgar_files/sec-edgar-filings'
    company_name_folders = []
    file_type_per_company = []
    company_filing_type_folders = []
    filing_numbers = []
    filing_date_folders = []
    file_names = []
    filing_names_for_edgar_urls = []

    #creates a new link for each company folder
    company_names = [companies for companies in os.listdir(top_folder) if os.path.isdir(os.path.join(top_folder, companies))]
    for companies in company_names:
        new_folder = '/Users/michaelferrell/Desktop/edgar_files/sec-edgar-filings'+"/"+companies
        company_name_folders.append(new_folder)
    # print(company_name_folders)

    # Creates a new list of the filing types and then creates a new list of links for each company filing type
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

    return file_names, filing_numbers
# print(file_names)

# for names in file_names:
#     extracted_company_names = re.findall("/([A-Z]{1,5})/", names)
#     extracted_company_names = str(extracted_company_names)
#     translation_table = dict.fromkeys(map(ord, '[]()/'), None)
#     extracted_company_names = extracted_company_names.translate(translation_table)
#     extracted_filing_type = re.findall("/\w+-\w+/", names)
#     extracted_filing_type = str(extracted_filing_type)
#     extracted_filing_type = extracted_filing_type.translate(translation_table)
#     extracted_dates = re.findall("/\d+-\d+-\d+/", names)
#     extracted_dates = str(extracted_dates)
#     extracted_dates = extracted_dates.translate(translation_table)
#     key = names
#     ten_k_file_dict.setdefault(key, [])
#     #trying to next these things under each other. This syntax doesn't work, try something else
#     ten_k_file_dict[key].append(extracted_company_names)
#     ten_k_file_dict[key].append(extracted_filing_type)
#     ten_k_file_dict[key].append(extracted_dates)
#
# print(ten_k_file_dict)

# Put all of this into a dataframe. columns = company name, company link, filing type, filing type link, filing date,
# filing date link. These will need to be nested, so I should create some kind of JSON matching all of them. Then turn
# that into a df

# f = open("/Users/michaelferrell/Desktop/edgar_files/sec-edgar-filings/AMC/10-K/0001514991-22-000007/full-submission.txt", "r")
# print(f.read(5000))


