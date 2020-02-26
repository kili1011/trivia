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

        # JSON Data
        self.new_question = {
            'question': 'This is a test question',
            'answer': 'This is a test answer',
            'category': 1,
            'difficulty': 5
        }
        self.start_quizz = {
            'previous_questions': [],
            'quiz_category': {
                'id': '1',
                'type': 'Science'
            }
        }
        self.continue_quizz = {
            'previous_questions': [20],
            'quiz_category': {
                'id': '1',
                'type': 'Science'
            }
        }        
        self.end_quizz = {
            'previous_questions': [20, 24],
            'quiz_category': {
                'id': '1',
                'type': 'Science'
            }
        }

        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    """ Test
    ROUTE: ('/categories')
    METHODs: GET
    """
    # GET
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])


    """ Test
    ROUTE: ('/questions')
    METHODS: GET, POST 
    """
    # GET
    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        
    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions_per_page'], 10)
        self.assertEqual(data['page'], 1)

    def test_get_second_page_with_questions(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['page'], 2)
    
    # POST
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    """ Test
    ROUTE: ('/questions/<int:question_id>')
    METHODS: GET, DELETE
    """
    # GET
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

    # DELETE 
    def test_delete_question(self):
        res = self.client().delete('/questions/19')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 19).one_or_none()
        self.assertEqual(res.status_code, 200)  


    """ Test
    ROUTE: ('/quizzes')
    METHODS: POST
    """
    # POST
    def test_start_quizz(self):
        res = self.client().post('/quizzes', json=self.start_quizz)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_next_question(self):
        res = self.client().post('/quizzes', json=self.continue_quizz)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_finish_quiz(self):
        res = self.client().post('/quizzes', json=self.end_quizz)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()


