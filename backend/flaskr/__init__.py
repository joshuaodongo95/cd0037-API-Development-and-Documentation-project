import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1 , type = int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app,resources={r"/api/*": {"origins": "*"}})
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,True")
        response.headers.add("Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS")
        return response
    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    # Get all categories endpoint
    @app.route('/categories')
    @cross_origin()
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        return jsonify({
                        'success':True,
                        'categories':formatted_categories        
                        })
        
    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        categories = Category.query.all()

        current_questions = paginate_questions(request, selection)
        formatted_categories = {category.id: category.type for category in categories}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
                            'success':True,
                            'questions':current_questions,
                            'total_questions':len(Question.query.all()),
                            'current_category':'',
                            'categories':formatted_categories
                        })
    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    # Delete Question End Point
    @app.route("/questions/<int:question_id>", methods = ["DELETE"])
    def delete_question(question_id):
        try:
            # Select question to be deleted with id or return none
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            
            # delete selected question    
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                            'success':True,
                            'deleted':question_id,
                            'questions':current_questions,
                            'total_questions':len(Question.query.all())
                        })
        except:
            abort(404)
    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer   = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        
        try:
            question = Question(question = new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
            
            if "difficulty" in body:
                    question.difficulty = int(body.get("difficulty"))
                    question.insert()
                
            selection = Question.query.order_by(Question.id).all()
            categories = Category.query.all()
            current_questions = paginate_questions(request, selection)
            formatted_categories = {category.id: category.type for category in categories}

            return jsonify({
                            'success':True,
                            'questions':current_questions,
                            'total_questions':len(Question.query.all()),
                            'current_category':'',
                            'categories':formatted_categories
                        })
        except:
            abort(422)
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions',methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get("search",None)
        try:
            if search:

                selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search)))

                categories = Category.query.all()
                current_questions = paginate_questions(request, selection)
                formatted_categories = {category.id: category.type for category in categories}

                return jsonify({
                                'success':True,
                                'questions':current_questions,
                                'total_questions':len(Question.query.all()),
                                'current_category':'',
                                'categories':formatted_categories
                            })
        except:
            print(sys.exc_info)
            abort(404)
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        
        selection = Question.query.filter(Question.category == category_id).all()
        categories = Category.query.all()
        current_questions = paginate_questions(request, selection)
        formatted_categories = {category.id: category.type for category in categories}

        return jsonify({
                        'success':True,
                        'questions':current_questions,
                        'total_questions':len(selection),
                        'current_category':'',
                        'categories':formatted_categories
                        })
    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes',methods=['POST'])
    def play_quiz():
    
        #get the request body
        body = request.get_json()
        previous_questions = body.get("previous_questions",None)
        category = body.get("quiz_category",None)
        
        print("Previous Questions are : " + str(previous_questions))
        print("Selected Category is : " + str(category['id']))

        previous_questions_list =[]
        try:
            if category['id']==0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
                next_question = random.choice(questions).format()

                next_question_id = next_question['id']
                previous_questions_list.append(next_question_id)
                print(previous_questions_list)
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).filter(Question.category==category['id']).all()
                next_question = random.choice(questions).format()
                next_question_id = next_question['id']
                previous_questions_list.append(next_question_id)
                print(previous_questions_list)
                
            return jsonify({
                             'success':True,
                             'question':next_question
                         })
        except:
            return jsonify({
                'success':True
            }) 
            abort(422) 
    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False, "error": 405, "message": "method not allowed"}), 405

    return app

