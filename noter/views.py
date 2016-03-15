from flask import url_for, redirect, request, render_template, \
    abort, flash, session
from noter import app, db
from models import Entry
from markdown2 import Markdown

@app.route('/')
def show_entries():
    entries = entries_render(Entry.query.order_by(Entry.id))
    return render_template('show_entries.html', entries = entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    newEntry = Entry(request.form['title'], request.form['text'])
    db.session.add(newEntry)
    db.session.commit()
    return redirect(url_for('show_entries'))

# Edit entry
@app.route('/edit/<int:id>', methods=['GET'])
def edit_entry_form(id):
    if not session.get('logged_in'):
        abort(403)
    entry = Entry.query.filter_by(id=id).first()
    return render_template('edit.html', entry = entry);

@app.route('/edit/<int:id>', methods=['POST'])
def edit_entry(id):
    if not session.get('logged_in'):
        abort(403)
    entry = Entry.query.filter_by(id=id).first()
    entry.title = request.form.get('title')
    entry.body = request.form.get('body')
    db.session.commit()
    return show_entries();

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form['username'] != app.config['USERNAME']) or \
           (request.form['password'] != app.config['PASSWORD']):
            error = 'Wrong username/password combination'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('show_entries'))

def entries_render(entries):
    try:
        for e in entries:
            e.body = Markdown().convert(e.body)
    except TypeError:
        entries.body = Markdown().convert(entries.body)

    return entries