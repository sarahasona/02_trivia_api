import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import Question, Category, setup_db
import random
import secrets
from models import setup_db, Question, Category
QUESTIONS_PER_PAGE = 10


def peginante_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formated_questions = [question.format() for question in selection]
    current_questions = formated_questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    @TO_DO: Set up CORS. Allow '*'
    for origins. Delete the sample route after completing the TO_DOs
    '''
    CORS(app, resources={"/": {'origins': ['http://localhost:3000/', '*']}})
    '''@TO_DO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-headers', 'Content_Type,Authentication')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
        response.headers.add(
            'Access-Control-Allow-Origin', 'http://localhost:3000/')
        return response
    '''
    @TO_DO: Create an endpoint to handle GET requests
    for all available categories.
    '''
    # get all categories
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)
        cat_obj = {}
        for cat in categories:
            cat_obj.update({cat.id: cat.type})
        formattedCat = [cat.format() for cat in categories]
        return jsonify({
            'success': True,
            'categories': cat_obj,
            'all_categories': len(categories)
            })
    '''@TO_DO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom
    of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    # get all questions in List in a pagenation each 10 question appear in page
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # getting all question
        selection = Question.query.order_by(Question.id).all()
        # pagination questions
        questions = peginante_questions(request, selection)
        if len(questions) == 0:
            abort(404)
        # get all categories as an object have a key of id and value of type
        categories = Category.query.order_by(Category.id).all()
        cat_data = {}
        for cat in categories:
            cat_data.update({cat.id: cat.type})
        return jsonify({
            "success": True,
            "categories": cat_data,
            "current_category": [cat['category'] for cat in questions],
            "questions": questions,
            "total_questions": len(selection)
            })
    '''@TO_DO:
    Create an endpoint to DELETE question using a question ID.
    '''
    # delete chosen question
    @app.route('/questions/<int:ques_id>', methods=['DELETE'])
    def delete_question(ques_id):
        question = Question.query.get(ques_id)
        if question is None:
            abort(404)
        question.delete()
        # get all questions
        selection = Question.query.order_by(Question.id).all()
        # get pagination questions
        current_questions = peginante_questions(request, selection)
        return jsonify({
            'success': True,
            'deleted_id': ques_id,
            'Questions': current_questions,
            'total_Questions': len(selection)
            })
    ''' TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    '''@TO_DO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty .score'''

    # create a new question
    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()
        question = data.get('question', None)
        answer = data.get('answer', None)
        category = data.get('category', None)
        difficulty_score = data.get('difficulty', None)
        # Error if there is missing data
        if (question is None or question == "" 
            and answer is None or answer == ""):
            abort(400)
        # save new question in db
        new_question = Question(
            question=question,
            answer=answer,
            category=category,
            difficulty=difficulty_score)
        new_question.insert()
        # get all questions
        selection = Question.query.order_by(Question.id).all()
        # get pagination question
        current_question = peginante_questions(request, selection)
        return jsonify({
          'success': True,
          'created': new_question.id,
          'Questions': current_question,
          'total_questions': len(selection)
          })

    '''TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at
    the end of the last page
    of the questions list in the "List" tab.
    '''
    '''@TO_DO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.'''
    # get questions according search
    @app.route('/questions/search', methods=['POST'])
    def question_search():
        data = request.get_json()
        search = data.get('searchTerm', None)
        # if there is no search enterd abort error
        if search is None or search == "":
            abort(400)
        # get all question case sensitive according to the search
        get_questions = Question.query.filter(
                        Question.question.ilike(f'%{search}%')).all()
        # if there is no data found abort error Not Found
        if len(get_questions) == 0:
            abort(404)
        # get pagination Questions
        current_questions = peginante_questions(request, get_questions)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(get_questions),
            'current_category': [
                ques['category'] for ques in current_questions]
            })
    ''' TEST: Search by any phrase. The questions list will update
    to include only question that include that string within
    their question. Try using the word "title" to start.
    '''
    '''
    @TO_DO:
    Create a GET endpoint to get questions based on category. '''

    # get questions of specfic category
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def categories_questions(id):
        # get question of chosin category
        questions = Question.query.filter(
                    Question.category == id).order_by(Question.id).all()
        if len(questions) == 0:
            abort(404)
        # get pagination questions
        current_questions = peginante_questions(request, questions)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'current_category': [id]
            })
    '''TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown. '''
    '''@TO_DO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions. '''
    # get questions in the game according to chosen ctegory
    # and sending previous questions in request & category id
    @app.route('/quizzes', methods=['POST'])
    def quiz_game():
        data = request.get_json()
        previous_questions = data.get('previous_questions', None)
        category = data.get('quiz_category', None)
        # if data missing in the request abort error
        if category is None or previous_questions is None:
            abort(400)
        chosen_category = category.get('id')
        questions = []
        # if chosen category id is 0 get all questions
        if chosen_category == 0:
            questions = Question.query.all()
        # else get questions according category id
        else:
            questions = Question.query.filter(
                        Question.category == chosen_category).all()
        # format questions and exclude previous questions
        current_questions = [
            ques.format() for ques in questions
            if ques.id not in previous_questions]
        # return random question
        if len(current_questions) == 0:
            random = ""
        else:
            random = secrets.choice(current_questions)
        return jsonify({
            'success': True,
            'question': random
            })
    '''
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. '''
    '''@TO_DO:
    Create error handlers for all expected errors
    including 404 and 422. '''
    @app.errorhandler(400)
    def Bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'Msg': 'Bad Request'
            }), 400

    @app.errorhandler(404)
    def Not_Found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'Msg': 'Resource Not Found'
            }), 404

    @app.errorhandler(422)
    def Unprocessible(error):
        return jsonify({
            'success': False,
            'error': 422,
            'Msg': 'Unprocessible Entity'
            }), 422

    @app.errorhandler(405)
    def Method_Not_Allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'Msg': 'Method Not Allowed'
            }), 405

    @app.errorhandler(500)
    def Server_Error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'Msg': 'Internal Server Error'
            }), 500
    return app
