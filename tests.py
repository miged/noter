import unittest
import requests
from flask_testing import LiveServerTestCase
from noter import app, db
import noter.views
from noter.models import User, Entry

url = 'http://localhost:5001'


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

    def test_signup_user(self):
        userdata = {
            'name': 'User123',
            'password': 'P@ssw0rd',
            'confirmPass': 'P@ssw0rd'
        }
        response = requests.get(url + '/signup')
        self.assertEqual(response.status_code, 200)

        # Test for signing up a user
        response = requests.post(url + '/signup', data=userdata)
        self.assertEqual(response.status_code, 201)
        newUser = User.query.filter_by(username=userdata['name']).first()
        self.assertEqual(newUser.username, userdata['name'])
        self.assertNotEqual(newUser._password, userdata['password'])

        # Test for unavailable username
        response = requests.post(url + '/signup', data=userdata)
        self.assertNotEqual(response.status_code, 201)

        # Test for invalid password confirmation
        userdata['confirmPass'] = 'nopass'
        response = requests.post(url + '/signup', data=userdata)
        self.assertNotEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
