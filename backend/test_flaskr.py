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

        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres", "abc", "localhost:5432", self.database_name)
    
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Which country is the fifa 2022 world cup host?","answer":"Qatar","category":6,"difficulty":3}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    # Test for get paginated questions
    def test_get_paginated_questions(self):
        
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["current_category"])
        self.assertTrue(data["categories"])

    # Test for request beyond valid pages

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # Test for get all categories
    def test_get_categories(self):
         res  =  self.client().get("/categories")
         data = json.loads(res.data)

         self.assertEqual(res.status_code,200)
         self.assertEqual(data["success"],True)
         self.assertTrue(data["categories"])
    
    # Test delete question

    def test_delete_question(self):
        res =self.client().delete("/questions/2")
        data =  json.loads(res.data)

        question = Question.query.filter(Question.id==2).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertEqual(data["deleted"],2)
        self.assertEqual(data['total_questions'])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)

    # Test if question exists

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("books/1000")
        data =json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    # Test Create question
    def test_create_question(self):
        res = self.client().post("/questions",json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["questions"]))

    # Test question book creation not allowed
    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/35",json=self.new_question)
        data =json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"],"Method not allowed")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()