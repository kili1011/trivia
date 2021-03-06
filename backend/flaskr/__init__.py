import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


''' Paginates the questions in the view
INPUT: Request and selection of questions from the db
OUTPUT: A list of paginates questions per page
'''
def paginated_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # ----------------------------------------------------------- #
    # Config.
    # ----------------------------------------------------------- #
    app = Flask(__name__)
    CORS(app)
    setup_db(app)

    '''
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # ----------------------------------------------------------- #
    # Controllers.
    # ----------------------------------------------------------- #
    '''
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def all_categories():
        query = Category.query.order_by(Category.id).all()
        if len(query) == 0:
            abort(422)
        else:
            response = {}
            for index in range(len(query)):
                category = query[index].type
                key = index + 1
                response[key] = category
            
        return jsonify({
            'success': True,
            'categories': response})

    '''
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def category_by_id(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()
        
        if category is None:
            abort(422)
        else:
            questions_with_id = Question.query.filter(Question.category == category.id).all()
            formatted_questions_with_id = paginated_questions(request, questions_with_id)

        return jsonify({
            'success': True, 
            'questions': formatted_questions_with_id,
            'total_questions': len(questions_with_id),
            'questions_per_page': len(formatted_questions_with_id),
            'current_category': category.type,
            'current_category_id': category.id})


    @app.route('/questions', methods=['GET', 'POST'])
    def all_questions():
        error = False
        try:
            '''
            Create an endpoint to handle GET requests for questions, 
            including pagination (every 10 questions). 
            This endpoint should return a list of questions, 
            number of total questions, current category, categories. 

            TEST: At this point, when you start the application
            you should see questions and categories generated,
            ten questions per page and pagination at the bottom of the screen for three pages.
            Clicking on the page numbers should update the questions. 
            '''
            if request.method == 'GET':
                # Get categories and format them as dictionary
                all_categories = Category.query.order_by(Category.id).all()
                formatted_categories = {}
                for index in range(len(all_categories)):
                    category = all_categories[index].type
                    key = index + 1
                    formatted_categories[key] = category
                # Check request parameters
                param = request.args.get('page', None, type=int)
                if param is None:
                    all_questions = Question.query.order_by(Question.id).all()
                    formatted_questions = [question.format() for question in all_questions]
                    response = {
                        'success': True,
                        'questions': formatted_questions,
                        'total_questions': len(all_questions),
                        'categories': formatted_categories,
                        'current_category': 0}
                else:
                    all_questions = Question.query.order_by(Question.id).all()    
                    page = request.args.get('page', 1, type=int)
                    formatted_questions = paginated_questions(request, all_questions)                    
                    response = {
                        'success': True,
                        'questions': formatted_questions,
                        'total_questions': len(all_questions),
                        'questions_per_page': len(formatted_questions),
                        'categories': formatted_categories,
                        'current_category': 0,
                        'page': page}

            if request.method == 'POST':
                body = request.get_json()
                if 'searchTerm' in body:
                    '''
                    Create a POST endpoint to get questions based on a search term. 
                    It should return any questions for whom the search term 
                    is a substring of the question. 

                    TEST: Search by any phrase. The questions list will update to include 
                    only question that include that string within their question. 
                    Try using the word "title" to start. 
                    '''
                    query = Question.query.filter(Question.question.ilike('%' + 
                        body['searchTerm'] + '%'))
                    if query.count() == 0:
                        response = {
                            'success': False,
                            'total_questions': 0}
                    else:
                        questions_from_search = query.all()
                        formatted_questions = [question.format() for question in questions_from_search]
                        response = {
                            'success': True,
                            'questions': formatted_questions,
                            'total_questions': len(questions_from_search)
                        }
                else:
                    '''
                    Create an endpoint to POST a new question, 
                    which will require the question and answer text, 
                    category, and difficulty score.

                    TEST: When you submit a question on the "Add" tab, 
                    the form will clear and the question will appear at the end of the last page
                    of the questions list in the "List" tab.  
                    '''
                    new_question = Question(
                        body['question'],   
                        body['answer'],
                        body['category'],
                        body['difficulty'])
                    new_question.insert()
                    db.session.close()
                    response = {
                        'success': True,
                    }
        except: 
            error = True
        if error:
            print(sys.exc_info())
            abort(422)
        else:
            return jsonify(response)

    '''
    Create an endpoint to DELETE question using a question ID.
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['GET', 'DELETE'])
    def question_with_id(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(422)
        else:
            if request.method == 'GET':
                formatted_question = question.format()
                response = {
                    'success': True,
                    'question': formatted_question}

            if request.method == 'DELETE':
                question.delete()
                response = { 
                    'success': True,
                }
            return jsonify(response)

    '''
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        previous_questions = body['previous_questions']
        category = body['quiz_category']
        questions = Question.query.filter(Question.category == category['id'])
        if len(previous_questions) == questions.count():
            response = {
                "sucess": True,
                "question": False
            }
        else:
            index = True
            while index:
                question_generator = random.choice(questions.all())
                if  question_generator.id not in previous_questions:
                    next_question = question_generator.format()
                    index = False 
            response = {
                "success": True,
                "question": next_question
            }
        return jsonify(response)


    # ----------------------------------------------------------- #
    # Error Handlers.
    # ----------------------------------------------------------- #
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Method not allowed"
            }), 405

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Unprocessable"
            }), 422

  
    return app

    