from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import psycopg2
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup
from tempfile import mkdtemp
import pandas as pd
from datetime import datetime, date, timedelta

# connecting to Postgres database(LOCAL)
# DATABASE_NAME = "public_opinion_db"
# ORIGINAL_TWEETS_TABLE_NAME = "original_tweets"
# USER_TABLE_NAME = "users"
# WEBAPP_USER_TABLE_NAME = "webapp_user"
# DB_USER = "mmiyazaki"

# connecting to Postgres database(RDS)
DATABASE_NAME = "my_webapp_db"
TWEETS_TABLE_NAME = "tweets_processed"
USER_TABLE_NAME = "users"
WEBAPP_USER_TABLE_NAME = "webapp_user"
DB_USER = "postgres"
PORT=5432
HOST="database-2.cb9rr2xmqpik.eu-west-3.rds.amazonaws.com"
PASSWORD = "PYQ4mEaWgMJ7iZbX5Rkf"
params = "host=%s port=%i dbname=%s user=%s password=%s" % (HOST, PORT, DATABASE_NAME, DB_USER, PASSWORD)

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        conn = None
        try:
            # connect to the PostgreSQL database
            params = "dbname=%s user=%s" % (DATABASE_NAME, DB_USER)
            conn = psycopg2.connect(params)
            # create a new cursor
            cur = conn.cursor()
        except: None

        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("make sure you typed the same password twice", 400)
        
        print(request.form.get("username"), request.form.get("password"))

        #conn = None
        # try:
        
        # params = "dbname=%s user=%s" % (DATABASE_NAME, DB_USER)
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        usernames = cur.execute("SELECT username FROM {}".format(WEBAPP_USER_TABLE_NAME))
        try:
            list_usernames = [user['username'] for user in usernames]
        except:
            list_usernames = []
        print("list_usernames", list_usernames)
        if request.form.get("username") in list_usernames:
            return apology("user already exists", 400)

        # write the new user into the table
        cur.execute("INSERT INTO webapp_user (username, hash) VALUES(%s, %s)", (request.form.get("username"), generate_password_hash(request.form.get("password"))))
        conn.commit()

        # get the new user info from the table
        cur.execute("SELECT id, username FROM webapp_user WHERE username = %s", (request.form.get("username"),))

        # Remember which user has logged in
        fetched_user = cur.fetchone()
        fetched_id = fetched_user[0]
        fetched_username = fetched_user[1]
        session["user_id"] = fetched_id
        print("fetched:", fetched_id, fetched_username)

        # close the communication with the db
        cur.close()

        # Redirect user to home page
        return redirect("/")

        # except: apology("we couldn't register", 400)

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        # params = "dbname=%s user=%s" % (DATABASE_NAME, DB_USER)
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM webapp_user WHERE username = %s", (request.form.get("username"),))
        fetched_user = cur.fetchall()
        print(fetched_user[0])

        # Ensure username exists and password is correct
        if len(fetched_user) != 1 or not check_password_hash(fetched_user[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = fetched_user[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/daily", methods=["GET", "POST"])
@login_required
def daily():
    column_names = ["tweet_created_at", "tweet_id", "user_id", "tweet", "politician", "retweet_count", "reply_count", "like_count", "quote_count", "lang", "entities", "conversation_id", "tweets_cleaned", "sentiment", "score"]
    today = date.today().strftime("%Y-%m-%d")
    today_1 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-1)).strftime("%Y-%m-%d")
    if request.method == "GET":
        return render_template("daily.html", today=today_1)
    
    elif request.method == "POST":
        conn = None
        try:
            # connect to the PostgreSQL database
            # params = "dbname=%s user=%s" % (DATABASE_NAME, DB_USER)
            conn = psycopg2.connect(params)
            cur = conn.cursor()

            date_picked = request.form.get("tweet-date")
            print("date selected:", date_picked)
            date_picked_plus_one = datetime.strptime(date_picked, '%Y-%m-%d') + timedelta(days=1)  
            print("date selected plus one:", date_picked_plus_one)

            cur.execute("SELECT * FROM tweets_processed WHERE tweet_created_at >= %s AND tweet_created_at < %s", (date_picked, date_picked_plus_one))
            rows = cur.fetchall()
            print("rows:", rows)
            cur.close()
            df = pd.DataFrame(rows, columns=column_names)
            print(df.head(1))
            print(df.shape)
            df_grouped = df.groupby("politician").score.mean().reset_index()
            chart_data = {'politician':df_grouped['politician'].tolist(), 'score':df_grouped['score'].tolist()}
            print("chart_data", chart_data)
            # chart_data = {'politician':['A', 'B', 'C'], 'score':[10, 20 , 30]}
            return render_template("daily.html", chart_data = chart_data, today=date_picked)
        except: 
            return apology("something went wrong", 400)

@app.route("/historical", methods=["GET", "POST"])
@login_required
def historical():
    column_names = ["tweet_created_at", "tweet_id", "user_id", "tweet", "politician", "retweet_count", "reply_count", "like_count", "quote_count", "lang", "entities", "conversation_id", "tweets_cleaned", "sentiment", "score"]
    conn = None
    try:
        # connect to the PostgreSQL database
        # params = "dbname=%s user=%s" % (DATABASE_NAME, DB_USER)
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT politician FROM tweets_processed")
        politicians_list = cur.fetchall()
        print("politicians_list:", politicians_list)
        cur.close()
    except: 
        return apology("couldn't load politicians data", 400)

    if request.method == "GET":
        return render_template("historical.html", politicians_list=politicians_list)
        
    elif request.method == "POST":
        politicians_selected = tuple(request.form.getlist("select-politicians"))
        print("politicians_selected: ", politicians_selected)

        today = date.today().strftime("%Y-%m-%d")
        today_7 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-7)).strftime("%Y-%m-%d")
        today_6 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-6)).strftime("%Y-%m-%d")
        today_5 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-5)).strftime("%Y-%m-%d")
        today_4 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-4)).strftime("%Y-%m-%d")
        today_3 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-3)).strftime("%Y-%m-%d")
        today_2 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-2)).strftime("%Y-%m-%d")
        today_1 = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=-1)).strftime("%Y-%m-%d")
        X_timestamp = [today_7, today_6, today_5, today_4, today_3, today_2, today_1]

        conn = None
        try:
            # params = "dbname=%s user=%s" % (DATABASE_NAME, DB_USER)
            conn = psycopg2.connect(params)
            cur = conn.cursor()
            cur.execute("SELECT * FROM tweets_processed WHERE politician in %s AND tweet_created_at >= %s", (politicians_selected, today_6, ))
            print("Executed query: ", cur.query)
            rows = cur.fetchall()
            print("len(rows):", len(rows))
            cur.close()
            df = pd.DataFrame(rows, columns=column_names)
            df['tweet_created_at'] = df['tweet_created_at'].dt.floor('D')
            df = df.sort_values('tweet_created_at', ascending=True)

            df_grouped = df.groupby(["politician", "tweet_created_at"]).score.mean().reset_index()
            df_grouped['tweet_created_at'] = df_grouped['tweet_created_at'].astype(str)

            chart_data = {}
            for politician in df_grouped['politician'].unique():
                score_list = []
                for d in X_timestamp:
                    try:
                        score = df_grouped[(df_grouped['politician']==politician) & (df_grouped['tweet_created_at']==d)].score.values[0]
                        score_list.append(score)
                    except:
                        score_list.append(0)
                    chart_data[politician] = score_list
            print("X_timestamp: ", X_timestamp)
            print("chart_data: ", chart_data)
            return render_template("historical.html", politicians_list=politicians_list, timestamp = X_timestamp, chart_data=chart_data)
            
        except:
            return apology("couldn't load politicians data", 400)

    else: apology("something went wrong", 400)

if __name__ == "__main__":
    app.run()