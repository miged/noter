from flask import abort, session
from noter import db
from models import Entry, User
from markdown2 import Markdown

def EntryGetById(entryid):
    """Retrieve entry by id"""
    entry = Entry.query.filter_by(id=entryid).first()
    return entry

def EntryGetByUserId(userid):
    """Retrieve entry by user id"""
    entries = Entry.query.filter_by(user_id=userid).order_by(Entry.id)
    return EntryRender(entries)

def EntryAdd(title, body, userid):
    """Create entry"""
    new_entry = Entry(title, body, userid)
    db.session.add(new_entry)
    db.session.commit()

def EntryEdit(entryid, title, body):
    """Update entry"""
    entry = Entry.query.filter_by(id=entryid).first()
    if not session.get('logged_in') or session['user_id'] != entry.user_id:
        abort(404)

    entry.title = title
    entry.body = body
    db.session.commit()

def EntryDelete(entryid):
    """Delete entry"""
    entry = Entry.query.filter_by(id=entryid).first()
    if not session.get('logged_in') or session['user_id'] != entry.user_id:
        abort(404)

    db.session.delete(entry)
    db.session.commit()

def EntryRender(entries):
    """Render entries in Markdown"""
    if isinstance(entries) is list:
        for entry in entries:
            entry.body = Markdown().convert(entry.body)
    else:
        entries.body = Markdown().convert(entries.body)

    return entries
