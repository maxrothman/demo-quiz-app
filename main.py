from flask import Flask, request, abort
from flask_restful import Api, Resource
from flask_sqlalchemy import SqlAlchemy
import csv
import os.path

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/database.db'.format(os.path.dirname(__file__))
db = SqlAlchemy(app)


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


def validate(data):
  if (not data or
      {k: type(v) for k,v in data.items()} != {'id': int, 'question': str, 'answer': str, 'distractors': str}
    ):
    abort(400)


def json2db(data):
  data['distractors'] = ','.join(data['distractors'])


def db2json(question):
  return {
    'id': question.id,
    'question': question.question,
    'answer': question.answer,
    'distractors': question.distractors.split(','),
  }


class QuestionApi(Resource):
  def get(self, question_id):
    question = QuestionModel.query.get_or_404(question_id)
    return db2json(question)

  def put(self, question_id):
    data = request.get_json()
    validate(data)
    QuestionModel.query.get_or_404(question_id).update(json2db(data)).commit()


class QuestionListApi(Resource):
  def get(self):
    pass

  def post(self):
    data = request.get_json()
    validate(data)
    question = QuestionModel(**json2db(data))
    db.session.add(question)
    db.session.commit()
    


class QuestionModel(db.Model):
  id          = db.Column(db.Integer, primary_key=True)
  question    = db.Column(db.String(255), unique=True)
  answer      = db.Column(db.String(255))
  distractors = db.Column(db.String(255))

  def get_page(self, page):
    pass