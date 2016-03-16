from flask import url_for, redirect, render_template, abort, \
    flash, session
from noter import app, db
from models import Entry, User
from forms import loginForm, entryForm, signupForm
from markdown2 import Markdown

## Entry
@app.route('/')
def show_entries():
    form = entryForm()
    entries = entries_render(Entry.query.order_by(Entry.id))
    return render_template('show_entries.html', entries = entries, form = form)

@app.route('/add', methods=['POST'])
def add_entry():
    form = entryForm()
    if form.validate_on_submit:
        if not session.get('logged_in'):
            abort(401)
        newEntry = Entry(form.title.data, form.body.data)
        db.session.add(newEntry)
        db.session.commit()
    return redirect(url_for('show_entries'))

# Edit entry
@app.route('/edit/<int:id>', methods=['GET'])
def edit_entry_form(id):
    if not session.get('logged_in'):
        abort(403)
    form = entryForm()
    entry = Entry.query.filter_by(id=id).first()
    form.title.data = entry.title
    form.body.data = entry.body
    return render_template('edit.html', entry = entry, form = form);

@app.route('/edit/<int:id>', methods=['POST'])
def edit_entry(id):
    form = entryForm()
    if form.validate_on_submit:
        if not session.get('logged_in'):
            abort(403)
        entry = Entry.query.filter_by(id=id).first()
        entry.title = form.title.data
        entry.body = form.body.data
        db.session.commit()
    return redirect(url_for('show_entries'))

# Delete entry
@app.route('/delete/<int:id>', methods=['GET'])
def confirm_delete_entry(id):
    if not session.get('logged_in'):
        abort(403)
    entry = entries_render(Entry.query.filter_by(id=id).first())
    return render_template('delete.html', entry = entry);

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    if not session.get('logged_in'):
        abort(403)
    entry = Entry.query.filter_by(id=id).first()
    db.session.delete(entry)
    db.session.commit()
    return show_entries();

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
    form = signupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = loginForm()
    if form.validate_on_submit():
        if (form.name.data != app.config['USERNAME']) or \
           (form.password.data != app.config['PASSWORD']):
            error = 'Wrong username/password combination'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error, form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('show_entries'))


