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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'postgres', '1234', 'localhost:5432',
            self.database_name)
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

    """TO_DO
    Write at least one test for each test for
    successful operation and for expected errors.
    """
    # test get all categories sucess
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['all_categories'])

    # test if method not allowed 405 in /categories
    def test_405_Not_allowed_method_post_category(self):
        res = self.client().patch('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['Msg'], 'Method Not Allowed')

    # test getting peganition questions success
    def test_get_peginant_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # test error not found 404 in pagination question
    def test_404_sent_request_not_valid_page_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['Msg'], 'Resource Not Found')

    # test success deleting existing question
    def test_delete_question(self):
        res = self.client().delete('/questions/16')
        data = json.loads(res.data)
        question = Question.query.get(16)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], 16)
        self.assertTrue(data['Questions'])
        self.assertTrue(data['total_Questions'])
        self.assertEqual(question, None)

    # test error not found 404 deleting non exist question
    def test_404_delete_question_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['Msg'], 'Resource Not Found')

    # test success creating new question with full data
    def test_create_new_question(self):
        new_question = {
            'question': 'When you gradute from college?',
            'answer': 'from 2016',
            'Category': 5,
            'difficulty': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['Questions'])
        self.assertTrue(data['total_questions'])

    # test error creating new question with data missing
    # error bad request 400
    def test_bad_request_create_new_question(self):
        new_question = {
            'Category': 5,
            'difficulty': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['Msg'], 'Bad Request')

    # test success getting questions according search
    # with result
    def test_question_search_with_result(self):
        res = self.client().post(
            '/questions/search', json={'searchTerm': 'what'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    # test error not found question search with no result
    def test_get_question_search_with_no_result(self):
        res = self.client().post(
            '/questions/search', json={'searchTerm': 'zamzamzam'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['Msg'], 'Resource Not Found')

    # test success geting questions of chosen category
    def test_get_Questions_of_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'], 1)

    # test error not found getting questions of non exist category
    def test_404_get_Questions_of_non_exist_category(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['Msg'], 'Resource Not Found')

    # test success quiz game with no missing data in request
    def test_start_quiz_game(self):
        res = self.client().post(
            '/quizzes',
            json={
                'previous_questions': [],
                'quiz_category': {'id': '6', 'type': 'Sports'}
                })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # test error bad request quiz game with missing data in request
    def test_Bad_request_start_quiz_game(self):
        res = self.client().post(
            '/quizzes', json={'previous_questions': []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['Msg'], 'Bad Request')
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
