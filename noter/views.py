from noter import app, g, Entry
from flask import url_for, redirect, request, render_template, \
    abort, flash, session
from markdown2 import Markdown

@app.route('/')
def show_entries():
    entries = Entry.query.order_by(Entry.id)
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_entry(id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from entries where id=?',['id'])
    return show_entries();

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_entry(id):
    return show_entries();

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form['username'] != app.config['USERNAME']) or \
           (request.form['password'] != app.config['PASSWORD']):
            error = 'Invalid info'
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
