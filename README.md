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
    - SEC filings (10-K's and 10-Q's)
    - Crypto data
    - Financial Data using (AlphaVantage)
         - The code is written to use the free API which has a cap of 500 calls per day
    - Deploy your code to your preferred cloud provider; I've been running this with ElasticBeanstalk and left the necessary extensions and packages
      

This is all the code necessary to run the causalation application. I have slimmed this down from my own project which has a lot of experimentation, so some things may be lost in translation. I know that it's poorly organized and commented, I originally built this just for myself but decided to publish it since I don't intend to keep the website running much longer.

If you want to run part of all of this code yourself and run into issues, shoot me an email. I'm happy to help with any piece of this! causalation@gmail.com


**Data**

All of the data populated into the application are pulled from the underlying Postgres database using SQL.

**Correlation Dashboard**
- Stock's closing price for a given week and the percentage of SEC Filings that mention the keyword selected. The keyword selected is cohorted by week and the percentage represented in the chart is based on a 12 week rolling average
- The returns of the stock in the given timeframe
- The returns of the S&P 500 during the same timeframe to make benchmarking easier
- The number of times the stock follows the moves of the keyword mentions with the filters applied. Example: you have the delay filter set to 2 weeks and the keyword mentions increase in a one week timeframe. Then two weeks later, the stock price increases as well. That would count as a match. If the moves match 50 out of 100 times, this value will show 50%.
- Total number of times this keyword is mentioned within the timeframe selected
- The correlation ratio between the stock and the keyword selected, within the given filters
- Top 25 stock/keyword combinations with the strongest correlation


**Machine Learning Dashboard**
- recommended stock purchases based on ML analysis of historical stock data. Any stock predicted to increase in price by >5% is recommended to buy. Based on the projeted growth, the model recommends a proportional purchase amount, given a starting principle of $1,000
- Backtested historical returns by the model
- S&P 500 returns (with dividends reinvested) over the same time period
- Sharpe ratio of the backtest
- All predicted returns of the most highly correlated stock/keyword pairs

**Discounted Stocks Dashboard**

Over the selected time period:
- Total stock % change
- Highest price achieved
- Current price
- Days since peak price
- Peak price date
- Change in cash held by the company since the peak price
- Change in assets held by the company since the peak price
- Change in company valuation
- Peak company valuation
- Most recent company valuation (10-K or 10-Q, whatever is more recent)
- Change in EPS
- EPS at peak price
- Most recent EPS (10-K or 10-Q, whatever is more recent)
- Price to Sales ratio change over time
- Price to sales ratio at peak stock price
- Price to Sales ratio, most recent
- P/E Ratio
- P/E Ratio at peak stock price
- P/E Ratio, most recent
- EBITDA change over time
- Quarterly earnings results charted over time

**HomePage**
<img width="1438" alt="Screen Shot 2024-04-06 at 1 35 28 PM" src="https://github.com/mikeferrell/causalation_application/assets/68746547/d2ada04b-3f2a-4b33-ae8d-33a0b9bd3f9b">


**Correlation Chart**

<img width="1053" alt="Screen Shot 2023-07-13 at 1 53 45 PM" src="https://github.com/mikeferrell/causalation_application/assets/68746547/89190532-556c-4452-91f9-20b4188ab270">


**Predicted Price Moves**

<img width="707" alt="Screen Shot 2023-06-30 at 5 51 51 PM" src="https://github.com/mikeferrell/causalation_application/assets/68746547/7f7cf848-933f-4d31-aa7a-48ef933ac7a1">

