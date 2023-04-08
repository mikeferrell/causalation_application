import dash
from flask import Flask, render_template
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import sidebar as sidebar
import cron_jobs
from apscheduler.schedulers.background import BackgroundScheduler
import one_time_jobs
import logging


app = Dash(__name__, use_pages=True, title='Causalation', assets_folder="static", assets_url_path="static",
           external_stylesheets=[dbc.themes.UNITED])
server = Flask(__name__)
scheduler = BackgroundScheduler()
application = app.server
# log_file = 'application.log'
# logging.basicConfig(filename=log_file, format='%(asctime)s - %(message)s', level=logging.INFO)

logo_image_direct = 'static/causalation-logo-no-background.png'


colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

app.layout = dbc.Container([
    dbc.Row(html.Div([sidebar.navbar, sidebar.content])),
    dbc.Row(dbc.Col(html.Div(html.Img(src=logo_image_direct,
                                      style={'height': '2%', 'width': '50%'})),
                    width={"size": 6, "offset": 4})),
    # dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
    dbc.Row(dbc.Col(dash.page_container)),
]
)
# content = dbc.Container([
#     dbc.Row(dbc.Col(html.Div(html.Img(src=logo_image_direct,
#                                       style={'height': '2%', 'width': '50%'})),
#                     width={"size": 6, "offset": 4})),
#     dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
#     dbc.Row(dbc.Col(dash.page_container)),
# ]
# )


@server.route("/")
def my_dash_app():
    return app.index()
    # return render_template('index.html', logo=logo_image_direct, content=content)


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)
logging.info('Admin logged in')


scheduler.add_job(cron_jobs.full_edgar_job_10ks, 'cron', hour=1, minute=1, name='full_edgar_10ks')
scheduler.add_job(cron_jobs.full_edgar_job_10qs, 'cron', hour=1, minute=30, name='full_edgar_10qs')
scheduler.add_job(cron_jobs.update_stock_data, 'cron', day_of_week='tue-sat', hour=2, minute=10)
scheduler.add_job(cron_jobs.top_correlation_scores, 'cron', day_of_week='tue-sat', hour=3, minute=30)
# scheduler.add_job(cron_jobs.weekly_stock_opening_cron_job, 'cron', day_of_week='tue-sat', hour=2, minute=40)
scheduler.add_job(cron_jobs.keyword_count_cron_job, 'cron', day_of_week='tue-sat', hour=3, minute=10)
scheduler.add_job(cron_jobs.ml_calculate_top_ten_forecasts, 'cron', day_of_week='sat', hour=4, minute=10)
scheduler.add_job(cron_jobs.predicted_prices_for_next_week, 'cron', day_of_week='sat', hour=22, minute=1)

# scheduler.add_job(one_time_jobs.one_time_backfill_correlation_scores, 'cron', day_of_week='tue', hour=13, minute=40)
# scheduler.add_job(one_time_edgar_pull.full_edgar_job_10ks, 'cron', day_of_week='sun', hour=15, minute=1, name='one_time_edgar_10ks')
# scheduler.add_job(one_time_edgar_pull.full_edgar_job_10qs, 'cron', day_of_week='sun', hour=20, minute=1, name='one_time_edgar_10qs')
scheduler.start()


if __name__ == '__main__':
    application.run(port=8000, debug=True)
