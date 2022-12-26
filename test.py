import os
import unittest
from datetime import datetime, timedelta

from app import app, db
from app.models import md5
from app.models import User, Post
from config import basedir


class UserModelTest(unittest.TestCase):
    """
    Test User Model Class
    """
    def setUp(self):
        """
        Configure app context and create a new database for each test
        """
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """
        Drop database tables and clear app_context
        """
        print(app.config['SQLALCHEMY_DATABASE_URI'])
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """
        Test password hash function
        """
        user = User(username='mendy', email='mendy@gmail.com')
        user.set_password('mendy')
        db.session.add(user)
        db.session.commit()
        self.assertFalse(user.check_password('slam'))
        self.assertTrue(user.check_password('mendy'))

    def test_user_avatar(self):
        """
        Test user avatar
        """
        user = User(username='mendy', email='mendy@gmail.com')
        db.session.add(user)
        db.session.commit()
        avatarhash = md5(user.email.lower().encode('utf-8')).hexdigest()
        self.assertEqual(user.avatar(120), 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(avatarhash, 120))

    def test_follows(self):
        """
        Test follow, unfollow and is_following feature
        """
        user1 = User(username='user1', email='user1@gmail.com')
        user2 = User(username='user2', email='user2@gmail.com')
        db.session.add_all([user1, user2])
        db.session.commit()

        # test followed and followers
        self.assertEqual(user1.followed.all(), [])
        self.assertEqual(user1.followers.all(), [])

        #test is_following()
        self.assertEqual(user1.following(user2), False)

        #test follow(user)
        user1.follow(user2)
        db.session.commit()
        self.assertTrue(user1.following(user2))
        self.assertEqual(user1.followed.count(), 1)
        self.assertEqual(user1.followed.first().username, 'user2')
        self.assertEqual(user2.followers.count(), 1)
        self.assertEqual(user2.followers.first().username, 'user1')

        # test unfollow(user)
        user1.unfollow(user2)
        db.session.commit()
        self.assertFalse(user1.following(user2))
        self.assertEqual(user1.followed.count(), 0)
        self.assertEqual(user2.followers.count(), 0)

    def test_followed_posts(self):
        """
        Test posts displayed to a user with followers
        """
        user1 = User(username='user1', email='user1@gmail.com')
        user2 = User(username='user2', email='user2@gmail.com')
        user3 = User(username='user3', email='user3@gmail.com')
        user4 = User(username='user4', email='user4@gmail.com')
        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()

        now = datetime.utcnow()
        post1 = Post(body='Post from user1', timestamp = now + timedelta(seconds=1), user_id=user1.id)
        post2 = Post(body='Post from user2', timestamp = now + timedelta(seconds=6), user_id=user2.id)
        post3 = Post(body='Post from user3', timestamp = now + timedelta(seconds=4), user_id=user3.id)
        post4 = Post(body='Post from user4', timestamp = now + timedelta(seconds=9), user_id=user4.id)
        db.session.add_all([post1, post2, post3, post4])
        db.session.commit()

        user1.follow(user2)
        user1.follow(user3)
        user2.follow(user3)
        user3.follow(user4)
        db.session.commit()

        self.assertEqual(user1.followed_posts().all(), [post2, post3, post1])
        self.assertEqual(user2.followed_posts().all(), [post2, post3])
        self.assertEqual(user3.followed_posts().all(), [post4, post3])
        self.assertEqual(user4.followed_posts().all(), [post4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
