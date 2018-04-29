# -*- coding: utf-8 -*-
"""
    First Flask db Demo
    ~~~~~~~~
    A program that reads in a hard-coded static db and retrieves via qeuery
"""
import webbrowser as wb
import os, sys, string, uuid
import time, tweepy, json
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, make_response
from werkzeug import check_password_hash, generate_password_hash
from textblob import TextBlob
from gmplot import gmplot


# configuration
DATABASE = 'tmp/index.db'
#PER_PAGE = 30
#DEBUG = True
#SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

consumer_key="QMM9pAjHKYRQ4gMGNbNRDugHu"
consumer_secret="00uRXAzclsmQE0MjR5LYOhwZJPfJQaXBmNJJ4gI9bZfGEwi286"
access_token="1170470796-W0IQzj5X4NAZZ0WN6dGic7cUeBSX3jhbJlCAwkG"
access_token_secret="kfhFd1Uw2cOfojmWLyoT3myF3LUmA6GcbXKelE6nuOKNK"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

app = Flask('first')
app.config.from_object(__name__)
#app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def uuid_page():
    # Set UID cookie
    UserID = str(uuid.uuid4())
    response = make_response(redirect(url_for('home')))
    response.set_cookie('UID',UserID)
    return response

@app.route('/Home')
def home_page():
    return render_template('index.html')

@app.route('/Tweets')
def tweets_page():
    db = get_db()
    query = query_db('''SELECT * FROM Tweets''')
#    print(query)
    return render_template('Tweets.html',data=query)

@app.route('/Curl')
def curl_page():
    i = 0
    db = get_db()
    with open("tmp_results.txt","r+") as f:
        data = f.readlines()
        for line in data:
            tmp = line.split(',')
            try:
                text = tmp[1].replace('^^^',',')
                db.execute('''insert into Tweets(Tweet_ID,Text,GeoX,GeoY,Time) values (?,?,?,?,?)''', 
                     [tmp[0],text,tmp[2],tmp[3],tmp[4]])
                db.commit()
            except IndexError:
                print("Bad tweet:(")
    os.system("rm tmp_results.txt")
    return redirect('/Tweets')


@app.route('/SentimentPins')
def sentiment_page():
    print("Starting Analysis...")
    db = get_db()
    c = db.cursor()
    gmap = gmplot.GoogleMapPlotter(39.8283, -98.5795, 5, apikey='AIzaSyCEYyEKiSKuoEW20-XKL53kJ3CuySnWVbI')
    posNounPhrases = dict()
    negNounPhrases = dict()
    for row in c.execute('''SELECT * FROM Tweets'''):
        #text is 2, lats are 3, lons are 4
        tweetBlob = TextBlob(row[2])
        nounList = tweetBlob.split()
        if float(tweetBlob.sentiment.polarity)>0:
            gmap.marker(float(row[3]), float(row[4]), '#FF0000')
            print(tweetBlob.sentiment.polarity, row[2])
            for i in nounList:
                try:
                    posNounPhrases[i] += 1
                except KeyError:
                    posNounPhrases[i] = 1
        elif float(tweetBlob.sentiment.polarity)==0:
            pass
        else:
            gmap.marker(float(row[3]), float(row[4]), 'cornflowerblue')
            print(tweetBlob.sentiment.polarity, row[2])
            for i in nounList:
                #print(i)
                try:
                    negNounPhrases[i] += 1
                except KeyError:
                    negNounPhrases[i] = 1
    dir_path = os.path.dirname(os.path.realpath(__file__))
    newPath = dir_path + "/templates/my_map.html"
    gmap.draw(newPath)
    pos = []
    neg = []
    #print(posNounPhrases)
    #print(negNounPhrases)
    for i in posNounPhrases:
        pos.append((posNounPhrases[i],i))
    for i in negNounPhrases:
        neg.append((negNounPhrases[i],i))
    pos = sorted(pos, reverse = True)
    neg = sorted(neg, reverse = True)
    posStr = ""
    negStr = ""
    posCount = 0
    negCount = 0
    for i in range(100):
        if posCount < 10 and len(pos[i][1])>3:
            posStr += pos[i][1] + ", "
            posCount += 1
        if negCount < 10 and len(neg[i][1])>3:
            negStr += neg[i][1] + ", "
            negCount += 1
    print("Most positive phrases: " + posStr)
    print("Most negative phrases: " + negStr)
    wb.open_new_tab("file://"+newPath)
        
    return redirect('/Tweets')
   
