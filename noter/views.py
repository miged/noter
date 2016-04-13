from flask import url_for, redirect, render_template, abort, \
    flash, session
from noter import app, db, bcrypt
from models import Entry, User
from forms import loginForm, entryForm, signupForm
from markdown2 import Markdown

## Entry
@app.route('/')
def index():
    form = entryForm()
    if not session.get('logged_in'):
        return render_template('index.html')
    user = User.query.filter_by(id=session['user_id']).first()
    entries = entries_render(Entry.query.filter_by(user_id=session['user_id']).order_by(Entry.id))
    return render_template('show_entries.html', entries = entries, form = form)

@app.route('/add', methods=['POST'])
def add_entry():
    form = entryForm()
    if form.validate_on_submit:
        if not session.get('logged_in'):
            abort(401)
        newEntry = Entry(form.title.data, form.body.data, session['user_id'])
        db.session.add(newEntry)
        db.session.commit()
    return redirect(url_for('index'))

# Edit entry
@app.route('/edit/<int:id>', methods=['GET'])
def edit_entry_form(id):
    entry = Entry.query.filter_by(id=id).first()
    if not session.get('logged_in') or session['user_id'] != entry.user_id:
        abort(403)

    form = entryForm()
    form.title.data = entry.title
    form.body.data = entry.body
    return render_template('edit.html', entry = entry, form = form);

@app.route('/edit/<int:id>', methods=['POST'])
def edit_entry(id):
    form = entryForm()
    if form.validate_on_submit:
        entry = Entry.query.filter_by(id=id).first()
        if not session.get('logged_in') or session['user_id'] != entry.user_id:
            abort(403)
        entry.title = form.title.data
        entry.body = form.body.data
        db.session.commit()
    return redirect(url_for('index'))

# Delete entry
@app.route('/delete/<int:id>', methods=['GET'])
def confirm_delete_entry(id):
    entry = entries_render(Entry.query.filter_by(id=id).first())
    if not session.get('logged_in') or session['user_id'] != entry.user_id:
        abort(403)
    return render_template('delete.html', entry = entry);

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    entry = Entry.query.filter_by(id=id).first()
    if not session.get('logged_in') or session['user_id'] != entry.user_id:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('index'))

def entries_render(entries):
    try:
        for e in entries:
            e.body = Markdown().convert(e.body)
    except TypeError:
        entries.body = Markdown().convert(entries.body)

    return entries


## User
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    form = signupForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if (user is None):
            user = User(form.name.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            session['logged_in'] = True
            session['user_id'] = user.id
            session['name'] = user.username
            return redirect(url_for('index'))
        else:
            error = 'Username not available'
        
    return render_template('signup.html', error=error, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = loginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        bcrypt.check_password_hash(user._password, form.password.data)

        if (user is None):
            error = 'User does not exist'
        elif (bcrypt.check_password_hash(user._password, form.password.data) != True):
            error = 'Wrong user/password combination'
        else:
            session['logged_in'] = True
            session['user_id'] = user.id
            session['name'] = user.username
            flash('You were logged in.')
            return redirect(url_for('index'))

    return render_template('login.html', error=error, form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('index'))