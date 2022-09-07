from flask import Flask
from flask import render_template
# import correlation_dashboard

application = Flask(__name__)

@application.route("/")
def index():
    # return render_template(correlation_dashboard.correlation_dash(), title='Home Page')
    return "hello world"

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)

# index()

# from flask import Flask
# from dash import Dash
# import correlation_dashboard
# import dash_core_components as dcc
# import dash_html_components as html
#
#
# server = Flask(__name__)
# app = Dash(
#     __name__,
#     server=server,
#     url_base_pathname='/'
# )


#
# @server.route("/")
# def my_dash_app():
#     return app.index()
