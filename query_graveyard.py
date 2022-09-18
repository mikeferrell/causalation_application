#Mentions of inflation and comparing it to a stock (filtered in the where clause)
query_results = f'''
with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
case when risk_factors ilike '%%inflat%%' then 1
when risk_disclosures ilike '%%inflat%%' then 1
else 0
end as inflation_count
from public.edgar_data
where risk_factors != ''
and risk_disclosures != ''
order by inflation_count desc)

select sum(inflation_count) as inflation_mentions, count(filing_url) as total_filings, DATE_TRUNC('month', filing_date) as filing_month
from count_inflation_mentions
group by filing_month
order by filing_month asc
),

stock_monthly_opening as (with temp_table as (
                          select date(created_at) as created_at, close_price, stock_symbol
from public.ticker_data
    order

by
stock_symbol, date(created_at)
asc
)

SELECT
created_at,
close_price,
stock_symbol,
LAG(created_at, 1)
OVER(
    ORDER
BY
stock_symbol, created_at
) as next_date,
     case
when
split_part(LAG(created_at, 1)
OVER(
    ORDER
BY
stock_symbol, created_at
)::TEXT, '-', 2) =
split_part(created_at::TEXT, '-', 2) then
null else created_at
end as first_price_in_month
FROM
temp_table)

select
first_price_in_month as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as inflation_percentage
from stock_monthly_opening join

keyword_data
on
stock_monthly_opening.first_price_in_month = keyword_data.filing_month
where
stock_symbol in ('{stock_symbol}')```
'''