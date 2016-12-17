from flask import url_for, abort, session, request
from noter import app, db, bcrypt
from models import Entry, User
from markdown2 import Markdown

def EntryGetById(entryid):
    entry = Entry.query.filter_by(id=entryid).first()
    return entry

def EntryGetByUserId(userid):
    entries = Entry.query.filter_by(user_id=userid).order_by(Entry.id)
    return EntryRender(entries)

def EntryAdd(title, body, userid):
    new_entry = Entry(title, body, userid)
    db.session.add(new_entry)
    db.session.commit()

def EntryEdit(entryid, title, body):
    entry = Entry.query.filter_by(id=entryid).first()
    if not session.get('logged_in') or session['user_id'] != entry.user_id:
        abort(404)

    entry.title = title
    entry.body = body
    db.session.commit()

def EntryDelete(entryid):
    entry = Entry.query.filter_by(id=entryid).first()
    if not session.get('logged_in') or session['user_id'] != entry.user_id:
        abort(404)

    db.session.delete(entry)
    db.session.commit()

def EntryRender(entries):
    try:
        for entry in entries:
            entry.body = Markdown().convert(entry.body)
    except TypeError:
        entries.body = Markdown().convert(entries.body)

    return entries
