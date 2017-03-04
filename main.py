from flask import Flask, request
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
import csv
import os.path

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/database.db'.format(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#TODO: TURN OFF
app.config['DEBUG'] = True

########################## HELPERS ##########################
def parse_data(data):
  """
  Given an iterable of CSV data, yields rows in the expected format. The first row
  should be the column names.

  Args:
    data (iterable): data to parse
  Yields: #TODO
  """
  DATA_HEADERS = ['question', 'answer', 'distractors']
  reader = csv.DictReader(data, delimiter='|')
  if reader.fieldnames != DATA_HEADERS:
    raise ValueError("Unexpected headers: expected {}, got {}".format(DATA_HEADERS, reader.fieldnames))

  for row in reader:
    yield {'question': row['question'], 'answer': row['answer'],
      'distractors': [i.strip() for i in row['distractors'].split(',')]}


def json2db(data):
  data['distractors'] = ','.join(data['distractors'])
  return data


def db2json(question):
  return {
    'id': question.id,
    'question': question.question,
    'answer': question.answer,
    'distractors': question.distractors.split(','),
  }


########################## API RESOURCES ##########################
req_parser = reqparse.RequestParser()
req_parser.add_argument('id',          type=int,  location='json')
req_parser.add_argument('question',    type=str,  location='json')
req_parser.add_argument('answer',      type=str,  location='json')
req_parser.add_argument('distractors', type=list, location='json')


class QuestionApi(Resource):
  def get(self, question_id):
    question = QuestionModel.query.get_or_404(question_id)
    return db2json(question)

  def put(self, question_id):
    args = req_parser.parse_args(strict=True)
    QuestionModel.query.get_or_404(question_id)
    QuestionModel.query.filter(QuestionModel.id == question_id).update(json2db(args))
    db.session.commit()
    #TODO: figure out how to get the thing I just committed without fetching it again
    return db2json(QuestionModel.query.get(question_id))


class QuestionListApi(Resource):
  def get(self):
    #TODO
    pass

  def post(self):
    args = req_parser.parse_args()
    question = QuestionModel(**json2db(args))
    db.session.add(question)
    db.session.commit()
    return db2json(question)


api.add_resource(QuestionApi, '/question/<int:question_id>')
api.add_resource(QuestionListApi, '/question')


########################## MODELS ##########################
class QuestionModel(db.Model):
  id          = db.Column(db.Integer, primary_key=True)
  question    = db.Column(db.String(255), unique=True)
  answer      = db.Column(db.String(255))
  distractors = db.Column(db.String(255))

  def get_page(self, page):
    #TODO
    pass