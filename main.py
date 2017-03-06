from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
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
  Yields: dict of the form {'question': str, 'answer': str, 'distractors': list}
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
json_parser = reqparse.RequestParser(bundle_errors=True)
json_parser.add_argument('id',          type=int,  location='json', required=True)
json_parser.add_argument('question',    type=str,  location='json', required=True)
json_parser.add_argument('answer',      type=str,  location='json', required=True)
json_parser.add_argument('distractors', type=list, location='json', required=True)


class QuestionApi(Resource):
  def get(self, question_id):
    question = QuestionModel.query.get_or_404(question_id)
    return db2json(question)

  def put(self, question_id):
    args = json_parser.parse_args(strict=True)
    QuestionModel.query.get_or_404(question_id)
    QuestionModel.query.filter(QuestionModel.id == question_id).update(json2db(args))
    db.session.commit()
    #TODO: figure out how to get the thing I just committed without fetching it again
    return db2json(QuestionModel.query.get(question_id))


QUESTIONS_PER_PAGE = 10
qlist_parser = reqparse.RequestParser(bundle_errors=True)
qlist_parser.add_argument('page', type=int, location='args')
qlist_parser.add_argument('sort', type=str, location='args',
  choices=[mod+field for mod in ('', '-') for field in ('id', 'question', 'answer', 'distractors')])

#Duplicated because you shouldn't send id with post
#TODO: deduplicate
post_parser = reqparse.RequestParser(bundle_errors=True)
post_parser.add_argument('question',    type=str,  location='json', required=True)
post_parser.add_argument('answer',      type=str,  location='json', required=True)
post_parser.add_argument('distractors', type=list, location='json', required=True)

class QuestionListApi(Resource):
  def get(self):
    print('started')
    args = qlist_parser.parse_args(strict=True)
    if args['page'] is not None and args['page'] < 1:
      abort(400, message='"page" query param must be >= 1')

    q = QuestionModel.query
    if args['sort']:
      if args['sort'].startswith('-'):
        q = q.order_by(getattr(QuestionModel, args['sort'][1:]).desc())
      else:
        q = q.order_by(getattr(QuestionModel, args['sort']))

    p = q.paginate(args['page'] if args['page'] is not None else 1, QUESTIONS_PER_PAGE, False)
    if args['sort']:
      next_page = api.url_for(QuestionListApi, sort=args['sort'], page=p.next_num) if p.has_next else None
      prev_page = api.url_for(QuestionListApi, sort=args['sort'], page=p.prev_num) if p.has_prev else None
    else:
      next_page = api.url_for(QuestionListApi, page=p.next_num) if p.has_next else None
      prev_page = api.url_for(QuestionListApi, page=p.prev_num) if p.has_prev else None

    return {
      'meta': {
        'next_page': next_page,
        'prev_page': prev_page,
      },
      'questions': [db2json(i) for i in p.items],
    }

  def post(self):
    args = post_parser.parse_args(strict=True)
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
