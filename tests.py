import unittest
import requests
from flask_testing import LiveServerTestCase
from noter import app, db
import noter.views
from noter.models import User, Entry
from copy import deepcopy

url = 'http://localhost:5001'

userdata = { 'name': 'User123',
    'password': 'P@ssw0rd',
    'confirmPass': 'P@ssw0rd'
}

entrydata = {
    'title': 'Post Title',
    'body': 'Lorem ipsum dolor sit amet'
}

class ModelTest(LiveServerTestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/unittest.db'
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 5001
        app.config['LIVESERVER_TIMEOUT'] = 10
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_server_is_up(self):
        res = requests.get(url)
        self.assertEqual(res.status_code, 200)

    def test_user(self):
        res = requests.get(url + '/signup')
        self.assertEqual(res.status_code, 200)

        # Test for successful user signup
        res = requests.post(url + '/signup', data=userdata)
        self.assertEqual(res.status_code, 201)
        newUser = User.query.filter_by(username=userdata['name']).first()
        self.assertEqual(newUser.username, userdata['name'])
        self.assertNotEqual(newUser._password, userdata['password'])

        # Test for unavailable username
        res = requests.post(url + '/signup', data=userdata)
        self.assertNotEqual(res.status_code, 201)

        # Test for invalid password confirmation
        userdata2 = deepcopy(userdata)
        userdata2['name'] = 'User456'
        userdata2['confirmPass'] = 'nopass'
        res = requests.post(url + '/signup', data=userdata2)
        self.assertNotEqual(res.status_code, 201)

        # Test successful login
        res = requests.post(url + '/login', data=userdata)
        self.assertEqual(res.status_code, 200)

        # Test invalid login pass
        userdata3 = deepcopy(userdata)
        userdata3['password'] = 'qwerty'
        res = requests.post(url + '/login', data=userdata3)
        self.assertEqual(res.status_code, 400)


    def test_entry(self):
        session = requests.Session()
        session.post(url + '/signup', data=userdata)
        user = User.query.filter_by(username=userdata['name']).first()

        # Test successful added entry
        res = session.post(url + '/add', data=entrydata)
        self.assertEqual(res.status_code, 201)

        entry = Entry.query.filter_by(id=1).first()
        self.assertEqual(entry.title, entrydata['title'])
        self.assertEqual(entry.body, entrydata['body'])
        self.assertEqual(entry.user_id, user.id)

        # Test adding entry without signing in
        res = requests.post(url + '/add', data=entrydata)
        self.assertEqual(res.status_code, 403)

        # Edit
        # Test successful edited entry
        entrydata['title'] = 'Edited title'
        entrydata['body'] = 'Edited body'
        res = session.post(url + '/edit/' + str(entry.id), data=entrydata)
        db.session.commit()
        self.assertEqual(res.status_code, 200)

        entry = Entry.query.filter_by(id=entry.id).first()
        self.assertEqual(entry.title, entrydata['title'])
        self.assertEqual(entry.body, entrydata['body'])

        # Test edit entry without correct user credentials
        res = requests.get(url + '/edit/' + str(entry.id))
        self.assertEqual(res.status_code, 403)
        res = requests.post(url + '/edit/' + str(entry.id), data=entrydata)
        self.assertEqual(res.status_code, 403)

        # Delete
        # Test deleting entry without correct user credentials
        res = requests.get(url + '/delete/' + str(entry.id))
        self.assertEqual(res.status_code, 403)
        res = requests.post(url + '/delete/' + str(entry.id))
        self.assertEqual(res.status_code, 403)

        # Test successful entry delete
        res = session.get(url + '/delete/' + str(entry.id))
        self.assertEqual(res.status_code, 200)
        res = session.post(url + '/delete/' + str(entry.id))
        self.assertEqual(res.status_code, 200)
        entry = Entry.query.filter_by(id=entry.id).first()
        self.assertTrue(entry is None)


if __name__ == '__main__':
    unittest.main()
