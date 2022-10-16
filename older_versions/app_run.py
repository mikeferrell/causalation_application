#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy import create_engine
import passwords
from flask import render_template
import pandas as pd



app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = passwords.rds_access
url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()
ticker_query = "select * from ticker_data limit 10"

ticker_frame = pd.read_sql(ticker_query, con=connect)


@app.route('/', methods=("POST", "GET"))
def html_table():

    return render_template('simple.html',  tables=[ticker_frame.to_html(classes='data')], titles=ticker_frame.columns.values)

@app.route('/login', methods=("POST", "GET"))
def login():
    return render_template('index.html')

# @app.route("/")
# def index():
#     with connect as conn:
#         ticker_frame = pd.read_sql(ticker_query, con=conn)
#         ticker_frame = display(ticker_frame)
#
#     return f"""
# <html>
#   <p>Here are some routes for you:</p>
#
#   <ul>
#     <li><a href="/hello/world">Hello world</a></li>
#     <li><a href="/hello/foo-bar">Hello foo-bar</a></li>
#   </ul>
#
#   <p>View trace: <a href="{ticker_frame}</a></p>
# </html>
# """


@app.route("/hello/<username>")
def hello(username):
    with connect as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())

    return f"""
<html>
  <h3>Hello {username}</h3>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
