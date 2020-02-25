import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_get_question_with_existing_id(self):
        res = self.client().get('/questions/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_if_question_does_not_exist(self):
        res = self.client().get('/questions/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422) 

    def test_delete_question(self):
        res = self.client().delete('/questions/19')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 19).one_or_none()

        self.assertEqual(res.status_code, 200)  




      


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()