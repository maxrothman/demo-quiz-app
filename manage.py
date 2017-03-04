#!/usr/bin/env python

from flask_script import Manager
from main import app, db, parse_data, QuestionModel, json2db

manager = Manager(app)

@manager.command
def init_db():
  db.create_all()

@manager.command
def import_data(data_file):
  counter = 0
  with open(data_file) as f:
    for row in parse_data(f):
      question = QuestionModel(**json2db(row))
      db.session.add(question)
      db.session.commit()
      counter += 1

  print('{} committed'.format(counter))

if __name__ == '__main__':
  manager.run()