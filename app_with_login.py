import dash
from flask import Flask, request
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
from static import navbar as sidebar
import cron_jobs
import one_time_jobs
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user
from dash.dependencies import Input, Output, State

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.UNITED])
scheduler = BackgroundScheduler()
# log_file = 'application.log'
# logging.basicConfig(filename=log_file, format='%(asctime)s - %(message)s', level=logging.INFO)

# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))

# Setting up login manager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


# User data model
class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    return User(username)


# Login screen
login = html.Div([
    dcc.Location(id='url_login', refresh=True),
    html.H2('''Please log in to continue:''', id='h1'),
    dcc.Input(placeholder='Enter your username', type='text', id='uname-box'),
    dcc.Input(placeholder='Enter your password', type='password', id='pwd-box'),
    html.Button('Login', n_clicks=0, type='submit', id='login-button'),
    html.Div(id='output-state')
])

# Successful login
success = html.Div([
    html.H2('Login successful.'),
    dcc.Link('Home', href='/')
])

# Failed Login
failed = html.Div([
    html.H2('Log in Failed. Please try again.'),
    html.Div([login]),
    dcc.Link('Home', href='/')
])

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# Callback function to login the user or display an error message
@app.callback(
    Output('page-content', 'children'),
    Output('url_login', 'pathname'),
    Output('output-state', 'children'),
    [Input('login-button', 'n_clicks')],
    [State('uname-box', 'value'), State('pwd-box', 'value')]
)
def login_button_click(n_clicks, username, password):
    if n_clicks is not None and n_clicks > 0:
        if username == 'test' and password == 'test':
            user = User(username)
            login_user(user)
            return success, '/success', ''
        else:
            return failed, '/login', 'Incorrect username or password'


# Main router
@app.callback(Output('page-content', 'children'), Output('redirect', 'pathname'),
              [Input('url', 'pathname')])
def display_page(pathname):
    view = None
    url = dash.no_update
    if pathname == '/login':
        view = login
    elif pathname == '/success':
        if current_user.is_authenticated:
            view = success
        else:
            view = failed
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            view = logout
        else:
            view = login
            url = '/login'

    elif pathname == '/dashboard':
        view = '/dashboard'
    elif pathname == '/predictions':
        if current_user.is_authenticated:
            view = '/predictions'
        else:
            view = 'Redirecting to login...'
            url = '/login'
    else:
        view = '/'
    # You could also return a 404 "URL not found" page here
    return view, url



#
# app.layout = dbc.Container([
#     html.Div([
#         dcc.Location(id='url', refresh=False),
#         html.Div(id='response-header', style={'display': 'none'})
#     ]),
#     dbc.Row(html.Div([sidebar.navbar, sidebar.content])),
#     # dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
#     dbc.Row(dbc.Col(dash.page_container)),
# ]
# )


@server.route("/")
def my_dash_app():
    return app.index()



console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)
logging.info('Admin logged in')


scheduler.add_job(cron_jobs.full_edgar_job_10ks, 'cron', hour=1, minute=1, name='full_edgar_10ks')
scheduler.add_job(cron_jobs.full_edgar_job_10qs, 'cron', hour=1, minute=20, name='full_edgar_10qs')
scheduler.add_job(cron_jobs.update_stock_data, 'cron', day_of_week='tue-sat', hour=1, minute=40)
scheduler.add_job(cron_jobs.wrapper_top_correlation_scores_asc, 'cron', day_of_week='tue-sat', hour=1, minute=59)
scheduler.add_job(cron_jobs.wrapper_top_correlation_scores_desc, 'cron', day_of_week='tue-sat', hour=2, minute=19)
scheduler.add_job(cron_jobs.top_ten_correlations_today, 'cron', day_of_week='tue-sat', hour=3, minute=3)
# scheduler.add_job(cron_jobs.weekly_stock_opening_cron_job, 'cron', day_of_week='tue-sat', hour=2, minute=40)
scheduler.add_job(cron_jobs.keyword_count_cron_job, 'cron', day_of_week='tue-sat', hour=1, minute=50)
scheduler.add_job(cron_jobs.ml_calculate_top_ten_forecasts, 'cron', day_of_week='sat', hour=3, minute=10)
scheduler.add_job(cron_jobs.predicted_prices_for_next_week, 'cron', day_of_week='sat', hour=22, minute=1)
scheduler.add_job(cron_jobs.predicted_prices_for_last_week, 'cron', day_of_week='sat', hour=22, minute=3)
scheduler.add_job(cron_jobs.last_week_top_correlation_scores, 'cron', day_of_week='sat', hour=3, minute=5)

# scheduler.add_job(one_time_jobs.backfill_score_wrapper_asc, 'cron', day_of_week='fri', hour=18, minute=55)
# scheduler.add_job(one_time_jobs.backfill_score_wrapper_desc, 'cron', day_of_week='sat', hour=3, minute=45)
# scheduler.add_job(one_time_jobs.one_time_backfill_correlation_scores, 'cron', day_of_week='tue', hour=13, minute=40)
# scheduler.add_job(one_time_edgar_pull.full_edgar_job_10ks, 'cron', day_of_week='sun', hour=15, minute=1, name='one_time_edgar_10ks')
# scheduler.add_job(one_time_edgar_pull.full_edgar_job_10qs, 'cron', day_of_week='sun', hour=20, minute=1, name='one_time_edgar_10qs')
scheduler.start()


if __name__ == '__main__':
    server.run(port=8000, debug=True)
