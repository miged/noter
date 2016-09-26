import unittest
import requests
from flask_testing import LiveServerTestCase
from noter import app, db
import noter.views
from noter.models import User, Entry
from copy import deepcopy

url = 'http://localhost:5001'

userdata = {
    'name': 'User123',
    'password': 'P@ssw0rd',
    'confirmPass': 'P@ssw0rd'
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
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user(self):
        response = requests.get(url + '/signup')
        self.assertEqual(response.status_code, 200)

        # Test for successful user signup
        response = requests.post(url + '/signup', data=userdata)
        self.assertEqual(response.status_code, 201)
        newUser = User.query.filter_by(username=userdata['name']).first()
        self.assertEqual(newUser.username, userdata['name'])
        self.assertNotEqual(newUser._password, userdata['password'])

        # Test for unavailable username
        response = requests.post(url + '/signup', data=userdata)
        self.assertNotEqual(response.status_code, 201)

        # Test for invalid password confirmation
        userdata2 = deepcopy(userdata)
        userdata2['name'] = 'User456'
        userdata2['confirmPass'] = 'nopass'
        response = requests.post(url + '/signup', data=userdata2)
        self.assertNotEqual(response.status_code, 201)

        # Test successful login
        response = requests.post(url + '/login', data=userdata)
        self.assertEqual(response.status_code, 200)

        # Test invalid login pass
        userdata3 = deepcopy(userdata)
        userdata3['password'] = 'qwerty'
        response = requests.post(url + '/login', data=userdata3)
        self.assertEqual(response.status_code, 400)


    def test_entry(self):
        entrydata = {
            'title': 'Post Title',
            'body': 'Lorem ipsum dolor sit amet'
        }
        session = requests.Session()
        session.post(url + '/signup', data=userdata)
        user = User.query.filter_by(username=userdata['name']).first()

        # Add
        # Test successful added entry
        response = session.post(url + '/add', data=entrydata)
        self.assertEqual(response.status_code, 201)

        entry = Entry.query.filter_by(id=1).first()
        self.assertEqual(entry.title, entrydata['title'])
        self.assertEqual(entry.body, entrydata['body'])
        self.assertEqual(entry.user_id, user.id)

        # Test adding entry without signing in
        response = requests.post(url + '/add', data=entrydata)
        self.assertEqual(response.status_code, 403)

        # Edit
        # Test successful edited entry
        entrydata['title'] = 'Edited title'
        entrydata['body'] = 'Edited body'
        response = session.post(url + '/edit/' + str(entry.id), data=entrydata)
        db.session.commit()
        self.assertEqual(response.status_code, 200)

        entry = Entry.query.filter_by(id=entry.id).first()
        self.assertEqual(entry.title, entrydata['title'])
        self.assertEqual(entry.body, entrydata['body'])

        # Test edit entry without correct user credentials
        response = requests.get(url + '/edit/' + str(entry.id))
        self.assertEqual(response.status_code, 403)
        response = requests.post(url + '/edit/' + str(entry.id), data=entrydata)
        self.assertEqual(response.status_code, 403)

        # Delete
        # Test deleting entry without correct user credentials
        response = requests.get(url + '/delete/' + str(entry.id))
        self.assertEqual(response.status_code, 403)
        response = requests.post(url + '/delete/' + str(entry.id))
        self.assertEqual(response.status_code, 403)

        # Test successful entry delete
        response = session.get(url + '/delete/' + str(entry.id))
        self.assertEqual(response.status_code, 200)
        response = session.post(url + '/delete/' + str(entry.id))
        self.assertEqual(response.status_code, 200)
        entry = Entry.query.filter_by(id=entry.id).first()
        self.assertTrue(entry is None)


if __name__ == '__main__':
    unittest.main()
