import re
import json

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for)
from flask.ext.login import current_user
from flask.ext.security import login_required

notesapp = Blueprint('notesapp', __name__, template_folder='templates')

@notesapp.route('/notesapp')
@login_required
def view():
  return render_template('notesapp/index.html')

@notesapp.route('/notesapp/1')
@login_required
def view1():
  with open('application/data/notes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/view.html', notes=notes)

@notesapp.route('/notesapp/2')
@login_required
def view2():
  with open('application/data/notes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/view2.html', notes=notes)

@notesapp.route('/notesapp/3')
@login_required
def view3():
  with open('application/data/notes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/view3.html', notes=notes)

@notesapp.route('/notesapp/4')
@login_required
def view4():
  with open('application/data/notes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/view4.html', notes=notes)

@notesapp.route('/notesapp/profile')
@login_required
def profile():
  return render_template('notesapp/profile.html')