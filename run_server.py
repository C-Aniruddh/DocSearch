import datetime
import json
import os
import time
from signal import signal, SIGPIPE, SIG_DFL

import bcrypt
from bson import json_util
from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename

app = Flask(__name__)

timestamp = datetime.datetime.now()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
signal(SIGPIPE, SIG_DFL)
app.config['MONGO_DBNAME'] = 'aniruddh'
app.config['MONGO_URI'] = 'mongodb://flaskmongo:flask@ds157187.mlab.com:57187/aniruddh'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        books = mongo.db.documents
        count = books.count()
        booklist = range(0, count, 1)
        subjects = mongo.db.subjects
        subject_count = subjects.count()
        sublist = range(1, subject_count + 1, 1)
        subjinja = range(0, subject_count, 1)
        subjects_dropdown = []

        for x in sublist:
            y = x
            z = str(y)
            subject_find = subjects.find_one({'sub_id': z})
            subject_name = subject_find['subject']
            subjects_dropdown.append(subject_name)

        authors = mongo.db.authors
        authors_count = authors.count()
        authlist = range(1, authors_count + 1, 1)
        authjinja = range(0, authors_count, 1)
        authors_dropdown = []

        for x in authlist:
            y = x
            z = str(y)
            author_find = authors.find_one({'auth_id': z})
            author_name = author_find['name']
            authors_dropdown.append(author_name)

        users = mongo.db.users
        user = session['username']
        user_find = users.find_one({'name': user})
        user_fullname = user_find['fullname']

        document_url = []
        book_title = []
        book_author = []
        book_edition = []
        book_subject = []
        for x in booklist:
            y = x + 1
            z = str(y)
            book_find = books.find_one({'book_id': z})
            doc_url = '/document/%s' % z
            document_url.append(doc_url)
            book_auth = book_find['book_author']
            book_author.append(book_auth)
            book_titl = book_find['book_title']
            book_title.append(book_titl)
            book_edi = book_find['book_edition']
            book_edition.append(book_edi)
            book_sub = book_find['book_subject']
            book_subject.append(book_sub)
        return render_template('home.html', book_title=book_title, book_author=book_author, document_url=document_url,
                               booklist=booklist, book_edition=book_edition, book_subject=book_subject,
                               user_fullname=user_fullname, sublist=sublist, subjects_dropdown=subjects_dropdown,
                               subjinja=subjinja, authlist=authlist, authors_dropdown=authors_dropdown,
                               authjinja=authjinja)
    return render_template('index.html')


