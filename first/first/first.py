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
from flask_wtf import Form
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

class ReusableForm(Form):
    keyword = TextField("Keyword:", validators = [validators.required()])

# configuration
DATABASE = 'tmp/index.db'
#PER_PAGE = 30
#DEBUG = True


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
    response = make_response(redirect(url_for('home_page')))
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
    os.system("python crawler.py")
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
    return redirect('/Home')

@app.route("/Input",methods=['GET','POST'])
def input_page():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        keyword = request.form['keyword']
        response = make_response(redirect(url_for('sentiment_page')))
        response.set_cookie('Location',"US")
        response.set_cookie('Keyword',keyword)
        return response
    if request.method == 'GET':
        return render_template("input.html", form=form)
        
    

@app.route("/Location/<location>")
def location_page(location):
    response = make_response(redirect(url_for('sentiment_page')))
    response.set_cookie('Location',location)
    response.set_cookie('Keyword',"NONE") 
    return response


@app.route('/SentimentPins')
def sentiment_page():
    uid = request.cookies.get("UID")
    location = request.cookies.get("Location")
    keyword = request.cookies.get("Keyword")
    coordDict = {"NY": (40.7829, -73.9682), "LA": (34.0522,-118.2436), "CH": (41.8781,-87.6232),"US":(39.8283, -98.5795)}
    if location != "US":
        zoom = 11
    else:
        zoom = 5
    print("Starting Analysis...")
    db = get_db()
    c = db.cursor()

    gmap = gmplot.GoogleMapPlotter(coordDict[location][0], coordDict[location][1],zoom, apikey='AIzaSyCEYyEKiSKuoEW20-XKL53kJ3CuySnWVbI')
    posNounPhrases = dict()
    negNounPhrases = dict()
    count = 0
    for row in c.execute('''SELECT * FROM Tweets'''):
        #text is 2, lats are 3, lons are 4
        tweetBlob = TextBlob(row[2])
        nounList = tweetBlob.split()
        if keyword in nounList or keyword == "NONE":
            if float(tweetBlob.sentiment.polarity)>.75:
                gmap.marker(float(row[3]), float(row[4]), 'maroon')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    try:
                        posNounPhrases[i] += 1
                    except KeyError:
                        posNounPhrases[i] = 1
            elif float(tweetBlob.sentiment.polarity)>.5:
                gmap.marker(float(row[3]), float(row[4]), 'red')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    try:
                        posNounPhrases[i] += 1
                    except KeyError:
                        posNounPhrases[i] = 1
            elif float(tweetBlob.sentiment.polarity)>.25:
                gmap.marker(float(row[3]), float(row[4]), 'deeppink')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    try:
                        posNounPhrases[i] += 1
                    except KeyError:
                        posNounPhrases[i] = 1
            elif float(tweetBlob.sentiment.polarity)>0:
                gmap.marker(float(row[3]), float(row[4]), 'pink')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    try:
                        posNounPhrases[i] += 1
                    except KeyError:
                        posNounPhrases[i] = 1
            elif float(tweetBlob.sentiment.polarity)==0:
                pass #gmap.marker(float(row[3]), float(row[4]), '#FFFFFF')
                #print(tweetBlob.sentiment.polarity, row[2])
                count += 1
            elif float(tweetBlob.sentiment.polarity)>-.25:
                gmap.marker(float(row[3]), float(row[4]), 'lightblue')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    #print(i)
                    try:
                        negNounPhrases[i] += 1
                    except KeyError:
                        negNounPhrases[i] = 1
            elif float(tweetBlob.sentiment.polarity)>-.5:
                gmap.marker(float(row[3]), float(row[4]), 'deepskyblue')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    #print(i)
                    try:
                        negNounPhrases[i] += 1
                    except KeyError:
                        negNounPhrases[i] = 1
            elif float(tweetBlob.sentiment.polarity)>-.75:
                gmap.marker(float(row[3]), float(row[4]), 'cornflowerblue')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    #print(i)
                    try:
                        negNounPhrases[i] += 1
                    except KeyError:
                        negNounPhrases[i] = 1
            elif float(tweetBlob.sentiment.polarity)>-.75:
                gmap.marker(float(row[3]), float(row[4]), 'darkslateblue')
                #print(tweetBlob.sentiment.polarity, row[2])
                for i in nounList:
                    #print(i)
                    try:
                        negNounPhrases[i] += 1
                    except KeyError:
                        negNounPhrases[i] = 1

    dir_path = os.path.dirname(os.path.realpath(__file__))
    newPath = dir_path + "/templates/{0}.html".format(uid)
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
        try:
            if posCount < 10 and len(pos[i][1])>3:
                posStr += pos[i][1] + ", "
                posCount += 1
        except IndexError:
            posCount = 10
        try:
            if negCount < 10 and len(neg[i][1])>3:
                negStr += neg[i][1] + ", "
                negCount += 1
        except IndexError:
            negCount = 10
    print("Most positive phrases: " + posStr)
    print("Most negative phrases: " + negStr)
    print("Total tweets with neutral sentiment: " + str(count))
    count = 0
    flag = False
    flag2=True
    with open(newPath,"r+") as f:
        data = f.readlines()
        for line in data:
            #if count==2:
#                f.write('<meta http-equiv="refresh" content="120; url=http://127.0.0.1:5000/SentimentPins"/>')
            count+=1
            if flag==True and flag2==True:
                flag2 = False
                flag = False
  
                f.write('<ul class="list-group">\n')
                f.write('<li class="list-group-item">People in {0} are upset about . . .</li>\n'.format(location))
                f.write('<li class="list-group-item">{0}</li>\n'.format(posStr))
                f.write('</ul>\n\n')
       
                f.write('<ul class="list-group">\n')
                f.write('<li class="list-group-item">People in {0} are happy about . . .</li>\n'.format(location))
                f.write('<li class="list-group-item">{0}</li>\n'.format(negStr))
                f.write('</ul>\n')
            if "body" in line:
                flag = True  
            f.write(line)

    f.close()
    wb.open_new_tab("file://"+newPath)
    return redirect('/Home')


