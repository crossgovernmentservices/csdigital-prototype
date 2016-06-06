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

@notesapp.route('/notesapp/search')
@login_required
def search():
  with open('application/data/notes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/search.html', notes=notes)

@notesapp.route('/notesapp/5')
@login_required
def view5():
  with open('application/data/selectednotes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/pins.html', notes=notes)

@notesapp.route('/notesapp/6')
@login_required
def view6():
  with open('application/data/taggednotes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/view6.html', notes=notes)

# Onboarding journey
# ==============================================================
@notesapp.route('/notesapp/onboarding/1')
@login_required
def onboarding1():
  return render_template('notesapp/onboarding/page1.html')

@notesapp.route('/notesapp/onboarding/2')
@login_required
def onboarding2():
  return render_template('notesapp/onboarding/page2.html')

@notesapp.route('/notesapp/onboarding/3')
@login_required
def onboarding3():
  return render_template('notesapp/onboarding/page3.html')

@notesapp.route('/notesapp/onboarding/4')
@login_required
def onboarding4():
  return render_template('notesapp/onboarding/page4.html')

@notesapp.route('/notesapp/onboarding/5')
@login_required
def onboarding5():
  return render_template('notesapp/onboarding/page5.html')

# Search banner design
# ==============================================================
@notesapp.route('/notesapp/searchbanner')
@login_required
def search_banner():
  with open('application/data/smallset.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/searchbanner.html', notes=notes)

# Tagging experiment pages
# ==============================================================

@notesapp.route('/notesapp/tagging')
@login_required
def tagging():
  with open('application/data/selectednotes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/tagging.html', notes=notes)

@notesapp.route('/notesapp/tag', defaults={'tag': None})
@notesapp.route('/notesapp/tag/<tag>')
@login_required
def tagged(tag):
  with open('application/data/DAPnotes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/tagged.html', notes=notes, tag=tag)

@notesapp.route('/notesapp/tags')
@login_required
def tags():
  with open('application/data/selectednotes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/yourtags.html', notes=notes)

@notesapp.route('/notesapp/structuredtags')
@login_required
def tags2():
  with open('application/data/tags.json') as data_file:
    tags = json.load( data_file )
  return render_template('notesapp/structuredtags.html', tags=tags)


# Deleting note example
# ==============================================================
@notesapp.route('/notesapp/deletenote')
@login_required
def delete_note():
  with open('application/data/selectednotes.json') as data_file:
    notes = json.load( data_file )
  return render_template('notesapp/deletenote.html', notes=notes)

# Timeline idea
# ==============================================================
@notesapp.route('/notesapp/timeline')
@login_required
def timeline():
  return render_template('notesapp/timeline.html')

# Account / setting pages
# ==============================================================

@notesapp.route('/notesapp/profile')
@login_required
def profile():
  return render_template('notesapp/profile.html')

@notesapp.route('/notesapp/settings/1')
@login_required
def settings():
  return render_template('notesapp/banner/settings.html')

@notesapp.route('/notesapp/settings/2')
@login_required
def settings2():
  return render_template('notesapp/banner/settings2.html')

@notesapp.route('/notesapp/settings/3')
@login_required
def settings3():
  return render_template('notesapp/banner/settings3.html')

@notesapp.route('/notesapp/email')
@login_required
def email():
  return render_template('notesapp/email.html')