@app.route('/userlogin', methods=['POST', 'GET'])
def userlogin():
    if 'username' in session:
        return redirect('/home')

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user[
            'password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return "not allowed     "
    if request.method == 'POST':
        users = mongo.db.users
        user_fname = request.form['name']
        user_email = request.form['email']
        existing_user = users.find_one({'name': request.form['username'], 'email': user_email})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'fullname': user_fname, 'email': user_email, 'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'A user with that Email id/username already exists'

    return render_template('register.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if 'username' in session:
        books = mongo.db.documents
        subjects = mongo.db.subjects
        subject_count = subjects.count()
        sublist = range(1, subject_count + 1, 1)
        subjinja = range(0, subject_count, 1)
        subjects_dropdown = []

        for x in sublist:
            y = x
            z = str(y)
            subject_find = subjects.find_one({'sub_id': z})
            subject_name = subject_find['subject']
            subjects_dropdown.append(subject_name)

        authors = mongo.db.authors
        authors_count = authors.count()
        authlist = range(1, authors_count + 1, 1)
        authjinja = range(0, authors_count, 1)
        authors_dropdown = []

        for x in authlist:
            y = x
            z = str(y)
            author_find = authors.find_one({'auth_id': z})
            author_name = author_find['name']
            authors_dropdown.append(author_name)

        if request.method == 'POST':
            file = request.files['book_upload']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                fname = filename
                book_title = request.form['book_title']
                book_author = request.form['book_author']
                book_edition = request.form['book_edition']
                document_type = request.form['document_type']
                subject_name = request.form['subject_name']
                book_c_tot = books.count()
                book_c = book_c_tot + 1
                book_id = str(book_c)
                type_c_find = books.find({'type': document_type})
                type_c_tot = type_c_find.count()
                type_c = type_c_tot + 1
                type_c_id = str(type_c)
                sub_c_find = books.find({'book_subject': subject_name})
                sub_c_tot = sub_c_find.count()
                sub_c = sub_c_tot + 1
                sub_c_id = str(sub_c)
                auth_c_find = books.find({'book_author': book_author})
                auth_c_tot = auth_c_find.count()
                auth_c = auth_c_tot + 1
                auth_c_id = str(auth_c)
                download_link = '/downloads/%s' % fname
                books.insert({'book_title': book_title, 'filename': fname, 'book_author': book_author,
                              'book_edition': book_edition, 'type': document_type, 'book_subject': subject_name,
                              'book_id': book_id, 'type_id': type_c_id, 'sub_id': sub_c_id, 'book_url': download_link,
                              'auth_id': auth_c_id})

        return render_template('submit2.html', sublist=sublist, subjects_dropdown=subjects_dropdown, subjinja=subjinja,
                               authlist=authlist, authors_dropdown=authors_dropdown, authjinja=authjinja)
    return 'Kindly login to perform this action'


@app.route('/add_sub', methods=['POST', 'GET'])
def add_sub():
    if 'username' in session:

        if request.method == 'POST':
            subjects = mongo.db.subjects
            count = subjects.count()
            new_subject = request.form['subject']
            existing_subject = subjects.find_one({'subject': new_subject})
            subject_added = timestamp.strftime("%Y-%m-%d")
            subject_id = count + 1
            subject_value = subject_id - 1
            subval = str(subject_value)
            subid = str(subject_id)
            if existing_subject is None:
                subjects.insert(
                    {'subject': new_subject, 'date_added': subject_added, 'sub_id': subid, 'subject_value': subval})

        return render_template('addsubject.html')

    return 'kindly login to perform this action'


@app.route('/add_auth', methods=['POST', 'GET'])
def add_auth():
    if 'username' in session:

        if request.method == 'POST':
            authors = mongo.db.authors
            count = authors.count()
            new_author = request.form['name']
            existing_author = authors.find_one({'name': new_author})
            author_added = timestamp.strftime("%Y-%m-%d")
            author_id = count + 1
            auth_id = str(author_id)
            if existing_author is None:
                authors.insert({'name': new_author, 'date_added': author_added, 'auth_id': auth_id})

        return render_template('addauthor.html')

    return 'kindly login to perform this action'


@app.route('/document/<book_id>')
def document(book_id):
    books = mongo.db.documents
    doc_find = books.find_one({'book_id': book_id})
    book_title = doc_find['book_title']
    book_author = doc_find['book_author']
    book_type = doc_find['type']
    book_subject = doc_find['book_subject']
    book_url = doc_find['book_url']
    book_edition = doc_find['book_edition']


    users = mongo.db.users
    user = session['username']
    user_find = users.find_one({'name': user})
    user_fullname = user_find['fullname']
    return render_template('book2.html', book_title=book_title, book_author=book_author, book_edition=book_edition,
                           type=book_type, book_subject=book_subject, book_url=book_url, user_fullname=user_fullname)


@app.route('/bysub/<subid>')
def bysub(subid):
    documents = mongo.db.documents
    books_find = documents.find({'book_subject': subid})
    count = books_find.count()
    booklist = range(0, count, 1)
    subjects = mongo.db.subjects
    subject_count = subjects.count()
    sublist = range(1, subject_count + 1, 1)
    subjinja = range(0, subject_count, 1)
    subjects_dropdown = []

    for x in sublist:
        y = x
        z = str(y)
        subject_find = subjects.find_one({'sub_id': z})
        subject_name = subject_find['subject']
        subjects_dropdown.append(subject_name)

    authors = mongo.db.authors
    authors_count = authors.count()
    authlist = range(1, authors_count + 1, 1)
    authjinja = range(0, authors_count, 1)
    authors_dropdown = []

    for x in authlist:
        y = x
        z = str(y)
        author_find = authors.find_one({'auth_id': z})
        author_name = author_find['name']
        authors_dropdown.append(author_name)

    users = mongo.db.users
    user = session['username']
    user_find = users.find_one({'name': user})
    user_fullname = user_find['fullname']
    document_url = []
    book_title = []
    book_author = []
    book_edition = []
    book_subject = []

    for x in booklist:
        y = x + 1
        z = str(y)
        book_find = documents.find_one({'sub_id': z, 'book_subject': subid})
        book_id = book_find['book_id']
        doc_url = '/document/%s' % book_id
        document_url.append(doc_url)
        book_auth = book_find['book_author']
        book_author.append(book_auth)
        book_titl = book_find['book_title']
        book_title.append(book_titl)
        book_edi = book_find['book_edition']
        book_edition.append(book_edi)
        book_sub = book_find['book_subject']
        book_subject.append(book_sub)
    return render_template('bysub.html', book_title=book_title, book_author=book_author, document_url=document_url,
                           booklist=booklist, book_edition=book_edition, book_subject=book_subject,
                           user_fullname=user_fullname, sublist=sublist, subjects_dropdown=subjects_dropdown,
                           subjinja=subjinja, authlist=authlist, authors_dropdown=authors_dropdown, authjinja=authjinja)


@app.route('/bytype/<typeid>')
def bytype(typeid):
    documents = mongo.db.documents
    books_find = documents.find({'type': typeid})
    count = books_find.count()
    booklist = range(0, count, 1)
    subjects = mongo.db.subjects
    subject_count = subjects.count()
    sublist = range(1, subject_count + 1, 1)
    subjinja = range(0, subject_count, 1)
    subjects_dropdown = []

    for x in sublist:
        y = x
        z = str(y)
        subject_find = subjects.find_one({'sub_id': z})
        subject_name = subject_find['subject']
        subjects_dropdown.append(subject_name)

    authors = mongo.db.authors
    authors_count = authors.count()
    authlist = range(1, authors_count + 1, 1)
    authjinja = range(0, authors_count, 1)
    authors_dropdown = []

    for x in authlist:
        y = x
        z = str(y)
        author_find = authors.find_one({'auth_id': z})
        author_name = author_find['name']
        authors_dropdown.append(author_name)

    users = mongo.db.users
    user = session['username']
    user_find = users.find_one({'name': user})
    user_fullname = user_find['fullname']
    document_url = []
    book_title = []
    book_author = []
    book_edition = []
    book_subject = []

    for x in booklist:
        y = x + 1
        z = str(y)
        book_find = documents.find_one({'type_id': z})
        book_id = book_find['book_id']
        doc_url = '/document/%s' % book_id
        document_url.append(doc_url)
        book_auth = book_find['book_author']
        book_author.append(book_auth)
        book_titl = book_find['book_title']
        book_title.append(book_titl)
        book_edi = book_find['book_edition']
        book_edition.append(book_edi)
        book_sub = book_find['book_subject']
        book_subject.append(book_sub)

    return render_template('bytype.html', book_title=book_title, book_author=book_author, document_url=document_url,
                           booklist=booklist, book_edition=book_edition, book_subject=book_subject,
                           user_fullname=user_fullname, sublist=sublist, subjects_dropdown=subjects_dropdown,
                           subjinja=subjinja, authlist=authlist, authors_dropdown=authors_dropdown, authjinja=authjinja)


@app.route('/byauth/<auth>')
def byauth(auth):
    documents = mongo.db.documents
    books_find = documents.find({'book_author': auth})
    count = books_find.count()
    booklist = range(0, count, 1)
    subjects = mongo.db.subjects
    subject_count = subjects.count()
    sublist = range(1, subject_count + 1, 1)
    subjinja = range(0, subject_count, 1)
    subjects_dropdown = []

    for x in sublist:
        y = x
        z = str(y)
        subject_find = subjects.find_one({'sub_id': z})
        subject_name = subject_find['subject']
        subjects_dropdown.append(subject_name)

    authors = mongo.db.authors
    authors_count = authors.count()
    authlist = range(1, authors_count + 1, 1)
    authjinja = range(0, authors_count, 1)
    authors_dropdown = []

    for x in authlist:
        y = x
        z = str(y)
        author_find = authors.find_one({'auth_id': z})
        author_name = author_find['name']
        authors_dropdown.append(author_name)

    users = mongo.db.users
    user = session['username']
    user_find = users.find_one({'name': user})
    user_fullname = user_find['fullname']
    document_url = []
    book_title = []
    book_author = []
    book_edition = []
    book_subject = []

    for x in booklist:
        y = x + 1
        z = str(y)
        book_find = documents.find_one({'auth_id': z, 'book_author': auth})
        book_id = book_find['book_id']
        doc_url = '/document/%s' % book_id
        document_url.append(doc_url)
        book_auth = book_find['book_author']
        book_author.append(book_auth)
        book_titl = book_find['book_title']
        book_title.append(book_titl)
        book_edi = book_find['book_edition']
        book_edition.append(book_edi)
        book_sub = book_find['book_subject']
        book_subject.append(book_sub)

    return render_template('byauth.html', book_title=book_title, book_author=book_author, document_url=document_url,
                           booklist=booklist, book_edition=book_edition, book_subject=book_subject,
                           user_fullname=user_fullname, sublist=sublist, subjects_dropdown=subjects_dropdown,
                           subjinja=subjinja, authlist=authlist, authors_dropdown=authors_dropdown, authjinja=authjinja)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if 'username' in session:
        users = mongo.db.users
        user = session['username']
        user_find = users.find_one({'name': user})
        user_fullname = user_find['fullname']
        if request.method == 'POST':
            search_query = request.form['search_query']
            querystr = '/query/%s' % search_query
            return redirect(querystr)
        return render_template('search.html', user_fullname=user_fullname)
    
    return 'You need to be logged in to perform search'

def toJson(data):
    return json.dumps(data, default=json_util.default)


@app.route('/query/<search_query>', methods=['POST', 'GET'])
def query(search_query):
    books = mongo.db.documents
    find_books = books.find({'book_title': {"$regex": search_query}})
    tot_count = find_books.count()
    booklist = range(0, tot_count, 1)
    document_url = []
    book_title = []
    book_author = []
    book_edition = []
    book_subject = []
    book_ids = []

    users = mongo.db.users
    user = session['username']
    user_find = users.find_one({'name': user})
    user_fullname = user_find['fullname']

    """
    Basic Goal is to make a list, sort the data and then fill the data from a cursor to a list by converting the
    cursor object to a dict object

    Code for reference :

    results = []
    find_book_res = books.find({'book_title': {"$regex": search_query}}, {'book_author': True, '_id': False})
    for author in find_book_res:
        text = str(author['book_author'].encode('utf-8'))
        results.append(text)"""
    start_time = time.time()
    find_book_author = books.find({'book_title': {"$regex": search_query}}, {'book_author': True, '_id': False})
    for author in find_book_author:
        auth = str(author['book_author'].encode('utf-8'))
        book_author.append(auth)

    find_book_title = books.find({'book_title': {"$regex": search_query}}, {'book_title': True, '_id': False})
    for title in find_book_title:
        titl = str(title['book_title'].encode('utf-8'))
        book_title.append(titl)

    find_book_id = books.find({'book_title': {"$regex": search_query}}, {'book_id': True, '_id': False})
    for identity in find_book_id:
        iden = str(identity['book_id'].encode('utf-8'))
        book_ids.append(iden)

    find_book_edition = books.find({'book_title': {"$regex": search_query}}, {'book_edition': True, '_id': False})
    for edition in find_book_edition:
        edi = str(edition['book_edition'].encode('utf-8'))
        book_edition.append(edi)

    find_book_subject = books.find({'book_title': {"$regex": search_query}}, {'book_subject': True, '_id': False})
    for subject in find_book_subject:
        subj = str(subject['book_subject'].encode('utf-8'))
        book_subject.append(subj)

    for x in booklist:
        id = book_ids[x]
        doc_url = '/document/%s' % id
        document_url.append(doc_url)

    time_taken = '%s seconds' % (time.time() - start_time)

    if request.method == 'POST':
        searchq = request.form['searchq']
        querystr = '/query/%s' % searchq
        return redirect(querystr)

    return render_template('query.html', search_query=search_query, booklist=booklist, book_title=book_title,
                           book_subject=book_subject, book_edition=book_edition, book_author=book_author,
                           document_url=document_url, user_fullname=user_fullname, time_taken=time_taken)


@app.route('/downloads/<filename>')
def downloads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, host='0.0.0.0', port=5000, passthrough_errors=False, threaded=True)
