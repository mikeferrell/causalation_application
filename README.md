# causalation_application
Causalation is a project with several pieces, all of which can be run from this code base:

- A website with homepage, blog, help page, about, contact, and a page for each of the following financial models:
     - Comparing correlations between keyword frequency in SEC filings and stock moves over the same timeframe
     - Machine Learning prediction of which stocks will increase by >5% in value in the coming week, based on changes in keyword frequency
     - A table organzing financial data over the past several years in order to quickly identify undervalued stocks for further investigation

In order to run this project:

- Create a database (preferrably Postgres) where all financial data can be stored
- Enter your database credentials into the two password.py files (or store these as environment variables)
- Use one_time_jobs.py to backfill the data into your database for the timeframe you want to see:
    - Stock Data
    - SEC filings
    - Crypto data
    - Financial Data using (AlphaVantage)
         - The code is written to use the free API which has a cap of 500 calls per day
    - Deploy your code to your preferred cloud provider; I've been running this with ElasticBeanstalk and left the necessary extensions and packages
      

This is all the code necessary to run the causalation application. I have slimmed this down from my own project which has a lot of experimentation, so some things may be lost in translation. I know that it's poorly organized and commented, I originally built this just for myself but decided to publish it since I don't intend to keep the website running much longer.

If you want to run part of all of this code yourself and run into issues, shoot me an email. I'm happy to help with any piece of this! causalation@gmail.com

**HomePage**
<img width="1438" alt="Screen Shot 2024-04-06 at 1 35 28 PM" src="https://github.com/mikeferrell/causalation_application/assets/68746547/d2ada04b-3f2a-4b33-ae8d-33a0b9bd3f9b">


**Correlation Chart**

<img width="1053" alt="Screen Shot 2023-07-13 at 1 53 45 PM" src="https://github.com/mikeferrell/causalation_application/assets/68746547/89190532-556c-4452-91f9-20b4188ab270">


**Predicted Price Moves**

<img width="707" alt="Screen Shot 2023-06-30 at 5 51 51 PM" src="https://github.com/mikeferrell/causalation_application/assets/68746547/7f7cf848-933f-4d31-aa7a-48ef933ac7a1">

