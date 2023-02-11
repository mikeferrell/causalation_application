import dash
from flask import Flask
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import images as my_images
import base64
import sidebar as sidebar
import cron_jobs
import edgar_jobs
from apscheduler.schedulers.background import BackgroundScheduler
import one_time_edgar_pull
import time
import os
import logging


app = Dash(__name__, use_pages=True, title='Causalation', assets_folder="static", assets_url_path="static",
           external_stylesheets=[dbc.themes.UNITED])
server = Flask(__name__)
scheduler = BackgroundScheduler()
application = app.server
# log_file = 'application.log'
# logging.basicConfig(filename=log_file, format='%(asctime)s - %(message)s', level=logging.INFO)

logo_image_direct = 'static/causalation-logo-no-background.png'
# logo_image = my_images.logo
# small_logo_image = my_images.small_logo
# encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
# encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.Div(html.Img(src=logo_image_direct,
                                      style={'height': '5%', 'width': '70%'})),
                    width={"size": 6, "offset": 4})),
    dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
    dbc.Row(dbc.Col(dash.page_container)),
]
)


@server.route("/")
def my_dash_app():
    return app.index()


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)
logging.info('Admin logged in')


scheduler.add_job(cron_jobs.full_edgar_job_10ks, 'cron', hour=1, minute=1, name='full_edgar_10ks')
scheduler.add_job(cron_jobs.full_edgar_job_10qs, 'cron', hour=1, minute=30, name='full_edgar_10qs')
scheduler.add_job(cron_jobs.update_stock_data, 'cron', day_of_week='tue-sat', hour=2, minute=10)
scheduler.add_job(cron_jobs.top_correlation_scores, 'cron', day_of_week='wed', hour=3, minute=30)
scheduler.add_job(cron_jobs.top_correlation_scores, 'cron', day_of_week='fri', hour=3, minute=30)
# scheduler.add_job(cron_jobs.weekly_stock_opening_cron_job, 'cron', day_of_week='tue-sat', hour=2, minute=40)
# scheduler.add_job(cron_jobs.weekly_stock_opening_cron_job, 'interval', minutes=3)
scheduler.add_job(cron_jobs.keyword_count_cron_job, 'cron', day_of_week='tue-sat', hour=3, minute=10)
scheduler.add_job(cron_jobs.ml_calculate_top_ten_forecasts, 'cron', day_of_week='fri', hour=4, minute=10)

# scheduler.add_job(one_time_edgar_pull.full_edgar_job_10ks, 'cron', day_of_week='sun', hour=15, minute=1, name='one_time_edgar_10ks')
# scheduler.add_job(one_time_edgar_pull.full_edgar_job_10qs, 'cron', day_of_week='sun', hour=20, minute=1, name='one_time_edgar_10qs')
scheduler.start()


if __name__ == '__main__':
    application.run(port=8000, debug=False)
#
# if __name__ == '__main__':
#     app.run_server(port=8000, debug=False)