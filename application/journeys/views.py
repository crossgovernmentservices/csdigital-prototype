from flask import (
    Blueprint,
    render_template
)

import json
import os.path

journeys = Blueprint('journeys', __name__, template_folder='templates')

@journeys.route('/journeys')
def journeys_home():
    return render_template('journeys/home.html')

@journeys.route('/journeys/<journey>')
def journeys_viewer(journey):
    datafile = "application/data/" + journey + ".json"
    if os.path.isfile( datafile ):
      with open( datafile ) as data_file:
            journeys = json.load(data_file)
      return render_template('journeys/viewer.html', journeys=journeys)
    else:
      return render_template("404.html"), 404