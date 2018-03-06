# -*- coding: utf-8 -*-
"""
    First Flask db Demo
    ~~~~~~~~

    A program that reads in a hard-coded static db and retrieves via qeuery

"""
import os, string
import time, tweepy, json
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash


# configuration
DATABASE = '/tmp/index.db'
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
#    db.execute('insert into Exp (Session_id, Image, Opt1, Opt2, Opt3, Sol) values (?, ?, ?, ?, ?, ?)',
#              [1,"https://www.what-dog.net/Images/faces2/scroll0015.jpg","Cat","Dog","Fish","Dog"])
#    db.commit()

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

@app.route('/Tweets')
def students_page():
    db = get_db()
    query = query_db('''select * from Tweets''')
    return render_template('Tweets.html',data=query)

class FilteredStream(tweepy.StreamListener):
	def on_status(self,status):
	db = get_db()
	db.execute('''insert into Tweets (Tweet_ID,Text,Date_Var) values (?,?,?)''',
			[status.id,status.text,status.date])
	db.commit()	


@app.route('/Curl')
def classes_page():
    db = get_db()
    streamListener = FilteredStream()
    stream = tweepy.Stream(auth=api.auth,listener=streamListener)
    stream.filter(locations[1,1,1,1])



