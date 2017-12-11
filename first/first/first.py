# -*- coding: utf-8 -*-
"""
    First Flask db Demo
    ~~~~~~~~

    A program that reads in a hard-coded static db and retrieves via qeuery

"""
import os, string
import time
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
    print('db Initialized')
    db.execute('insert into Students (Student_id, First, Last) values (?, ?, ?)',
              [1,"Brandon","RichardWebster"])
    db.commit()
    db.execute('insert into Students (Student_id, First, Last) values (?, ?, ?)',
              [2,"Joel","Brogan"])
    db.commit()
    db.execute('insert into Students (Student_id, First, Last) values (?, ?, ?)',
              [3,"Andrey","Kuekhamp"])
    db.commit()
    db.execute('insert into Classes (Class_id, Name, Credits) values (?, ?, ?)',
              [1,"Databases",3])
    db.commit()
    db.execute('insert into Classes (Class_id, Name, Credits) values (?, ?, ?)',
              [2,"Algorithms",4])
    db.commit()
    db.execute('insert into Classes (Class_id, Name, Credits) values (?, ?, ?)',
              [3,"Operating Systems",4])
    db.commit()
    db.execute('insert into Schedule (Schedule_id, Students_id, Class_id) values (?, ?, ?)',
              [1,1,1])
    db.commit()
    db.execute('insert into Schedule (Schedule_id, Students_id, Class_id) values (?, ?, ?)',
              [2,1,3])
    db.commit()
    db.execute('insert into Schedule (Schedule_id, Students_id, Class_id) values (?, ?, ?)',
              [3,2,2])
    db.commit()
    db.execute('insert into Schedule (Schedule_id, Students_id, Class_id) values (?, ?, ?)',
              [4,3,1])
    db.commit()
    db.execute('insert into Schedule (Schedule_id, Students_id, Class_id) values (?, ?, ?)',
              [5,3,2])
    db.commit()
    db.execute('insert into Schedule (Schedule_id, Students_id, Class_id) values (?, ?, ?)',
              [6,3,3])
    db.commit()
    db.execute('insert into Exp (Session_id, Image, Opt1, Opt2, Opt3, Sol) values (?, ?, ?, ?, ?, ?)',
              [1,"https://www.what-dog.net/Images/faces2/scroll0015.jpg","Cat","Dog","Fish","Dog"])
    db.commit()
    print('DB udpated')

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

@app.route('/Students')
def students_page():
    db = get_db()
    query = query_db('''select * from Students''')
    return render_template('Students.html',data=query)

@app.route('/Classes')
def classes_page():
    db = get_db()
    query = query_db('''select * from Classes''')
    return render_template('Classes.html',data=query)

@app.route('/Schedule')
def schedule_page():
    db = get_db()
    query = query_db('''select * from Schedule''')
    return render_template('Schedule.html',data=query)

@app.route('/AppendDB',methods=['GET','POST'])
def append_db_page():
        if request.method == 'GET':
            return render_template('Append_Db.html')
        if request.method == 'POST':
            db = get_db()
            db.execute('''insert into Classes (Class_id,Name,Credits) values (?,?,?)''',
                    [request.form['Class_id'],request.form['Name'],request.form['Credits']])
            db.commit()
        query = query_db('''select * from Classes''')
        return render_template('Classes.html',data=query)

@app.route('/Example',methods=['GET','POST'])
def example_page():
        if request.method == 'GET':
            db = get_db()
            query = query_db('''select * from Exp where Session_id=1''')
            return render_template('Example.html',data=query)
        if request.method == 'POST':
            db = get_db()
            query = query_db('''select * from Exp where Session_id=?''',
                    [1],one=True)
            ID = query['Session_id']
            Solution = query['Sol']

            db.execute('''insert into Data (Question_id,Correct_answer,Submitted_answer) values (?,?,?)''',
                     [ID,Solution,request.form['options']])
            db.commit()
#            db_tmp = get_db()
            query_tmp = query_db('''select * from Data''')
            return render_template('Data.html',data=query_tmp)

@app.route('/trial/<path:code>')
def trial(code):
    
    # Dummy inits
    data_in = ['Brandon Richard Webster','Kevin Bower','Walter Scheirer']
    data_out = []

    # Decode incoming URL
    temp = code.split('/')  
    user_name = temp[0]
    question_num_in = temp[1]
    question_id_in = temp[2]
    question_answer_in = temp[3]

    # Testing
    print("Question Answer : {}".format(question_answer_in))
    print("Question Number : {}".format(question_num_in))
    print("Question ID: {}".format(question_id_in))
    print("User ID: {}".format(user_name))

    # Encode outoing URL base characteristics
    question_num_out = str(int(question_num_in)+1)

    # Build out whole url
    answer = data_in[0].replace(' ','_')
    url1_tail = data_in[0].replace(' ','_')
    url1=user_name+'/'+question_num_out+'/'+answer+'/'+url1_tail
    
    url2_tail = data_in[1].replace(' ','_')
    url2=user_name+'/'+question_num_out+'/'+answer+'/'+url2_tail

    url3_tail = data_in[2].replace(' ','_')
    url3=user_name+'/'+question_num_out+'/'+answer+'/'+url3_tail

    # Testing
    print("URL 1: {}".format(url1))
    print("URL 2: {}".format(url2))
    print("URL 3: {}".format(url3))

    print("Data 1: {}".format(data_in[0]))
    print("Data 2: {}".format(data_in[1]))
    print("Data 3: {}".format(data_in[2]))


    # Build out object
    tmp_trial = {}
    # Get button name
    tmp_trial['data1'] = data_in[0]
    tmp_trial['data2'] = data_in[1]
    tmp_trial['data3'] = data_in[2]
    # Get image
    tmp_trial['image'] = 'https://engineering.nd.edu/profiles/brichardwebster/@@images/81a1b34f-ee63-457b-864a-cb8eee7df648.jpeg' 
    # Get URLS
    tmp_trial['url1'] = url1
    tmp_trial['url2'] = url2
    tmp_trial['url3'] = url3
    # Append object
    data_out.append(tmp_trial)
    return render_template('Example.html',data=data_out)

'''
    trials = []    
    #resp = make_response(render_template('home.html'))
    trial = {}
    trial['id'] = 0
    trial['image'] = 'https://engineering.nd.edu/profiles/brichardwebster/@@images/81a1b34f-ee63-457b-864a-cb8eee7df648.jpeg'
    trial['answer'] = [True, False, False]
    trials.append(trial)
    return make_response(render_template('example.html', exp0=trials))
    print("Question Number: {}".format(int(question_number)+1))
    print("Question ID: {}".format(question_id))
    print("User ID: {}".format(user_id))
'''




