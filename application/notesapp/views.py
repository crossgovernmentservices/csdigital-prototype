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
  with open('application/data/notes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/view.html', notes=notes)
